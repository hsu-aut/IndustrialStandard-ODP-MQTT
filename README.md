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

- **The normative vocabulary of clause 1.2**, all fifteen defined terms —
  network connection, application message, client, server, session,
  subscription, shared subscription, wildcard subscription, topic name, topic
  filter, control packet, malformed packet, protocol error, will message, and
  the disallowed Unicode code points.
- **The packet structure** — fixed header, variable header, payload, properties,
  reason codes, and all fifteen control packet types of clause 2.1.2, declared
  pairwise disjoint and annotated with their wire value from Table 2-1. Which
  packet types carry a payload is stated as cardinalities from **Table 2-5**
  (clause 2.3): required for CONNECT, SUBSCRIBE, SUBACK, UNSUBSCRIBE and
  UNSUBACK, optional for PUBLISH, none for the other nine. What is *in* a
  payload is said on the packet, not on the payload: six packet types put six
  different things there.
- **Topics and subscriptions** — topics, topic filters, sessions, subscriptions,
  and the cardinalities that clause 1.2 states for them.
- **Quality of service** — the three levels of clause 4.3 as an enumerated class
  with three individuals, usable both for the QoS of a message and for the
  maximum QoS of a subscription.
- **All 27 protocol properties of Table 2-4** (clause 2.2.2.2), including the
  group that describes what a broker can actually do: maximum QoS, retained
  messages, wildcard subscriptions, shared subscriptions and subscription
  identifiers. A User Property is a class rather than a literal, since 2.2.2.2
  defines it as a name-value pair and allows the same name more than once. Those five are modelled as capabilities of `MQTT:MQTTServer`,
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

### The one entity that goes beyond the standard

MQTT 5.0 does not define a broker address: clause 1.2 explicitly delegates the
transport to "a construct provided by the underlying transport protocol", and
the word *endpoint* appears exactly once in the 137 pages, non-definitionally,
in clause 3.1.4. A model of a concrete system needs the address nevertheless.
The ontology therefore keeps `MQTT:endpointUrl` — a datatype property on
`MQTT:MQTTServer`, range `xsd:anyURI`, deliberately not functional, since a
broker is usually reachable at several URIs — and marks it with a
`dcterms:source` annotation saying that it is an extension beyond the standard.
It can be found mechanically:

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

## Constraints that OWL cannot express

Four statements of the standard are normative and mechanically checkable, but
they are not axioms: three constrain the characters of a string and one is a key
constraint over a pair of individuals. They live in `constraints/mqtt-shapes.ttl`
as SHACL shapes, so that a model can be checked against them instead of being
trusted:

| Constraint | Clause | Shape |
|---|---|---|
| Wildcards must not appear in a topic name | 4.7.1, [MQTT-4.7.0-1] | `TopicNameNoWildcards` — which since 6.0.0 also covers the response topic of 3.3.2.3.5 and the will topic, because both are a `MQTT:Topic` |
| Each subscription within a session has a different topic filter | 1.2 | `SubscriptionsShareAFilterNode`, `SubscriptionsShareAFilterString` |
| A shared subscription's topic filter has the form `$share/{ShareName}/{filter}` | 4.8.2, [MQTT-4.8.2-1], [MQTT-4.8.2-2] | `SharedSubscriptionFilterPrefix` |
| A reason code appears only in the packet types Table 2-6 lists for it | 2.4 | `ReasonCodeNotAllowedInPacketType` |

These are conditions of the *standard*, not of any model that reuses this
pattern, which is why they ship with it. Validate your data **together with**
`mqtt.ttl`: the reason code shape reads the ontology's own `appliesToPacket`
annotations and the class hierarchy of the control packets, and finds nothing
without them.

```sh
python tools/check_shapes.py        # needs rdflib and pyshacl
```

The script checks every shape twice over — against `tests/fixtures/valid.ttl`,
which has to pass, and against one fixture per shape built to break exactly that
shape. A shape that never fires would prove nothing, so the expected result is
not "no violations" but a named set of them.

One thing the shapes deliberately do not do: a subscription that is *not* typed
`MQTT:SharedSubscription` but carries a `$share/` filter goes unreported. The
`$share/` prefix marks a filter as shared (4.8.2), so such a model is probably
wrong — but the standard words the rule in one direction only, and reporting the
other direction would amount to classifying the subscription rather than
checking it.

## Versions

