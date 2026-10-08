#!/bin/bash
# The unsound cases of proof-certification.md §8 (ADR-0046 A2, pending), looked for. tlapm 7824dab has two. The binder
# case: it hands SMT, Zenon and Isabelle a term it does not translate (an ENABLED it has not expanded, a \cdot, a
# temporal formula) as a nullary constant, and under a binder that constant drops the variable bound around it. The
# names case: it names each term it abstracts, and each atom it hands LS4, by 20 bits of the MD5 of the term as it
# prints it, does not check that two terms of one obligation get two names, and prints a bound variable as it prints
# a constant of its name, so that a definition expanded at an argument naming one of its bound variables prints, and
# is named, as another term. A backend's input keeps only the name, not what it stood for, so this looks from four
# ends and prints, for a reader to classify:
# 1. Sources: every occurrence, outside comments, of ENABLED, \cdot, [], <>, ~>, WF_, SF_, \EE and \AA in spec/*.tla
#    (the recorded traces, Trace_*.tla, aside), by module and line. An obligation can hold such a term only by stating
#    it or by expanding a definition that does. Three shapes are counted rather than listed: [][A]_v, the box of an
#    action, which specifications are written with; a line stating Spec => []P, P a bare name, with no binder on it;
#    and [] between CASE arms, which is not the temporal operator. Every other line is listed in full. The sources
#    cannot show the binder case tlapm makes by moving a quantifier out of a temporal body; the runs can, for SMT.
# 2. Runs: for each proof module, a certified run made as proof-cert.sh makes it but on one thread, so that each
#    backend is called in the same order every time, with the SMT evidence, every backend's input and tlapm's
#    per-obligation messages kept, and two listings. The SMT queries in which an opaque constant
#    (smt__TLA____Anon__OPAQUE__*) occurs under forall, exists or lambda, by obligation line, with a digest of the query
#    without its location comment. And the obligations Zenon or Isabelle closed, by line, each Zenon proof Isabelle
#    did not accept marked so, by tlapm's trace of Isabelle's check (+k entered, -k left accepted), since tlapm's
#    message names only the first refusal Isabelle prints. Each module's line gives this run's verdict by
#    proof-cert.sh's test, and how many results the run reused. On one thread tlapm reuses every result it can, where proof-cert.sh's threads may send an obligation
#    again, so the two verdicts can differ where a reused result rests on names (proof-certification.md §6, §8).
# 3. Names: every proof module is run again, in the same way, over a copy of spec/*.tla in which every identifier but
#    the keywords, the names the standard modules define, the module names and record fields has a new name of the
#    same length, so that the columns of bulleted /\ and \/ lists, which TLA+ reads, do not move. A term that holds a
#    renamed identifier gets a name of its own in each run. The two runs' inputs to each backend are paired in the
#    order they were made; each pair must have the same shape once identifiers and names are masked, and the same
#    pattern of names; and each obligation must end by the same route. Two terms that share a name by the hash in one
#    run and not in the other show as a difference. Per module: the inputs, those with two or more names, the most in
#    one, and the pairs of names within an input, whose number over 2^20 is how many collisions to expect by accident.
#    A renaming that renames each identifier alike everywhere keeps a capture, so section 4 looks for those.
# 4. Capture: every obligation of each module's run, as tlapm's display printer shows it (--printallobs). That printer
#    renames a bound variable whose scope holds a free name it would capture (k becomes k_1); the print tlapm hashes
#    to name terms does not. So a renamed name x_N whose scope holds x is a term the hashed print shows as another, a
#    capture, whatever the source wrote: an expansion, a TAKE or a WITNESS. And each proof module must parse under
#    SANY, which refuses the shadowing tlapm accepts.
#   usage: proof-scan.sh [<Module>_proof ...] > proof-scan-results-<date>.txt     (from spec/; default: every *_proof.tla)
# Needs what proof-cert.sh needs. STRETCH= multiplies the backend timeouts, as there (default 1; the records of
# RulesFloorNV_rev5, Confinement and Confinement_A1 ran at 10). Exits non-zero if a named module does not exist, a
# module's run produced no obligations, its renamed run differs, an obligation holds a capture, or a module does not
# parse under SANY; a run that does not certify is reported, and is not a failure of the scan.
set -u
here=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$here/.." && pwd)
cd "$here" || exit 2
tlapm="$root/tools/tlapm"
export TOPAK_CVC5=${CVC5:-$root/tools/cvc5-macOS-arm64-static/bin/cvc5}
export TOPAK_ETHOS=${ETHOS:-$root/tools/ethos-8dc85c4/bin/ethos}
export TOPAK_CPC=${TOPAK_CPC:-$root/tools/cpc}
for x in "$TOPAK_CVC5" "$TOPAK_ETHOS"; do [ -x "$x" ] || { echo "missing $x" >&2; exit 2; }; done
if [ $# -gt 0 ]; then mods="$*"; else mods=$(ls *_proof.tla | sed 's/\.tla$//' | LC_ALL=C sort); fi
cfg=$("$tlapm" --config 2>/dev/null)
bin=$(echo "$cfg" | sed -n 's/^tlapm_executable == "\(.*\)"$/\1/p')
lib=$(echo "$cfg" | sed -n 's/^library_path == "\(.*\)"$/\1/p')
jar="$root/tools/tla2tools.jar"
d16() { shasum -a 256 "$1" | cut -c1-16; }
tmp=$(mktemp -d "${TMPDIR:-/tmp}/topak-scan.XXXXXX") || exit 2
trap 'rm -rf "$tmp"' EXIT
echo "TOPAK — the prover's unsound cases (proof-certification.md §8) looked for: the untranslated operators in spec/*.tla; in each proof module's certified run, the queries that hold an opaque constant under a binder and the obligations Zenon or Isabelle closed; the names the run gives abstracted terms, against a run over renamed sources; and, in the obligations as tlapm prints them, the bound variables that capture a name"
echo "Runner: proof-scan.sh (sha256 $(d16 "$here/proof-scan.sh")) · tlapm $("$tlapm" --version) (binary sha256 $(d16 "$bin")) · smt-checked (sha256 $(d16 "$here/smt-checked")) · cvc5 (sha256 $(d16 "$TOPAK_CVC5")) · ethos (sha256 $(d16 "$TOPAK_ETHOS")) · tla2tools.jar (sha256 $(d16 "$jar")) · one thread · backend timeouts x${STRETCH:-1}"
echo "An opaque constant under a binder is sound when the term it stands for mentions no variable bound around it (a step's primed goal, the prime of a variable-tuple definition); it is the binder case when the term does (an ENABLED, a \\cdot or a temporal formula over the bound variable). The listings say where; the step at each line says which. A difference under renaming is two terms that shared a name in one run; a capture is a bound variable tlapm's printer renames (x_1) over the name it would capture, which the print tlapm hashes shows as another term."
echo
echo "1. Sources"
python3 - "$here" <<'PY'
import collections, glob, hashlib, os, re, sys
here = sys.argv[1]
ops = [("ENABLED", r"\bENABLED\b"), ("\\cdot", r"\\cdot\b"), ("[]", r"\[\]"), ("<>", r"<>"), ("~>", r"~>"),
       ("WF_", r"\bWF_"), ("SF_", r"\bSF_"), ("\\EE", r"\\EE\b"), ("\\AA", r"\\AA\b")]
def strip(text):
    out, i, n, depth = [], 0, len(text), 0
    while i < n:
        if text.startswith("(*", i):
            depth += 1; i += 2; continue
        if depth and text.startswith("*)", i):
            depth -= 1; i += 2; continue
        if depth:
            out.append("\n" if text[i] == "\n" else " "); i += 1; continue
        if text.startswith("\\*", i):
            j = text.find("\n", i); j = n if j < 0 else j
            out.append(" " * (j - i)); i = j; continue
        if text[i] == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            out.append(" " * (j + 1 - i)); i = j + 1; continue
        out.append(text[i]); i += 1
    return "".join(out)
total, listed = 0, 0
for path in sorted(glob.glob(os.path.join(here, "*.tla"))):
    name = os.path.basename(path)
    if name.startswith("Trace_"):
        continue
    raw = open(path, encoding="utf-8").read().split("\n")
    code = strip("\n".join(raw)).split("\n")
    hits, shapes = [], collections.Counter()
    for k, line in enumerate(code, 1):
        found = [o for o, rx in ops if re.search(rx, line)]
        if not found:
            continue
        if found == ["[]"] and line.count("[]") == len(re.findall(r"\[\]\[", line)):
            shapes["[][A]_v, the box of an action"] += 1
        elif (found == ["[]"] and re.search(r"=>\s*\[\]\s*[A-Za-z_][A-Za-z0-9_]*\s*$", line) and re.search(r"\bSpec\w*\s*=>", line)
              and not re.search(r"\\A\b|\\E\b|\bNEW\b|\bCHOOSE\b|\{\s*\w+\s*\\in[^}]*:", line)):
            shapes["Spec => []P, P a bare name"] += 1
        elif found == ["[]"] and re.search(r"(?<!\|)->", line) and (line.lstrip().startswith("[]") or re.search(r"\bCASE\b", line)):
            shapes["[] between CASE arms"] += 1
        else:
            hits.append((k, found, raw[k - 1].strip()))
    if hits or shapes:
        dig = hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]
        print(f"  {name} (sha256 {dig}): {sum(shapes.values()) + len(hits)} lines" + (" (" + "; ".join(f"{v} {k}" for k, v in sorted(shapes.items())) + ")" if shapes else ""))
        for k, found, text in hits:
            print(f"    {k}: {' '.join(found)} · {text[:150]}")
        total += sum(shapes.values()) + len(hits); listed += len(hits)
