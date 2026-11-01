# Class 7

---

## Naming

### Essence

Names are used to denote entities in a distributed system. To operate on an entity, we need to access it at an **access point**. Access points are entities that are named by means of an **address**.

### Note

A **location-independent** name for an entity $E$, is independent of the addresses of the access points offered by $E$.

## Identifiers

### Pure Name

A name that has no meaning at all; it is just a random string. Pure names can be used for comparison only.

### Identifier: A name having some specific properties

1. An identifier refers to at most one entity.
2. Each entity is referred to by at most one identifier.
3. An identifier always refers to the same entity (i.e. it is never reused).

### Observation

An identifier need not necessarily be a pure name, i.e. it may have content.

- URL's with query strings
- File path

## Broadcasting

### Broadcast the ID, requesting the entity to return its current address

- Can never scale beyond local-area-networks
- Requires all proceses to listen to incoming location requests

### Address Resolution Protocol (ARP)

To Find out which MAC address is associated with an IP address, boradcast the query "who has this IP address"?
-> Basically a **query** to the network

## Forwarding Pointers

### When an entity moves, it leaves behind a pointer to its next location

- Dereferencing can be made entirely transparent to clients by simply following the chain of pointers
- Update a client's reference when present location is found
- Geographical scalability problems (for which separate chaoin reduction mechanisms are needed)

## Home Based Approaches

### Single-tier scheme

## Hierarchichal Loccation Services (HLS)

### Basic idea

Build a large-scale search tree for which the underlying network is divided into hierarchical domains. Each domain is represented by a separate directory node.

### Principle

## HLS: Tree organization

### Invariants

- Address of entity $E$ is stored in a leaf or intermediate node
- Intermediate nodes contain a pointer to a child if and only if the subtree rooted

## Security if flat naming

### Basics

Without special measures, we need to trust that the name-resolution process to return what is associated with a flat name. Two approaches to follow:

- Secure the identifier-to-entity association
- Secure the name-resolution process

### Self-certifying names

Use a value derived from the associated entity and make it (part of) the flat name:

- $id(e) = h(d(e))$ or if we want to be fancy $\text{id}(e) = h \circ d (e)$

## Name Space

### Naming Graph

A graph in which a _leaf node_ represents a _named entity_