| Version | Change |
|---|---|
| **6.0.0** | The packet structure gets teeth, and three shapes are made consistent. **Table 2-5** (clause 2.3) is now in the ontology: `hasPayload` is functional, since clause 2.1 gives a packet at most one payload, the five packet types that require one carry a minimum cardinality, and the nine that must not have one carry `max 0` — a PINGREQ with a payload was permitted up to 5.0.0 and is an error now. The wire value of a packet type moves from a datatype property on the fixed header to the annotation `packetTypeValue` **on the class** (Table 2-1), and `flags` is **removed**: clause 2.1.3 describes it as the byte that holds DUP, QoS and RETAIN, all three of which are modelled separately. `payloadFormatIndicator` becomes the enumerated class `PayloadFormat` with two individuals, since 3.3.2.3.2 lists exactly two values — the construction QoS and Retain Handling already had. `responseTopic` becomes `hasResponseTopic` with range `MQTT:Topic`: a response topic *is* a topic name, and the SHACL layer needs one shape for the wildcard prohibition instead of two. `subscribesTo` and `connectsTo` are **derived** from property chains instead of asserted, so the convenient edge and the long path through session and subscription can no longer disagree; `publishesTo` stays asserted, because deriving it would need a sender and a network connection carries both directions — Table 2-1 gives PUBLISH as "Client to Server or Server to Client". `MalformedPacket` and `ProtocolError` point at reason codes 0x81 and 0x82 with `rdfs:seeAlso`. |
| **5.0.0** | Three shapes corrected where a class, a literal or a datatype was the wrong instrument. `clientId` moves to `MQTT:MQTTClient`, functional, with `owl:hasKey` for clause 3.1.3.1 ("Each Client connecting to the Server has a unique ClientID"); the class `ClientIdentifier` and `hasClientIdentifier` are **removed** — the ClientID assigned by the server was a plain literal next to them. A **User Property is now a class** `UserProperty` with `propertyName` and `propertyValue`, exactly one each, reached through `hasUserProperty`: clause 2.2.2.2 calls it a UTF-8 **String Pair** and allows the same name to appear more than once, which a single `xsd:string` could express neither of. `password` becomes `xsd:base64Binary`, because 3.1.3.6 says "The Password field is Binary Data" — MQTT 5.0 changed that from 3.1.1 and the ontology had not followed. **Breaking fix:** the domain of `serverReference` moves from `Connack` to `MQTTProperty`; with `Connack` a DISCONNECT carrying a Server Reference (3.14.2.2.5, 4.11) made a model **inconsistent**, since the fifteen packet types are pairwise disjoint. The division behind `MQTTProperty` is now written into its comment: the properties of Table 2-4 that appear in several packet types and have no carrier of their own live there, the other twenty live on the entity they are about. |
| **4.0.0** | The server address is flat. `MQTT:endpointUrl` moves to `MQTT:MQTTServer`; the class `ServerEndpoint`, the property `hasEndpoint` and the property `hasPortNumber` are **removed**. Scheme and port are part of the URI and are no longer stated twice — the old form allowed a port in the URI and a `hasPortNumber` to contradict each other, with nothing able to detect it. The flat form is the one the sibling pattern WADL uses for `hasBase`. The difference to OPC UA is deliberate: there an `EndpointDescription` is a structure of the standard itself (Part 4) carrying security mode, policy and identity tokens, whereas MQTT 5.0 defines no endpoint structure at all. |
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
    owl:imports <https://raw.githubusercontent.com/hsu-aut/IndustrialStandard-ODP-MQTT/v6.0.0/mqtt.ttl> .
```

The ontology IRI is `http://www.w3id.org/hsu-aut/MQTT`, version IRIs are of the
form `http://www.w3id.org/hsu-aut/MQTT/6.0.0`. **Note:** unlike the other
patterns in the list above, this one does not have a w3id redirect yet, so those
IRIs do not resolve — use the raw URL above until it does.

Of course you can also clone this repository and import a local copy.

## Checks

The ontology is OWL 2 DL (`robot validate-profile --profile DL`), consistent
under HermiT and free of unsatisfiable classes. The shapes are checked with
`tools/check_shapes.py`, including the control that `mqtt.ttl` on its own — 51
individuals, among them all 45 reason codes — does not trip over its own shapes.
The axioms added since 1.0.0 are
backed by twenty-four reasoner probes, among them a case that has to fail, a probe
showing that the new minimum cardinalities do not invalidate existing data, and
two showing that disjointness which used to be asserted is now derived,
documented in `docs/design/MQTT-2.0.0-conceptualization.md` of the
[CaSkBot](https://github.com/CaSkade-Automation/CaSkBot) repository, where this
pattern is used.

[1] A. Banks, E. Briggs, K. Borgendale, R. Gupta (eds.): *MQTT Version 5.0*.
OASIS Standard, 07 March 2019.
https://docs.oasis-open.org/mqtt/mqtt/v5.0/os/mqtt-v5.0-os.html