print(f"  lines with an untranslated operator, outside comments: {total}, of which listed in full: {listed}")
PY

# What sections 3 and 4 share: TLA+ cut into comments, strings and code, and code into tokens.
cat > "$tmp/tla.py" <<'PY'
import re
KEYWORDS = set("""ACTION ASSUME ASSUMPTION AXIOM BOOLEAN BY CASE CHOOSE CONSTANT CONSTANTS COROLLARY DEF DEFINE DEFS
DOMAIN ELSE ENABLED EXCEPT EXTENDS FALSE HAVE HIDE IF IN INSTANCE LAMBDA LEMMA LET LOCAL MODULE NEW OBVIOUS OMITTED
ONLY OTHER PICK PROOF PROPOSITION PROVE QED RECURSIVE SF_ STATE STRING SUBSET SUFFICES TAKE TEMPORAL THEN THEOREM TRUE
UNCHANGED UNION USE VARIABLE VARIABLES WF_ WITH WITNESS""".split())
BINDERS = {"\\A", "\\E", "\\AA", "\\EE", "\\forall", "\\exists", "CHOOSE", "LAMBDA"}
IDENT = re.compile(r"[A-Za-z0-9_]*[A-Za-z][A-Za-z0-9_]*")
MULTI = ["|->", "<=>", "~>", "->", "<-", ":>", "::=", ":=", "::", "==", "=>", "=<", "<=", ">=", "/\\", "\\/", "...", "..",
         "<<", ">>", "[]", "<>", "/=", "@@", "-+->"]
