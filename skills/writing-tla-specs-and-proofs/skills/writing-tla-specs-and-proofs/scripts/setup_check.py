#!/usr/bin/env python3
"""Check that this machine and this project can run the skill's workflow, before any module is written.

    setup_check.py [--proofs] [--fetch-jar] [--write-pins] [--dir D] [--results-dir R]

Reports, one line each:

  python    3.9 or later (the scripts use the standard library only)
  java      11 or later, which the TLA+ tools need
  project   the spec directory, the project root and the results directory the scripts will use
  checker   tla2tools.jar, where it was found, and whether its sha256 is the pin's
  tlc       the bundled fixture (assets/selftest/Counter.tla) run through its row list in a temp directory: every
            kind of row and every verdict, so a jar whose messages this skill's scripts cannot read is caught here
  prover    tlapm, where it was found, and whether its sha256 is the pin's
  tlapm     the fixture's proof proved, and its flip test failing as required

The prover lines are informational unless --proofs is given: model checking (steps 1 and 2 of the workflow) needs
only java and the jar. Exits non-zero when something a script would refuse is wrong.

--fetch-jar   download the pinned tla2tools.jar into tools/ at the project root when none is found, and refuse it
              if its sha256 is not the pin's. An existing jar is never replaced.
--write-pins  write tools/TLC-PIN (the skill's default pin, or the jar found when it is another build) and
              tools/TLAPS-PIN (the prover found, recorded as observed) where the project has none. An existing pin
              is never rewritten: moving a pin is a deliberate edit, and the record that the tool changed.

tla_common.py says where each thing is looked for and which environment variables override it. tlapm is not
fetched: install a release from https://github.com/tlaplus/tlapm/releases under tools/tlaps-<version>/ (so that
tools/tlaps-<version>/bin/tlapm exists), put it on PATH, or set TLAPM to the binary.
"""
import argparse
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.dont_write_bytecode = True  # leave no __pycache__ in the skill directory
import tla_common as t  # noqa: E402
from flip_test import flip  # noqa: E402

FIXTURE = os.path.join(os.path.dirname(t.HERE), "assets", "selftest")
problems = []


def say(label, status, detail, fatal=True):
    print(f"{label:8} {status:7} {detail}")
    if status == "FAIL" and fatal:
        problems.append(label)


def fetch_jar(layout, checker):
    pin = checker.pin
    url = pin.get("url") or f"https://github.com/tlaplus/tlaplus/releases/download/{pin.get('version')}/tla2tools.jar"
    tools = layout.up("tools") or os.path.join(layout.root, "tools")
    dest = os.path.join(tools, "tla2tools.jar")
    os.makedirs(tools, exist_ok=True)
    part = dest + ".part"
    try:
        try:
            with urllib.request.urlopen(url) as r, open(part, "wb") as f:
                shutil.copyfileobj(r, f)
        except OSError as e:
            if not shutil.which("curl"):
                raise
            print(f"         (python could not fetch it: {e}; trying curl)")
            subprocess.run(["curl", "-sSL", "--fail", "-o", part, url], check=True)
        got = t.sha256(part)
        if got != pin.get("jar_sha256"):
            say("fetch", "FAIL", f"{url} is sha256 {got}, not the {pin.get('jar_sha256')} pinned by {checker.pin_label}; "
                "nothing installed")
            return
        os.replace(part, dest)
        say("fetch", "ok", f"{layout.rel(dest)} from {url}, sha256 as pinned by {checker.pin_label}")
    except (OSError, subprocess.CalledProcessError) as e:
        say("fetch", "FAIL", f"could not download {url}: {e}")
    finally:
        if os.path.exists(part):
            os.remove(part)


