#!/usr/bin/env python3
"""Check the SHACL shapes of the MQTT ODP against the fixtures.

Every shape in constraints/ is checked twice over: once against a fixture that
has to conform, and once against a fixture built to break exactly that shape.
A shape that never fires proves nothing, so the expected result is not "no
violations" but a named set of them -- the table EXPECTED below. A fixture that
reports the wrong shape fails here just as loudly as one that reports nothing.

The data graph is always mqtt.ttl merged with the fixture. The reason code
shape reads the ontology's own appliesToPacket annotations and the class
hierarchy of the control packets, so without the ontology it would quietly find
nothing.

Usage:
    python tools/check_shapes.py [<fixture> ...]

Needs rdflib and pyshacl (see requirements.txt). In a fresh clone:
    python -m venv .venv
    .venv/Scripts/python -m pip install -r requirements.txt
    .venv/Scripts/python tools/check_shapes.py
On Linux and macOS the interpreter is .venv/bin/python.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ONTOLOGY = ROOT / "mqtt.ttl"
SHAPES_DIR = ROOT / "constraints"
FIXTURE_DIR = ROOT / "tests" / "fixtures"
SHAPES_NS = "http://www.w3id.org/hsu-aut/MQTT/shapes#"

# Fixture -> the shapes that must report, with their severity. An empty set
# means the fixture has to pass without a single result.
EXPECTED: dict[str, set[str]] = {
    "valid.ttl": set(),
    "invalid-topic-name-wildcard.ttl": {
        "TopicNameNoWildcards:Violation",
    },
    # Since 6.0.0 the response topic is a MQTT:Topic, so this fixture has to
    # trip the one topic name shape -- not a shape of its own.
    "invalid-response-topic-wildcard.ttl": {
        "TopicNameNoWildcards:Violation",
    },
    "invalid-same-filter-node.ttl": {
        "SubscriptionsShareAFilterNode:Violation",
    },
    "invalid-same-filter-string.ttl": {
        "SubscriptionsShareAFilterString:Violation",
    },
    "invalid-shared-subscription-prefix.ttl": {
        "SharedSubscriptionFilterPrefix:Violation",
    },
    "invalid-reason-code-packet.ttl": {
        "ReasonCodeNotAllowedInPacketType:Violation",
    },
    "warning-shared-subscription-no-filter-string.ttl": {
        "SharedSubscriptionFilterStringPresent:Warning",
    },
}


def load_shapes():
    from rdflib import Graph

    graph = Graph()
    files = sorted(SHAPES_DIR.glob("*.ttl"))
    if not files:
        sys.exit(f"no shapes in {SHAPES_DIR}")
    for path in files:
        graph.parse(path.as_posix(), format="turtle")
    return graph, files


def results(data_files: list[Path], shapes):
    """Validate the ontology plus the given files, return the results found."""
    from rdflib import Graph, Namespace
    from pyshacl import validate

    sh = Namespace("http://www.w3.org/ns/shacl#")

    data = Graph()
    data.parse(ONTOLOGY.as_posix(), format="turtle")
    for path in data_files:
        data.parse(path.as_posix(), format="turtle")

    # inference="none": the shapes are written so that they need no entailment.
    # The one place a class hierarchy is needed -- the control packet types --
    # is read explicitly in the query, which is cheaper and easier to read than
    # an RDFS closure over the whole ontology.
    _, report, _ = validate(data, shacl_graph=shapes,
                            inference="none", advanced=True,
                            allow_warnings=True)

    found = []
    for result in report.subjects(sh.resultSeverity, None):
        severity = report.value(result, sh.resultSeverity)
        constraint = report.value(result, sh.sourceConstraint)
        shape = constraint if constraint is not None else report.value(result, sh.sourceShape)
        found.append({
            "shape": short(shape),
            "severity": str(severity).rsplit("#", 1)[-1],
            "focus": short(report.value(result, sh.focusNode)),
            "value": report.value(result, sh.value),
            "message": str(report.value(result, sh.resultMessage) or ""),
        })
    return found


def short(node) -> str:
    if node is None:
        return "?"
    text = str(node)
    if text.startswith(SHAPES_NS):
        return text[len(SHAPES_NS):]
    return text.rsplit("#", 1)[-1] if "#" in text else text


def main() -> int:
    shapes, shape_files = load_shapes()
    print(f"shapes: {', '.join(p.name for p in shape_files)}")

    wanted = sys.argv[1:]
    names = wanted or sorted(EXPECTED)
    failures = 0

    # Control first: the pattern itself must not trip over its own shapes.
    # It carries 51 individuals, among them all 45 reason codes.
    plain = results([], shapes)
    if plain:
        failures += 1
        print("  FAIL  mqtt.ttl alone reports:")
        for item in plain:
            print(f"          {item['shape']} on {item['focus']}")
    else:
        print("  ok    mqtt.ttl alone: no result")

    for name in names:
        if name not in EXPECTED:
            print(f"  FAIL  {name}: not in the table EXPECTED")
            failures += 1
            continue
        path = FIXTURE_DIR / name
        if not path.exists():
            print(f"  FAIL  {name}: file missing")
            failures += 1
            continue

        found = results([path], shapes)
        actual = {f"{item['shape']}:{item['severity']}" for item in found}
        expected = EXPECTED[name]

        if actual == expected:
            if expected:
                print(f"  ok    {name}: {', '.join(sorted(actual))}")
                for item in found:
                    print(f"          {item['focus']} -> {item['message'][:120]}")
            else:
                print(f"  ok    {name}: conforms")
        else:
            failures += 1
            print(f"  FAIL  {name}")
            print(f"          expected: {sorted(expected) or 'nothing'}")
            print(f"          found:    {sorted(actual) or 'nothing'}")
            for item in found:
                print(f"          {item['shape']} on {item['focus']}: {item['message'][:120]}")

    print()
    if failures:
        print(f"{failures} check(s) failed")
        return 1
    print(f"all {len(names)} fixture(s) as expected")
    return 0


if __name__ == "__main__":
    try:
        import rdflib  # noqa: F401
        import pyshacl  # noqa: F401
    except ImportError as exc:
        sys.exit(f"{exc}. Needs rdflib and pyshacl, see the docstring of this file.")
    sys.exit(main())