def segments(text):
    """('code' | 'comment' | 'string', text, offset) pieces of a module."""
    i, n, start = 0, len(text), 0
    while i < n:
        if text.startswith("(*", i):
            if i > start: yield ("code", text[start:i], start)
            j, depth = i + 2, 1
            while j < n and depth:
                if text.startswith("(*", j): depth += 1; j += 2
                elif text.startswith("*)", j): depth -= 1; j += 2
                else: j += 1
            yield ("comment", text[i:j], i); i = start = j; continue
        if text.startswith("\\*", i):
            if i > start: yield ("code", text[start:i], start)
            j = text.find("\n", i); j = n if j < 0 else j
            yield ("comment", text[i:j], i); i = start = j; continue
        if text[i] == '"':
            if i > start: yield ("code", text[start:i], start)
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            yield ("string", text[i:j + 1], i); i = start = j + 1; continue
        i += 1
    if start < n: yield ("code", text[start:], start)
def tokens(code, base=0):
    """(kind, text, offset) over code: ws, label, num, op, id."""
    i, n = 0, len(code)
    while i < n:
        c = code[i]
        if c.isspace():
            j = i
            while j < n and code[j].isspace(): j += 1
            yield ("ws", code[i:j], base + i); i = j; continue
        m = re.match(r"<(?:\d+|\*|\+)>[A-Za-z0-9_]*", code[i:i + 40])
        if m:
            yield ("label", m.group(0), base + i); i += len(m.group(0)); continue
        m = re.match(r"\\(?:[hH][0-9a-fA-F]+|[oO][0-7]+|[bB][01]+)(?![0-9A-Za-z_])", code[i:i + 80])
        if m:
            yield ("num", m.group(0), base + i); i += len(m.group(0)); continue
        if c == "\\" and i + 1 < n and code[i + 1].isalpha():
            j = i + 1
            while j < n and code[j].isalpha(): j += 1
            yield ("op", code[i:j], base + i); i = j; continue
        m, mi = re.match(r"\d+(?:\.\d+)?(?![A-Za-z_])", code[i:i + 40]), IDENT.match(code, i)
        if m and not mi:
            yield ("num", m.group(0), base + i); i += len(m.group(0)); continue
        if mi:
            yield ("id", mi.group(0), base + i); i = mi.end(); continue
        for op in MULTI:
            if code.startswith(op, i):
                yield ("op", op, base + i); i += len(op); break
        else:
            yield ("op", c, base + i); i += 1
def all_tokens(text):
    out = []
    for kind, s, off in segments(text):
        out += [(kind, s, off)] if kind != "code" else list(tokens(s, off))
    return out
def defined_names(text):
    """Names a module defines at column 0: a line opening with an identifier and holding == outside brackets."""
    names = set()
    code = "".join(s if k == "code" else re.sub(r"[^\n]", " ", s) for k, s, _ in segments(text))
    for line in code.split("\n"):
        m = re.match(r"(?:LOCAL[ \t]+)?([A-Za-z][A-Za-z0-9_]*)", line)
        if not m:
            continue
        m2 = re.match(r"(?:THEOREM|LEMMA|COROLLARY|PROPOSITION|AXIOM)[ \t]+([A-Za-z0-9_]+)[ \t]*==", line)
        if m2:
            names.add(m2.group(1)); continue
        depth, j = 0, m.end()
        while j < len(line):
            if line[j] in "([{": depth += 1
            elif line[j] in ")]}": depth -= 1
            elif depth == 0 and line.startswith("==", j):
                names.add(m.group(1)); break
            j += 1
    return names
PY

# The renamed copy of section 3. A single letter is renamed by a cyclic shift over the letters no keyword or standard
# module claims, a bijection applied to every occurrence at once; a longer name gets an unused name of its length.
cat > "$tmp/rename.py" <<'PY'
import glob, os, re, sys, zipfile
sys.path.insert(0, os.path.dirname(__file__))
from tla import KEYWORDS, BINDERS, IDENT, all_tokens, defined_names
spec, out, jar, stdlib = sys.argv[1:5]
MOD = re.compile(r"-{4,}\s*MODULE\s+([A-Za-z0-9_]+)")
std = []
with zipfile.ZipFile(jar) as z:
    std += [z.read(p).decode("utf-8", "replace") for p in z.namelist() if p.startswith("tla2sany/StandardModules/") and p.endswith(".tla")]
