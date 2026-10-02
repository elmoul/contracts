"""
Schema-level validation for schemas/app/descriptor.json (app.descriptor/1) and the optional
`app` summary on schemas/control-plane/registry.entry.json.

Fixtures: tests/fixtures/app-descriptor/valid-*.yaml must pass, invalid-*.yaml must be
rejected (one per enforced rule). Run: python tests/validate_app_descriptor.py
"""
import copy
import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "tests" / "fixtures" / "app-descriptor"
DESCRIPTOR = json.loads((ROOT / "schemas" / "app" / "descriptor.json").read_text(encoding="utf-8"))
REGISTRY = json.loads((ROOT / "schemas" / "control-plane" / "registry.entry.json").read_text(encoding="utf-8"))

EXPECTED_VALID = {
    "valid-in-repo-full.yaml",
    "valid-in-repo-ungated-pr-only.yaml",
    "valid-wrapped-third-party-pr-only.yaml",
    "valid-in-repo-all-delivery-fields.yaml",
    "valid-in-repo-no-delivery-fields.yaml",
}
EXPECTED_INVALID = {
    "invalid-third-party-no-fork.yaml",
    "invalid-third-party-empty-fork.yaml",
    "invalid-third-party-full.yaml",
    "invalid-empty-checks-full.yaml",
    "invalid-in-repo-app-root-app.yaml",
    "invalid-wrapped-app-root-dot.yaml",
    "invalid-command-shell-string.yaml",
    "invalid-env-map.yaml",
    "invalid-workflow-empty-state.yaml",
    "invalid-hostname-dot.yaml",
    "invalid-hostname-uppercase.yaml",
    "invalid-github-slug-no-slash.yaml",
}


def errors(schema, doc):
    return list(Draft202012Validator(schema).iter_errors(doc))


def expect_valid(schema, doc, label):
    errs = errors(schema, doc)
    if errs:
        raise AssertionError(f"{label}: expected valid, got {[e.message for e in errs]}")
    print(f"PASS  {label}")


def expect_invalid(schema, doc, label):
    errs = errors(schema, doc)
    if not errs:
        raise AssertionError(f"{label}: expected invalid, but document passed")
    print(f"PASS  {label} (rejected: {errs[0].message[:90]})")


def load(name):
    return yaml.safe_load((FIXTURES / name).read_text(encoding="utf-8"))


def main():
    Draft202012Validator.check_schema(DESCRIPTOR)
    on_disk = {p.name for p in FIXTURES.glob("*.yaml")}
    assert on_disk == EXPECTED_VALID | EXPECTED_INVALID, f"fixture set drifted: {on_disk ^ (EXPECTED_VALID | EXPECTED_INVALID)}"
    assert "NOT `app.manifest`" in DESCRIPTOR["description"], "description must say it is distinct from app.manifest"

    for name in sorted(EXPECTED_VALID):
        expect_valid(DESCRIPTOR, load(name), f"app.descriptor: {name}")
    for name in sorted(EXPECTED_INVALID):
        expect_invalid(DESCRIPTOR, load(name), f"app.descriptor: {name}")

    entry = {
        "functionalName": "portfolio", "kind": "app", "side": "ui", "status": "active",
        "repoUrl": "https://github.com/elmoul/portfolio", "version": "v0.1.0",
        "updatedAt": "2026-10-02T10:00:00Z",
    }
    expect_valid(REGISTRY, entry, "registry.entry: without app summary (still valid)")
    with_app = copy.deepcopy(entry)
    with_app["app"] = {"name": "portfolio", "trackerKey": "POR", "layout": "in-repo", "ownership": "owned",
                       "deliveryMode": "full", "devUrl": "http://portfolio.platform.localhost"}
    expect_valid(REGISTRY, with_app, "registry.entry: with app summary")
    bad = copy.deepcopy(with_app)
    bad["app"]["deliveryMode"] = "yolo"
    expect_invalid(REGISTRY, bad, "registry.entry: app.deliveryMode outside enum")
    bad = copy.deepcopy(with_app)
    bad["app"]["env"] = {"K": "v"}
    expect_invalid(REGISTRY, bad, "registry.entry: app summary rejects extra properties")
    full = copy.deepcopy(with_app)
    full["app"].update({
        "repoUrl": "https://github.com/ElasMoul/plants", "integrationBranch": "dev",
        "githubSlug": "ElasMoul/plants", "hostname": "planotell",
        "workflow": {"planned": "Plan", "developing": "Develop", "ready-for-test": "Review", "accepted": "Staging"},
    })
    expect_valid(REGISTRY, full, "registry.entry: app summary with every delivery field")
    for path, value, label in [
        (("workflow", "planned"), "", "empty workflow state"),
        (("workflow", "done"), "Done", "unknown workflow stage"),
        (("hostname",), "Plano.tell", "hostname with dot/uppercase"),
        (("githubSlug",), "plants", "githubSlug without slash"),
        (("repoUrl",), "git@github.com:x/y", "non-http repoUrl"),
    ]:
        bad = copy.deepcopy(full)
        target = bad["app"]
        for k in path[:-1]:
            target = target[k]
        target[path[-1]] = value
        expect_invalid(REGISTRY, bad, f"registry.entry: app.{label}")

    gate = copy.deepcopy(with_app)
    gate["app"].update({"requiredChecks": ["build", "test", "lint"], "appRoot": "app", "releaseBranch": "main"})
    expect_valid(REGISTRY, gate, "registry.entry: app summary with requiredChecks, appRoot, releaseBranch")
    pr_only = copy.deepcopy(with_app)
    pr_only["app"].update({"deliveryMode": "pr-only", "requiredChecks": [], "appRoot": "."})
    expect_valid(REGISTRY, pr_only, "registry.entry: app summary with empty requiredChecks (pr-only)")
    for key, value, label in [
        ("requiredChecks", ["build", ""], "empty check name"),
        ("requiredChecks", ["build", "build"], "duplicate check name"),
        ("appRoot", "src", "appRoot other than '.' or 'app'"),
        ("appRoot", "./app", "appRoot './app'"),
        ("releaseBranch", "", "empty releaseBranch"),
    ]:
        bad = copy.deepcopy(gate)
        bad["app"][key] = value
        expect_invalid(REGISTRY, bad, f"registry.entry: app.{label}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
