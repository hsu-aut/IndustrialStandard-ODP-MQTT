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
covers the whole normative vocabulary of the standard:

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
- **All 27 protocol properties of Table 2-4** (clause 2.2.2.2), including the
  group that describes what a broker can actually do: maximum QoS, retained
  messages, wildcard subscriptions, shared subscriptions and subscription
  identifiers. Those five are modelled as capabilities of `MQTT:MQTTServer`,
  because that is how the standard words them — "this byte declares whether the
  *Server* supports …" — even though it transports them in the CONNACK packet.
- **All 45 reason codes of Table 2-6** (clause 2.4) as individuals of an
  enumerated class, with the two subclasses `SuccessReasonCode` and
  `ErrorReasonCode` defined over the value, since clause 2.4 draws the line at
  0x80. Note that a value does not identify a reason code: 0x00 is *Success*,
  *Normal disconnection* and *Granted QoS 0*, depending on the packet. Which
  packets a code may appear in is recorded with the `appliesToPacket`
  annotation.

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

**Behaviour.** This pattern describes the vocabulary of MQTT, not its dynamics.
Flow control (4.9) introduces no term of its own — `receiveMaximum`,
`maximumPacketSize` and the reason codes 0x93 and 0x95 are all here; what 4.9
adds is a rule about how many messages may be in flight. Enhanced
authentication (4.12) is the same: the AUTH packet, the authentication method
and data, and the reason codes 0x18, 0x19 and 0x8C are present, but the
*sequence* of CONNECT, AUTH exchange and CONNACK is not. A vocabulary ontology
is the wrong instrument for a protocol flow; a state machine or process pattern
is the right one.

Four
constraints of the standard are string patterns or key constraints and cannot be
expressed in OWL 2; they belong in SHACL and are named here so that nobody
expects a reasoner to catch them:

- wildcards must not appear in a topic name (4.7.1),
- each subscription within a session has a different topic filter (1.2),
- a shared subscription's topic filter starts with `$share/` (4.8.2),
- a reason code appears only in the packet types Table 2-6 lists for it (2.4) —
  recorded as an annotation here, not as an axiom.

## Versions

| Version | Change |
|---|---|
| **3.0.0** | All 45 reason codes of Table 2-6 as individuals of an enumerated class `ReasonCode`, parsed from the standard's own table rather than transcribed. `SuccessReasonCode` and `ErrorReasonCode` defined over the value (clause 2.4 draws the line at 0x80), so membership is derived: 35 error codes, 10 success codes. `hasReasonCode` relates a packet to its code, restricted to at most one on the seven packets that carry a single code, unrestricted on SUBACK and UNSUBACK which carry a list. `grantsQoS` links the three *Granted QoS* codes to the QoS levels. `appliesToPacket` records the packet types per code. **Breaking:** `reasonCode` is renamed to `reasonCodeValue` and its domain moves from `MQTTControlPacket` to `ReasonCode` — the value belongs to the code, the code to the packet. Keeping both would have been the same mistake that the QoS rework fixed in 2.0.0. |
| **2.1.0** | Completeness pass against Table 2-4 of clause 2.2.2.2: the ten missing protocol properties added, so all 27 are covered. The five server capability properties (maximum QoS, retain, wildcard subscriptions, subscription identifiers, shared subscriptions) are modelled on `MQTTServer`. The remaining subscription options added: `noLocal`, `retainAsPublished`, and `RetainHandling` as an enumerated class with three individuals. `hasRequestedTopicFilter` on SUBSCRIBE and `hasRevokedTopicFilter` on UNSUBSCRIBE, each with a minimum cardinality of one, so that the packet side of subscribing reaches its filters at all. `isSessionOfClient` and `isSessionOnServer`, because a session outlives the network connection (1.2) and was previously reachable only through one. `cleanStart`, `willRetain`, and `DisallowedUnicodeCodePoint`, the fifteenth term of clause 1.2. Additive only — no axiom removed, no domain narrowed. |
| **2.0.0** | Quality of service reworked as an enumerated class with three individuals; `hasQoS` and `hasMaximumQoS` added; the three publication classes defined instead of asserted. Cardinalities from clause 1.2 for subscriptions, functional properties where the standard states uniqueness. `MalformedPacket` and `ProtocolError` added, completing the vocabulary of clause 1.2. A label for every entity and a `dcterms:source` clause reference throughout, plus ontology metadata (title, creator, licence, citation, preferred prefix). **Breaking:** the domain of `qosLevel` changed from `owl:Thing` to `MQTT:QoS`, the domain of `hasTopic` from `owl:Thing` to `MQTT:ApplicationMessage`, the domain of `topicAlias` from `MQTT:ApplicationMessage` to `MQTT:Publish`, and the disjointness of `SharedSubscription` and `WildcardSubscription` was **removed** — clause 4.8.2 refutes it, since its own example `$share/consumer1/sport/tennis/+` is a shared subscription with a wildcard. |
| 1.0.0 | First version: taxonomy of the protocol, fifteen control packet types, domains and ranges. |

## Usage

If you want to use this ontology design pattern, the easiest way is to import it
into your ontology via an `owl:imports` statement. Reference a fixed release
version so that future changes cannot surprise you:

```turtle
<http://example.org/my-ontology#> rdf:type owl:Ontology ;
    owl:imports <https://raw.githubusercontent.com/hsu-aut/IndustrialStandard-ODP-MQTT/v3.0.0/mqtt.ttl> .
```

The ontology IRI is `http://www.w3id.org/hsu-aut/MQTT`, version IRIs are of the
form `http://www.w3id.org/hsu-aut/MQTT/3.0.0`. **Note:** unlike the other
patterns in the list above, this one does not have a w3id redirect yet, so those
IRIs do not resolve — use the raw URL above until it does.

Of course you can also clone this repository and import a local copy.

## Checks

The ontology is OWL 2 DL (`robot validate-profile --profile DL`), consistent
under HermiT and free of unsatisfiable classes. The axioms added since 1.0.0 are
backed by thirteen reasoner probes, among them a case that has to fail, a probe
showing that the new minimum cardinalities do not invalidate existing data, and
two showing that disjointness which used to be asserted is now derived,
documented in `docs/design/MQTT-2.0.0-conceptualization.md` of the
[CaSkBot](https://github.com/CaSkade-Automation/CaSkBot) repository, where this
pattern is used.

[1] A. Banks, E. Briggs, K. Borgendale, R. Gupta (eds.): *MQTT Version 5.0*.
OASIS Standard, 07 March 2019.
https://docs.oasis-open.org/mqtt/mqtt/v5.0/os/mqtt-v5.0-os.html