std += [open(p, encoding="utf-8", errors="replace").read() for p in glob.glob(os.path.join(stdlib, "*.tla"))]
builtin, modules = set(), set()
for t in std:
    builtin |= defined_names(t); modules |= set(MOD.findall(t))
corpus = {p: open(p, encoding="utf-8").read() for p in sorted(glob.glob(os.path.join(spec, "*.tla")))}
for t in corpus.values():
    modules |= set(MOD.findall(t))
KEEP = KEYWORDS | builtin | modules
USED = set(KEEP)
for t in corpus.values():
    USED |= {s for kind, s, _ in all_tokens(t) if kind == "id"}
LET, DIG = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", "0123456789"
ONE = sorted(c for c in LET if c not in KEEP)
MAP, TAKEN = {}, set(USED)
def new_name(s):
    if s not in MAP:
        if len(s) == 1:
            MAP[s] = ONE[(ONE.index(s) + 1) % len(ONE)]
        else:
            for i in range(len(s) - 1, -1, -1):
                pool = LET if s[i].isalpha() else DIG if s[i].isdigit() else ""
                cands = [s[:i] + c + s[i + 1:] for c in pool]
                cands = [x for x in cands if x != s and x not in TAKEN and IDENT.fullmatch(x) and not re.fullmatch(r"h[0-9a-f]{5}", x)
                         and not x.startswith(("WF_", "SF_"))]
                if cands:
                    MAP[s] = cands[0]; TAKEN.add(cands[0]); break
            else:
                raise SystemExit(f"no unused name of the length of {s}")
    return MAP[s]
def rename(text):
    toks = all_tokens(text)
    sig = [k for k, t in enumerate(toks) if t[0] not in ("ws", "comment", "string")]
    pos = {k: j for j, k in enumerate(sig)}
    at = lambda k, d: toks[sig[pos[k] + d]] if 0 <= pos[k] + d < len(sig) else ("", "", 0)
    stack, record, inner = [], {}, {}
    for k in sig:
        s = toks[k][1]
        if s in ("[", "(", "{", "<<"):
            stack.append(k)
            if s == "[":
                record[k] = at(k, 1)[0] == "id" and at(k, 2)[1] in (":", "|->")
        elif s in ("]", ")", "}", ">>") and stack:
            stack.pop()
        elif toks[k][0] == "id":
            inner[k] = stack[-1] if stack else None
    def in_binder_list(k):
        j = k
        while at(j, -1)[1] == "," and at(j, -2)[0] == "id":
            j = sig[pos[j] - 2]
        return at(j, -1)[1] in BINDERS
    res = []
    for k, (kind, s, _) in enumerate(toks):
        if kind != "id":
            res.append(s); continue
        b = inner[k]
        field = (at(k, -1)[1] == "." and at(k, -2)[0] != "label") or \
                (b is not None and record.get(b) and at(k, -1)[1] in ("[", ",") and at(k, 1)[1] in (":", "|->")
                 and not in_binder_list(k))
        pre = ""
        if s.startswith(("WF_", "SF_")) and len(s) > 3:
            pre, s = s[:3], s[3:]
        elif s.startswith("_") and k > 0 and toks[k - 1][1] in ("]", ">>"):
            pre, s = "_", s[1:]
        res.append(pre + (s if field or s in KEEP or not IDENT.fullmatch(s) else new_name(s)))
    return "".join(res)
os.makedirs(out, exist_ok=True)
for p, t in corpus.items():
    open(os.path.join(out, os.path.basename(p)), "w", encoding="utf-8").write(rename(t))
print(f"{len(corpus)} modules copied; {len(MAP)} identifiers renamed, each to a name of the same length; {len(KEEP)} keyword, standard and module names kept")
PY
# The comparison of section 3, for one module: the two runs' inputs to each backend, paired in the order they were made,
# and every obligation's route.
cat > "$tmp/names.py" <<'PY'
import collections, glob, os, re, sys
mod, da, db, tba, tbb, out = sys.argv[1:7]
KINDS = {".smt": "SMT", ".znn": "Zenon", ".thy": "Isabelle", ".ls4": "LS4"}
# A name is h and five hex digits: after __ in SMT, bare to LS4, and to Zenon and Isabelle either as a_h…a (when it
# ends in a digit) or bare (when it ends in a letter).
ZI = re.compile(r"(?<![0-9A-Za-z_'])(?:a_(h[0-9a-f]{5})a|(h[0-9a-f]{5}))(?![0-9A-Za-z_'])")
HASHED = {"SMT": re.compile(r"(?<=__)(h[0-9a-f]{5})(?![0-9A-Za-z_])"), "Zenon": ZI, "Isabelle": ZI,
          "LS4": re.compile(r"(?<![0-9A-Za-z_])(h[0-9a-f]{5})(?![0-9A-Za-z_])")}
