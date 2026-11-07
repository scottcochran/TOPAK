"""Layer: deployment · pytest: select the declaration per deployment and report the inventory.
Extends 04-assurance/tdd/conftest.py: `pytest --declaration=declaration.yaml --report-inventory`
prints, after the run, every theorem marker with holds/void and the premises that voided it."""
import pytest

pytest_plugins = ["assurance_conftest"]     # 04-assurance/tdd/conftest.py, on the path


def pytest_addoption(parser):
    parser.addoption("--report-inventory", action="store_true")


def pytest_terminal_summary(terminalreporter, config):
    if not config.getoption("--report-inventory"):
        return
    inv = {}
    for rep in terminalreporter.stats.get("passed", []) + terminalreporter.stats.get("skipped", []):
        item = next(i for i in config.pluginmanager.get_plugin("session").items if i.nodeid == rep.nodeid)
        for m in item.iter_markers("theorem"):
            inv.setdefault(m.args[0], []).append("void: " + rep.longrepr[2].split("void: ", 1)[1] if rep.skipped and "void" in str(rep.longrepr) else "holds")
    terminalreporter.section(f"inventory for {config.getoption('--declaration')} (ADR-0023 §2)")
    for t, vs in sorted(inv.items()):
        terminalreporter.line(f"  {t:36} {'void' if any(v.startswith('void') for v in vs) else 'holds':6} {'; '.join(v for v in vs if v != 'holds')}")