def tlc_selftest(checker):
    """Run the fixture's row list in a temp directory. Returns TLC's banner line."""
    tmp = tempfile.mkdtemp(prefix="tla_setup_")
    try:
        for f in os.listdir(FIXTURE):
            shutil.copy(os.path.join(FIXTURE, f), tmp)
        layout = t.Layout(tmp)
        meta, rows = t.parse_rows(os.path.join(tmp, "Counter-rows.txt"))
        bad, banner = [], ""
        for row in rows:
            verdict, states, ok, out = t.run_row(layout, checker, "Counter", meta, row)
            m = re.search(r"^TLC2 Version.*$", out, re.M)
            banner = banner or (m.group(0) if m else "")
            if not ok:
                bad.append((t.format_row(row, verdict, states, ok), out))
        if bad:
            say("tlc", "FAIL", f"{len(bad)} of {len(rows)} fixture rows not as expected; the first:")
            print("         " + bad[0][0])
            print("\n".join("         " + line for line in bad[0][1].rstrip().splitlines()[-12:]))
        else:
            want = checker.pin.get("tlc")
            note = "" if not want or not checker.pinned or want == banner else f" (the pin says {want})"
            say("tlc", "ok", f"{banner or 'TLC'}: all {len(rows)} fixture rows as expected{note}")
        return banner
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def tlapm_selftest(prover, fatal):
    tmp = tempfile.mkdtemp(prefix="tla_setup_")
    try:
        for f in os.listdir(FIXTURE):
            shutil.copy(os.path.join(FIXTURE, f), tmp)
        code, out = t.run_group(t.tlapm_cmd(prover, os.path.join(tmp, "cache")) + ["Counter_proof.tla"], tmp)
        m = re.search(r"All \d+ obligations? proved", out)
        if not (m and code == 0):
            say("tlapm", "FAIL", f"the fixture's proof did not prove (exit {code}):", fatal)
            print("\n".join("         " + line for line in out.rstrip().splitlines()[-12:]))
            return
        ok, line = flip(t.Layout(tmp), prover, "Counter", "M_NOLIMIT")
        if ok:
            say("tlapm", "ok", f"the fixture's proof: {m.group(0)}; with its hypothesis flipped it fails, as required")
        else:
            say("tlapm", "FAIL", f"the fixture's flip test: {line}", fatal)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def backends(prover):
    code, out = t.run_group([prover.path, "--config"], os.getcwd())
    seen = []
    for name, v in re.findall(r'^(\S[^=\n]*) version == "(.*)"$', out, re.M):
        v = re.sub(r"^zenon version (\S+ \S+).*$", r"Zenon \1", v)
        v = re.sub(r"^Z3 version (\S+).*$", r"Z3 \1", v)
        v = name if v == "unknown" else v  # LS4 reports no version
        if v not in seen:
            seen.append(v)
    return "; ".join(seen)


PIN_HEAD = "# One line per field, `key value`. The scripts of the writing-tla-specs-and-proofs skill refuse a tool whose\n" \
           "# sha256 is not the one here unless {env}=1 is set, and print the digest in every results file. Moving this\n" \
           "# pin is the record that the tool changed.\n"


def tools_dir(layout):
    tools = layout.up("tools") or os.path.join(layout.root, "tools")
    os.makedirs(tools, exist_ok=True)
    return tools


def write_tlc_pin(layout, checker, banner):
    path = os.path.join(tools_dir(layout), "TLC-PIN")
    if os.path.exists(path):
        say("pins", "kept", f"{layout.rel(path)} exists; a pin moves by a deliberate edit")
    elif not checker.sha:
        say("pins", "FAIL", "no jar to pin; run with --fetch-jar first")
    else:
        default = t.read_pin(os.path.join(t.HERE, "TLC-PIN"))
        fields = default if checker.sha == default.get("jar_sha256") else \
            {"version": "unknown", "tlc": banner or "unknown", "jar_sha256": checker.sha}
        with open(path, "w", encoding="utf-8") as f:
            f.write("# The model checker every TLC results file cites.\n" + PIN_HEAD.format(env="TLC_UNPINNED"))
            f.write("".join(f"{k} {v}\n" for k, v in fields.items()) + f"pinned {t.today()}\n")
        say("pins", "wrote", f"{layout.rel(path)}: jar sha256 {checker.sha}")
        if "checker" in problems and fields is not default:
            problems.remove("checker")  # the jar found is now the project's pin