LEFT = re.compile(r"(?<![0-9a-zA-Z])_?h[0-9a-f]{5}(?![0-9A-Za-z])")
TOKEN, IDENT = re.compile(r"[A-Za-z0-9_']+|\S"), re.compile(r"[A-Za-z0-9_']*[A-Za-z][A-Za-z0-9_']*")
def messages(tb):
    final, seq = {}, collections.defaultdict(list)
    for blk in open(tb, encoding="utf-8", errors="replace").read().split("@!!BEGIN"):
        f = dict(re.findall(r"@!!(\w+):(.*)", blk))
        if f.get("type") != "obligation" or "id" not in f:
            continue
        line = f["loc"].split(":")[0] if "loc" in f else "?"
        if f.get("status") in ("proved", "failed") and f.get("already", "").strip() != "true":
            seq[f.get("prover", "-")].append(line)
        if f.get("status") in ("proved", "trivial", "failed", "interrupted", "omitted", "missing"):
            final[f["id"]] = (line, f["status"], f.get("prover", "-"))
    return final, seq
def inputs(d):
    res, unread = collections.defaultdict(list), []
    files = [p for p in glob.glob(os.path.join(d, "tlapm_*")) if os.path.splitext(p)[1] in KINDS]
    for p in sorted(files, key=lambda p: (os.stat(p).st_mtime_ns, p)):
        kind = KINDS[os.path.splitext(p)[1]]
        text = open(p, encoding="utf-8", errors="replace").read()
        line = re.search(r"Generated from file .*, line (\d+)", text)
        if kind == "SMT":
            text = "\n".join(l for l in text.split("\n") if not l.lstrip().startswith(";"))
        elif kind != "LS4":
            text = re.sub(r"(?m)^theory \S+", "theory T", re.sub(r"\(\*.*?\*\)", " ", text, flags=re.S))
        names = ["".join(g for g in m.groups() if g) for m in HASHED[kind].finditer(text)]
        masked = HASHED[kind].sub(" # ", text)
        if LEFT.search(masked):
            unread.append(f"{kind} {os.path.basename(p)}: {LEFT.search(masked).group(0)}")
        shape = collections.Counter("I" if IDENT.fullmatch(t) else t for t in TOKEN.findall(masked))
        res[kind].append((shape, tuple(sorted(collections.Counter(names).values())), set(names), line.group(1) if line else None))
    return res, unread
