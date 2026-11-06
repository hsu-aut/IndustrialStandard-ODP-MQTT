# MQTT Ontology-Design-Pattern

## Introduction

Applications that monitor, analyze or coordinate distributed devices need to know
how those devices talk to each other. In robotics and manufacturing, a large part
of that traffic is publish/subscribe: a device publishes application messages
under a topic, and other devices subscribe to the topics they are interested in.
The protocol that does this in most systems is MQTT. Describing the communication
means of a system together with the rest of its model — its structure, its
capabilities, its skills — requires the vocabulary of that protocol in the same
schema as everything else.

This repository contains an ontology of MQTT, which is an OASIS standard for a
publish/subscribe messaging transport. We maintain a whole list of
standard-based ontologies, check out these links:
 - [DIN EN 61360](https://github.com/hsu-aut/IndustrialStandard-ODP-DINEN61360)
 - [VDI 2206](https://github.com/hsu-aut/IndustrialStandard-ODP-VDI2206)
 - [VDI 2860](https://github.com/hsu-aut/IndustrialStandard-ODP-VDI2860)
 - [VDI 3682](https://github.com/hsu-aut/IndustrialStandard-ODP-VDI3682)
 - [DIN 8580](https://github.com/hsu-aut/IndustrialStandard-ODP-DIN8580)
 - [ISA 88](https://github.com/hsu-aut/IndustrialStandard-ODP-ISA88)
 - [WADL](https://github.com/hsu-aut/IndustrialStandard-ODP-WADL)
 - [DIN EN 62264-2](https://github.com/hsu-aut/IndustrialStandard-ODP-DINEN62264-2)
 - [OPC UA](https://github.com/hsu-aut/IndustrialStandard-ODP-OPC-UA)
 - [ISO 22400-2](https://github.com/hsu-aut/IndustrialStandard-ODP-ISO22400-2)
 - [IEEE 1872.2](https://github.com/hsu-aut/IndustrialStandard-ODP-IEEE1872-2)
 - [VDI 5100](https://github.com/hsu-aut/IndustrialStandard-ODP-VDI5100)

## MQTT

The ontology follows *MQTT Version 5.0*, OASIS Standard, 07 March 2019 [1]. It
covers four parts of the standard:

- **The normative vocabulary of clause 1.2** — network connection, application
  message, client, server, session, subscription, shared subscription, wildcard
  subscription, topic name, topic filter, control packet, malformed packet,
  protocol error and will message. The fifteenth defined term, the disallowed
  Unicode code points, is a matter of string encoding (1.5.4) and is
  deliberately left out.
- **The packet structure** — fixed header, variable header, payload, properties,
  reason codes, and all fifteen control packet types of clause 2.1.2, declared
  pairwise disjoint.
- **Topics and subscriptions** — topics, topic filters, sessions, subscriptions,
  and the cardinalities that clause 1.2 states for them.
- **Quality of service** — the three levels of clause 4.3 as an enumerated class
  with three individuals, usable both for the QoS of a message and for the
  maximum QoS of a subscription.

Each entity carries an `rdfs:label`, an `rdfs:comment` and a `dcterms:source`
annotation naming the clause of the standard it reflects, so that the claim
"this is MQTT" can be checked at the artefact rather than taken on trust.

### Quality of service

The three levels are individuals of the class `MQTT:QoS`, which is defined as
the enumeration of exactly those three. `MQTT:hasQoS` relates an application
message to its level, `MQTT:hasMaximumQoS` relates a subscription to the maximum
level the server may use for it (3.8.3.1), and `MQTT:qosLevel` gives the numeric
value of a level. The three classes `QoS0Publication`, `QoS1Publication` and
`QoS2Publication` are *defined* over the level of the carried message, so a
reasoner derives the class from the data and the data from the class, and their
pairwise disjointness follows from the model instead of resting on a separate
assertion.

### Four entities that go beyond the standard

MQTT 5.0 does not define a broker address: clause 1.2 explicitly delegates the
transport to "a construct provided by the underlying transport protocol", and
the word *endpoint* appears exactly once in the 137 pages, non-definitionally,
in clause 3.1.4. A model of a concrete system needs the address nevertheless.
The ontology therefore keeps `MQTT:ServerEndpoint`, `MQTT:hasEndpoint`,
`MQTT:endpointUrl` and `MQTT:hasPortNumber`, and marks all four with a
`dcterms:source` annotation saying that they are an extension beyond the
standard. They can be found mechanically:

```sparql
SELECT ?e WHERE {
  ?e <http://purl.org/dc/terms/source> ?src .
  FILTER(STRSTARTS(STR(?src), "Extension beyond"))
}
```

### What is deliberately not modelled

Error handling (4.13), flow control (4.9), the request/response pattern (4.10),
enhanced authentication (4.12), and the subscription options other than maximum
QoS — No Local, Retain As Published, Retain Handling (3.8.3.1). Three
constraints of the standard are string patterns or key constraints and cannot be
expressed in OWL 2; they belong in SHACL and are named here so that nobody
expects a reasoner to catch them:

- wildcards must not appear in a topic name (4.7.1),
- each subscription within a session has a different topic filter (1.2),
- a shared subscription's topic filter starts with `$share/` (4.8.2).

## Versions

| Version | Change |
|---|---|
| **2.0.0** | Quality of service reworked as an enumerated class with three individuals; `hasQoS` and `hasMaximumQoS` added; the three publication classes defined instead of asserted. Cardinalities from clause 1.2 for subscriptions, functional properties where the standard states uniqueness. `MalformedPacket` and `ProtocolError` added, completing the vocabulary of clause 1.2. A label for every entity and a `dcterms:source` clause reference throughout, plus ontology metadata (title, creator, licence, citation, preferred prefix). **Breaking:** the domain of `qosLevel` changed from `owl:Thing` to `MQTT:QoS`, the domain of `hasTopic` from `owl:Thing` to `MQTT:ApplicationMessage`, the domain of `topicAlias` from `MQTT:ApplicationMessage` to `MQTT:Publish`, and the disjointness of `SharedSubscription` and `WildcardSubscription` was **removed** — clause 4.8.2 refutes it, since its own example `$share/consumer1/sport/tennis/+` is a shared subscription with a wildcard. |
| 1.0.0 | First version: taxonomy of the protocol, fifteen control packet types, domains and ranges. |

## Usage

If you want to use this ontology design pattern, the easiest way is to import it
into your ontology via an `owl:imports` statement. Reference a fixed release
version so that future changes cannot surprise you:

```turtle
<http://example.org/my-ontology#> rdf:type owl:Ontology ;
    owl:imports <https://raw.githubusercontent.com/hsu-aut/IndustrialStandard-ODP-MQTT/v2.0.0/mqtt.ttl> .
```

The ontology IRI is `http://www.w3id.org/hsu-aut/MQTT`, version IRIs are of the
form `http://www.w3id.org/hsu-aut/MQTT/2.0.0`. **Note:** unlike the other
patterns in the list above, this one does not have a w3id redirect yet, so those
IRIs do not resolve — use the raw URL above until it does.

Of course you can also clone this repository and import a local copy.

## Checks

The ontology is OWL 2 DL (`robot validate-profile --profile DL`), consistent
under HermiT and free of unsatisfiable classes. The axioms added in 2.0.0 are
backed by reasoner probes, each of them paired with a case that has to fail,
documented in `docs/design/MQTT-2.0.0-conceptualization.md` of the
[CaSkBot](https://github.com/CaSkade-Automation/CaSkBot) repository, where this
pattern is used.

[1] A. Banks, E. Briggs, K. Borgendale, R. Gupta (eds.): *MQTT Version 5.0*.
OASIS Standard, 07 March 2019.
https://docs.oasis-open.org/mqtt/mqtt/v5.0/os/mqtt-v5.0-os.html