def write_tlaps_pin(layout, prover):
    path = os.path.join(tools_dir(layout), "TLAPS-PIN")
    if os.path.exists(path):
        say("pins", "kept", f"{layout.rel(path)} exists; a pin moves by a deliberate edit")
    elif not prover.sha or t.is_script(prover.path):
        say("pins", "skipped", "no tlapm binary to pin")
    else:
        code, out = t.run_group([prover.path, "--version"], os.getcwd())
        version = out.strip().splitlines()[-1] if out.strip() else "unknown"
        with open(path, "w", encoding="utf-8") as f:
            f.write("# The prover every proof results file cites, recorded as observed on this machine: a release tag can be\n"
                    "# rebuilt upstream under the same name, so the digest is the pin and the version is a label.\n"
                    + PIN_HEAD.format(env="TLAPM_UNPINNED"))
            f.write(f"version {version}\nbinary_sha256 {prover.sha}\n"
                    f"platform {platform.machine()}-{platform.system().lower()}\n"
                    f"backends {backends(prover)}\npinned {t.today()}\n")
        say("pins", "wrote", f"{layout.rel(path)}: tlapm {version} sha256 {prover.sha}")
        if not layout.up("tools", f"tlaps-{version}", "bin", "tlapm"):
            print(f"         (the scripts find this binary through TLAPM or PATH, not under tools/tlaps-{version}/)")


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--proofs", action="store_true", help="the prover is required, not informational")
    ap.add_argument("--fetch-jar", action="store_true")
    ap.add_argument("--write-pins", action="store_true")
    ap.add_argument("--dir")
    ap.add_argument("--results-dir")
    a = ap.parse_args(argv)
    v = sys.version_info
    say("python", "ok" if v >= (3, 9) else "FAIL", f"{v.major}.{v.minor}.{v.micro}" + ("" if v >= (3, 9) else " (3.9 or later is needed)"))
    jv = t.java_version()
    if not jv:
        say("java", "FAIL", "not found; the TLA+ tools need Java 11 or later. Install a JDK; this script does not.")
    else:
        say("java", "ok" if jv[0] >= 11 else "FAIL", jv[1] + ("" if jv[0] >= 11 else " (11 or later is needed)"))
    layout = t.Layout(a.dir, a.results_dir)
    say("project", "ok", f"{layout.project}: modules in {layout.rel(layout.spec) if layout.spec != layout.root else '.'}, "
        f"results in {layout.rel(layout.results) if layout.results != layout.root else '.'}, root {layout.root}")

    checker = t.find_checker(layout)
    if not checker.sha and a.fetch_jar:
        fetch_jar(layout, checker)
        checker = t.find_checker(layout)
    banner = ""
    if not checker.sha:
        say("checker", "FAIL", f"no tla2tools.jar ({checker.path or 'no tools/tla2tools.jar at or above the spec directory'}); "
            "run with --fetch-jar, or set TLA_JAR")
    else:
        where = layout.rel(checker.path)
        if checker.pinned:
            say("checker", "ok", f"{where} {checker.pin.get('version', '')} sha256 {checker.sha}, as pinned by {checker.pin_label}")
        else:
            override = bool(os.environ.get("TLC_UNPINNED"))
            say("checker", "WARN" if override else "FAIL",
                f"{where} is sha256 {checker.sha}, not the {checker.want} pinned by {checker.pin_label}"
                + ("; TLC_UNPINNED is set, and results files will say so" if override else
                   "; the scripts refuse it unless TLC_UNPINNED=1"))
        if jv and jv[0] >= 11:
            banner = tlc_selftest(checker)

    if a.write_pins:
        write_tlc_pin(layout, checker, banner)
        write_tlaps_pin(layout, t.find_prover(layout))
    prover = t.find_prover(layout)
    need = a.proofs
    if not prover.sha:
        say("prover", "FAIL" if need else "absent", "no tlapm (TLAPM, tools/tlaps-<version>/bin/tlapm, PATH); needed for "
            "proofs only: https://github.com/tlaplus/tlapm/releases", need)
    elif t.is_script(prover.path):
        say("prover", "FAIL" if need else "WARN", f"{prover.path} is a wrapper script; set TLAPM to the binary so the "
            "digest printed is the prover's", need)
    else:
        if prover.pinned:
            say("prover", "ok", f"{layout.rel(prover.path)} {prover.pin.get('version', '')} sha256 {prover.sha}, "
                f"as pinned by {prover.pin_label}")
        else:
            override = bool(os.environ.get("TLAPM_UNPINNED"))
            why = f"not the {prover.want} pinned by {prover.pin_label}" if prover.pin_label else \
                "and the project has no tools/TLAPS-PIN (--write-pins records this binary)"
            say("prover", "WARN" if override or not need else "FAIL",
                f"{layout.rel(prover.path)} is sha256 {prover.sha}, {why}"
                + ("; TLAPM_UNPINNED is set, and results files will say so" if override else
                   "; the proof scripts refuse it unless TLAPM_UNPINNED=1"), need)
        tlapm_selftest(prover, need)

    if problems:
        print(f"setup: not ready ({', '.join(dict.fromkeys(problems))})")
        return 1
    print("setup: ready for model checking" + (" and proofs" if prover.sha and not t.is_script(prover.path)
                                               and (prover.pinned or os.environ.get("TLAPM_UNPINNED")) else
                                               "; proofs need the prover line above settled"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