ra, sa = messages(tba)
rb, _ = messages(tbb)
(ia, ua), (ib, ub) = inputs(da), inputs(db)
cells, diffs, totals = [], [], collections.Counter()
for kind in ("SMT", "Zenon", "Isabelle", "LS4"):
    a, b = ia.get(kind, []), ib.get(kind, [])
    many = [x for x in a if len(x[2]) >= 2]
    pairs = sum(len(x[2]) * (len(x[2]) - 1) // 2 for x in a)
    lines = sa.get({"SMT": "smt", "Zenon": "zenon", "Isabelle": "isabelle", "LS4": "ls4"}[kind], [])
    where = lambda j, x: f"line {x[3] or (lines[j] if j < len(lines) and len(lines) == len(a) else '?')}"
    diffs += [f"{kind} {where(j, x)}: " + ("another shape" if x[0] != y[0] else "another pattern of names") for j, (x, y) in enumerate(zip(a, b)) if x[:2] != y[:2]]
    if len(a) != len(b):
        diffs.append(f"{kind}: {len(a)} inputs, {len(b)} renamed")
    kept = sum(1 for x, y in zip(a, b) if x[2] & y[2])
    if kept:
        diffs.append(f"{kind}: {kept} inputs keep a name under the renaming")
    totals.update(inputs=len(a), many=len(many), pairs=pairs)
    cells.append(f"{kind} {len(a)}" + (f" ({len(many)} with two or more names, at most {max(len(x[2]) for x in a)}, {pairs} pairs)" if many else ""))
diffs += [f"an input holds a name the scan does not read: {u}" for u in ua + ub]
moved = [i for i in sorted(set(ra) | set(rb), key=int) if ra.get(i, ("?",) + ("none", "-"))[1:] != rb.get(i, ("?",) + ("none", "-"))[1:]]
if moved:
    diffs.append("routes differ: " + ", ".join(f"line {(ra.get(i) or rb.get(i))[0]} " + "/".join(ra.get(i, ("", "none", "-"))[1:]) + " -> " + "/".join(rb.get(i, ("", "none", "-"))[1:]) for i in moved))
print(f"== {mod}.tla: " + " · ".join(cells) + f" · renamed run: {'each of ' + str(len(ra)) + ' obligations by the same route' if not moved else str(len(moved)) + ' obligations by another route'}, " + ("no difference" if not diffs else f"{len(diffs)} DIFFERENCES"))
for d in diffs:
    print(f"     {d}")
with open(out, "a") as f:
    f.write(f"{totals['inputs']} {totals['many']} {totals['pairs']} {len(diffs)}\n")
sys.exit(1 if diffs else 0)
PY
# Section 4: captures in the obligations as tlapm prints them, and a SANY parse of each proof module.
cat > "$tmp/capture.py" <<'PY'
import glob, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
from tla import tokens, all_tokens
here, tmp, lib, jar = sys.argv[1:5]
mods = sys.argv[5].split()
OPEN, CLOSE = {"(", "[", "{", "<<"}, {")", "]", "}", ">>"}
BINDERS = {"\\A", "\\E", "\\AA", "\\EE", "CHOOSE", "LAMBDA"}
def label(toks, encl, j):
    """A record field, which no binder captures: r.f, and f in [f |-> e] or [f : S]."""
    if j > 0 and toks[j - 1][1] == ".":
        return True
    return (encl[j] == "[" and j > 0 and toks[j - 1][1] in ("[", ",") and j + 1 < len(toks)
            and toks[j + 1][1] in ("|->", ":"))
def obligations(path):
    """id -> (line, the obligation as tlapm prints it once normalized)."""
    out = {}
    for blk in open(path, encoding="utf-8", errors="replace").read().split("@!!BEGIN"):
        if "@!!type:obligation" not in blk:
            continue
        fields, key = {}, None
        for line in blk.split("\n"):
            m = re.match(r"@!!(\w+):(.*)", line)
            if m:
                key = m.group(1); fields[key] = m.group(2)
            elif key == "obl" and not line.startswith("@!!END"):
                fields["obl"] += "\n" + line
        if fields.get("status", "").strip() == "normalized" and "obl" in fields and "id" in fields:
            out[fields["id"].strip()] = (fields.get("loc", "?").split(":")[0], fields["obl"])
    return out
def sites(text, suffixed):
    """Every renamed name x_N whose scope holds x. A name inside brackets has the rest of its group as scope; one at
    the top level has the rest of its hypothesis, which ends at a top-level comma outside a quantifier's variable
    list, or at ASSUME or PROVE."""
    toks = [(k, s) for k, s, _ in tokens(text) if k != "ws"]
    names = {s for k, s in toks if k == "id"}
    depth, d, sep, in_list, stack, encl = [], 0, set(), False, [], []
    for j, (k, t) in enumerate(toks):
        depth.append(d); encl.append(stack[-1] if stack else None)
        if t in OPEN: d += 1; stack.append(t)
        elif t in CLOSE:
            d -= 1
            if stack: stack.pop()
        elif d == 0:
            if t in BINDERS: in_list = True
            elif t == ":" and in_list: in_list = False
            elif (t == "," and not in_list) or t in ("PROVE", "ASSUME"): sep.add(j)
    found = set()
    for i, (k, s) in enumerate(toks):
        m = re.fullmatch(r"(.*[A-Za-z].*)_(\d+)", s) if k == "id" else None
        if not m or s in suffixed or m.group(1) not in names:
            continue
        base = m.group(1)
        if depth[i] > 0:
            end = next((j for j in range(i + 1, len(toks)) if toks[j][1] in CLOSE and depth[j] == depth[i]), len(toks))
        else:
            end = next((j for j in range(i + 1, len(toks)) if j in sep), len(toks))
        if any(toks[j][0] == "id" and toks[j][1] == base and not label(toks, encl, j) for j in range(i + 1, end)):
            found.add((s, base))
    return found
# a name the sources already end in _N is not a renaming
suffixed = set()
for p in glob.glob(os.path.join(here, "*.tla")):
    if not os.path.basename(p).startswith("Trace_"):
        suffixed |= {s for k, s, _ in all_tokens(open(p, encoding="utf-8").read()) if k == "id" and re.fullmatch(r".*_\d+", s)}
tot = {"obs": 0, "ids": 0, "caps": 0, "parse": 0}
bad = False
for m in mods:
    tb = os.path.join(tmp, m + ".cache", "toolbox.txt")
    if not os.path.exists(tb):
        continue
    obs = obligations(tb)
    text = open(tb, encoding="utf-8", errors="replace").read()
    ids, final, reused = set(re.findall(r"@!!id:(\d+)", text)), {}, set()
    for blk in text.split("@!!BEGIN"):
        f = dict(re.findall(r"@!!(\w+):(.*)", blk))
        if f.get("type") == "obligation" and "id" in f and f.get("status") in ("proved", "trivial", "failed", "interrupted", "omitted", "missing"):
            final[f["id"]] = f["status"]
            if f.get("already", "").strip() == "true": reused.add(f["id"])
    sent = {i for i in ids if final.get(i) != "trivial" and i not in reused}
    unread = sent - set(obs)
    found = sorted({(int(line) if line.isdigit() else 0, s, base) for line, text in obs.values() for s, base in sites(text, suffixed)})
    r = subprocess.run(["java", f"-DTLA-Library={lib}", "-cp", jar, "tla2sany.SANY", m + ".tla"], cwd=here, capture_output=True, text=True)
    parses = r.returncode == 0 and not re.search(r"\*\*\* ?Errors|Semantic errors|Fatal errors|Parse Error", r.stdout + r.stderr)
    tot["obs"] += len(obs); tot["ids"] += len(sent); tot["caps"] += len(found); tot["parse"] += parses
    bad = bad or bool(found) or not parses or bool(unread)
    print(f"== {m}.tla: {len(obs)} obligations printed normalized, of the {len(sent)} sent to a backend" + (f" ({len(unread)} SENT AND NOT PRINTED)" if unread else "")
          + " · " + (f"{len(found)} CAPTURES" if found else "no capture") + " · SANY: " + ("parses" if parses else "DOES NOT PARSE"))
    for line, s, base in found:
        print(f"     line {line} · {s} binds over {base}")
print(f"\nModules: {len(mods)} · obligations sent to a backend: {tot['ids']}, printed normalized: {tot['obs']} · captures: {tot['caps']} · modules SANY parses: {tot['parse']} of {len(mods)}"
      + (f" · names the sources end in _N, not taken for renamings: {', '.join(sorted(suffixed))}" if suffixed else ""))
sys.exit(1 if bad else 0)
PY
mkdir -p "$tmp/renamed"
renamed=$(python3 "$tmp/rename.py" "$here" "$tmp/renamed" "$jar" "$lib") || { echo "renaming failed: $renamed"; exit 2; }
run() {   # run <dir> <module> <evidence dir> <cache dir>: a certified run as proof-cert.sh makes it, on one thread
  (cd "$1" || exit 2; export TOPAK_PROOF_DIR="$3"; "$tlapm" -C --cleanfp --strict --stretch "${STRETCH:-1}" --threads 1 --debug tempfiles \
      --printallobs --cache-dir "$4" --toolbox 0 0 --solver "$here/smt-checked \"\$file\"" "$2.tla" > "$4/toolbox.txt" 2>&1)
}
echo
echo "2. Runs"
status=0
: > "$tmp/names.txt"
for mod in $mods; do
  mod=${mod%.tla}
  [ -f "$here/$mod.tla" ] || { echo "== $mod.tla: no such module"; status=1; continue; }
  ev="$tmp/$mod.ev"; cache="$tmp/$mod.cache"; evr="$tmp/$mod.ev-r"; cacher="$tmp/$mod.cache-r"
  mkdir -p "$ev" "$cache" "$evr" "$cacher"
  run "$tmp/renamed" "$mod" "$evr" "$cacher" &
  run "$here" "$mod" "$ev" "$cache"
  rc=$?
  wait
  python3 - "$mod" "$cache/toolbox.txt" "$ev" "$rc" "$tmp/counts" "$(d16 "$here/$mod.tla")" <<'PY' || status=1
import collections, glob, hashlib, json, os, re, sys
mod, tbp, ev, rc, counts, dig = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5], sys.argv[6]
tb = open(tbp, encoding="utf-8", errors="replace").read()
final, line_of, reused = {}, {}, set()
for blk in tb.split("@!!BEGIN"):
    if "@!!type:obligation" not in blk:
        continue
    f = dict(re.findall(r"@!!(\w+):(.*)", blk))
    i = f.get("id")
    if i is None:
        continue
    if "loc" in f and i not in line_of:
        line_of[i] = int(f["loc"].split(":")[0])
    if f.get("status") in ("proved", "trivial", "failed", "interrupted", "omitted", "missing"):
        final[i] = (f["status"], f.get("prover", "-"))
        if f.get("already", "").strip() == "true":
            reused.add(i)
ids = sorted(set(re.findall(r"@!!id:(\d+)", tb)), key=int)
if not ids:
    print(f"== {mod}.tla (sha256 {dig}): no obligations (tlapm exit {rc})"); sys.exit(1)
routes = collections.Counter(final.get(i, ("unproved", "-")) for i in ids)
def n(st, pr): return routes[(st, pr)]
known = {("trivial", "tlapm"), ("proved", "smt"), ("proved", "zenon"), ("proved", "isabelle"), ("proved", "ls4")}
other = sum(v for k, v in routes.items() if k not in known)
# this run's verdict, by proof-cert.sh's test
rejected = sorted(set(re.findall(r"Isabelle/TLA\+ rejected the proof of obligation (\d+)", tb)), key=int)
isa_ok = "Proof checking done. No errors found." in tb and not rejected
tr = re.search(r"Obligation checking trace follows\. \*\)\s*\(\*([^*]*)\*\)", tb)   # +k entered, -k left accepted
left = set(re.findall(r"-(\d+)", tr.group(1))) if tr else set()
unaccepted = set() if isa_ok else {i for i in ids if final.get(i) == ("proved", "zenon") and i not in left}
calls = [l.split() for l in open(os.path.join(ev, "calls.log"))] if os.path.exists(os.path.join(ev, "calls.log")) else []
accepted = sum(1 for c in calls if c[1] == "unsat" and c[2] == "1")
smt_new = sum(1 for i in ids if final.get(i) == ("proved", "smt") and i not in reused)
why = []
if other: why.append(f"{other} obligation(s) not proved")
if n("proved", "zenon") and not isa_ok: why.append(f"Isabelle accepted {n('proved', 'zenon') - len(unaccepted)} of Zenon's {n('proved', 'zenon')} proofs (tlapm reports {len(rejected)} refused)" if tr else "Isabelle could not check Zenon's proofs")
if smt_new > accepted: why.append(f"{smt_new} SMT-proved obligations against {accepted} accepted proofs")
if rc and not why: why.append(f"tlapm exit {rc}")
print(f"== {mod}.tla (sha256 {dig}): {len(ids)} obligations (trivial {n('trivial','tlapm')} · SMT {n('proved','smt')} · Zenon {n('proved','zenon')} "
      f"· Isabelle {n('proved','isabelle')} · LS4 {n('proved','ls4')} · not proved {other}) · {len(reused)} results reused · tlapm exit {rc} · "
      + ("this run certifies" if not why else "this run does not certify: " + "; ".join(why)))
sys.setrecursionlimit(100000)
def parse(s):
    stack, i, L = [[]], 0, len(s)
    while i < L:
        c = s[i]
        if c.isspace(): i += 1
        elif c == ";":
            j = s.find("\n", i); i = L if j < 0 else j
        elif c == "(":
            stack.append([]); i += 1
        elif c == ")":
            top = stack.pop(); stack[-1].append(top); i += 1
        elif c in '"|':
            j = s.find(c, i + 1); stack[-1].append(s[i:j + 1]); i = j + 1
        else:
            j = i
            while j < L and not s[j].isspace() and s[j] not in "();": j += 1
            stack[-1].append(s[i:j]); i = j
    return stack[0]
def walk(t, depth, hits):
    if isinstance(t, list):
        if t and t[0] in ("forall", "exists", "lambda"):
            for y in t[2:]: walk(y, depth + 1, hits)
            return
        for y in t: walk(y, depth, hits)
    elif "smt__TLA____Anon__OPAQUE__" in t and depth > 0:
        hits.add(t.replace("smt__TLA____Anon__OPAQUE__", ""))
rows = []
for q in sorted(glob.glob(os.path.join(ev, "q-*.smt2"))):
    text = open(q, encoding="utf-8").read()
    hits = set()
    walk(parse(text), 0, hits)
    if not hits:
        continue
    meta = os.path.splitext(q)[0] + ".json"
    line = "?"
    if os.path.exists(meta):
        m = re.search(r"line (\d+)", json.load(open(meta)).get("obligation", ""))
        line = m.group(1) if m else "?"
    body = "\n".join(l for l in text.split("\n") if "Generated from" not in l)
    rows.append((int(line) if line.isdigit() else 0, os.path.basename(q)[:-5], hashlib.sha256(body.encode()).hexdigest()[:16], sorted(hits)))
print(f"   SMT queries with an opaque constant under a binder: {len(rows)}")
for line, q, dg, hs in sorted(rows):
    print(f"     line {line} · {q} · content {dg} · {' '.join(hs)}")
zi = sorted(((line_of.get(i, 0), final[i][1], i in unaccepted) for i in ids if final.get(i, ("", ""))[1] in ("zenon", "isabelle") and final[i][0] == "proved"))
print(f"   Obligations Zenon or Isabelle closed: {len(zi)}" + (f", of which Isabelle did not accept {sum(1 for z in zi if z[2])} of Zenon's proofs" if any(z[2] for z in zi) else ""))
for line, pr, rej in zi:
    print(f"     line {line} · {pr}" + (" · NOT ACCEPTED by Isabelle" if rej else ""))
with open(counts, "a") as f:
    f.write(f"{len(rows)} {len(zi)} {0 if why else 1}\n")
PY
  python3 "$tmp/names.py" "$mod" "$cache/$mod.tlaps" "$cacher/$mod.tlaps" "$cache/toolbox.txt" "$cacher/toolbox.txt" "$tmp/ncounts" >> "$tmp/names.txt" || status=1
done
python3 - "$tmp/counts" <<'PY'
import os, sys
rows = [tuple(map(int, l.split())) for l in open(sys.argv[1])] if os.path.exists(sys.argv[1]) else []
print(f"\nModules run: {len(rows)}, of which this run certifies: {sum(r[2] for r in rows)} · SMT queries with an opaque constant under a binder: {sum(r[0] for r in rows)} · obligations Zenon or Isabelle closed: {sum(r[1] for r in rows)}")
PY
echo
echo "3. Names"
echo "  renamed copy: $renamed"
cat "$tmp/names.txt"
python3 - "$tmp/ncounts" <<'PY'
import os, sys
rows = [tuple(map(int, l.split())) for l in open(sys.argv[1])] if os.path.exists(sys.argv[1]) else []
pairs = sum(r[2] for r in rows)
print(f"\nModules run: {len(rows)} · backend inputs: {sum(r[0] for r in rows)}, of which hold two or more names: {sum(r[1] for r in rows)} · pairs of names within an input: {pairs}, so {pairs / 2**20:.4f} collisions to expect by accident · modules whose renamed run differs: {sum(1 for r in rows if r[3])}")
PY
echo
echo "4. Capture"
python3 "$tmp/capture.py" "$here" "$tmp" "$lib" "$jar" "$(echo $mods | sed 's/\.tla//g')" || status=1
exit $status
