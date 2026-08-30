# Chapter 2 - Architecture

---

## Introduction

Distributed systems are often complex pieces of software of which the components
are by definition dispersed across multiple machines. To master their complexity,
it is crucial that these systems are properly organized.  There are different ways
to view the organization of a distributed system, and we focus on two specific ways
to do this.

- **Software Architecture** describes the intended interaction and organization of the
software components of a distributed system.
  - **Middleware** exists to separate the applications from the underlying platforms
  - Engineering trade-offs must be made to achieve transparency while allowing application
  utility.
  - **System Architecture** is the final instantiation of **software architecture**

The focus of this chapter will be **centralized architectures** where the server
implements most or all of the software components and functionality while remote
clients access the server (server-client architectures) and **decentralized** or
**peer-to-peer (P2P)** architectures in which each vertex in the graph is of an
equivalent class.  We will also include examples of real-world **hybrid architectures**.

---

## 2.1 Architectural Styles

**Def: _Software Architecture_**: the logical organization of a distributed system
into software components

**Def: _Architectural Style_**: the way that software components are connected to each
other, how they exchange data, and how they are configured into a system

**Component**: A modular unit with well-defined required and provided **interfaces**
such that it is _replaceable_ within its environment.

- _replacement_ must be able to occur while the rest of the system runs
- **interfaces** must not change
- It is often impossible to shut down the system for maintenance

**Connector**: a mechanism that mediates communication, coordination, or cooperation
among components

### Key Architectural Styles

- Layered Architectures
- Object-based architectures
- Resource-centered architectures (see [CRUD Operations](#crud-operations))
- Event-based architectures

In the real world, many different architectural styles are combined, and notably, almost
all feature some level or layering between logical levels.

### Layered Architectures

- Components are organized in a **layered fashion** where a component at $L_j$ makes a
**downcall** (a form of **request**) to a lower layer $L_i$ with $i \lt j$ and expects
some form of **response** (_often, we consider the request response architecture architecture a
**polymorph** analagous to call-stacks, so layering can be thought of as a message between layers
of the callstack_).
- Only in exceptional cases will components make an **upcall** (a request directed to a higher layer)

In applications that handle networking communications, a pure **downcall** or **request/response**
organization is generally used.  In the writers experience, the server in the client/server
architecture is generally subdivided into layers in the case of CRUD applications where the
provider layer deciphers inbound requests (often termed something like a `ProviderRequest`)
to send a downcall `DomainRequest` into the **domain layer** which further deciphers and
translates request information to the **Data Access Layer** which generally interfaces with
a database. Responses are then converted between layers back to the caller.

There are situations where we encounter a **Mixed Layer Organization**.  For instance,
consider an application $A$ that makes use of a library $L_{OS}$ which exposes the interfaces
with an operating system (often in the form of a `syscall`).  The same application $A$ may simultaneously
use a mathematical library $L_{math}$ which also uses $L_{OS}$. In this case, we may find that the layers
form a **directed acyclic graph** of calls as they both depend on $L_{OS}$.

Finally, a special situation occurs when a layer makes an **upcall**.  Here, we lose the acyclic nature
of the request graph, due to the cycle introduced by an upcall. An example of these situations arises
when the operating system signals the occurrence of an event to which end it calls a user-defined operation
(**callback** or **handle**) which the caller had previously provided as a reference.

### Layered Communication Protocols

A well-known and ubiquitously applied layered architecture is that of so-called _communication-protocol stacks_.
In each of these stacks, each layer implements one or several **communcation services** allowing data to be sent
from a destination to one of several targets, i.e. each layer offers an interface specifying the functions to be
called as well as the parameters necessary to enforce the interface's **contract**.  These **interfaces** generally
must hide the _implementation details_ which are generally based on a **communication protocol** (a description
of the set of rules parties will follow or **contract** governing the communication between the parties).

> [!IMPORTANT]
> A distinction must be made between
>
> - The _service_ offered by a particular layer
> - the _interface_ by which the service is made available
> - The _protocol_ that layer implements to establish communication

#### Protocol Example

**Transmission Control Protocol (TCP)** specifies which messages are to be exchanged for _setting up_ or
_tearing down_ (creation or destruction) of a connection between two peers.

This is different than UDP in the fact that it deals with exactly two parties meant to exchange limited information,
sometimes with transport layer encryption.

The protocol governs

- messaging
- ordering and transfer of data
- the correction of data lost during transmission

#### Service Example

The service is made available in the form of a relatively simple programming interface
which contains calls to set up a connection, send and receive messages, and to tear down the connections again.
Check out the [server](../python-workspace/client-server/server.py) and [client](../python-workspace/client-server/client.py) code examples

### Application Layering

Three logical levels as referred to above

1. The application interface layer (Provider layer)
2. The processing level (Service or Domain layer)
3. The data layer (Data Access Layer)

### Object-based and service-oriented architectures

**Object-based architectures** are a more loose architectural style.  Each object corresponds
to a component, and these components are connected through a _procedure call mechanism_.  
In the case of distributed systems, the procedure called does not need to take place
on the same object that calls it (such as in RPC).

Object based architectures are attractive for the same reasons that OOP is often an attractive
design paradigm: the architecture provides a mechanism for _encapsulating_ data or state.

As compared to the layered architectural style, which mostly resembles the functional programming
paradigm, this architectural style has the state live within the host object which operates on it
via its _methods_.  The **interface** provided by an object conceals the implementation details,
and thus we consider the object completely independent of its environment. As with components,
this means that the interface's contract is adequately defined to the extent that the object
is modular and replaceable.

The organization of multiple objects together in a graph is often referred to as a **distributed object**
or **remote object**.  

When a client **binds** to a distributed object, and implementation of the objects interface (**proxy**)
is then loaded into the client's address space.  A proxy is analogous to a client stub in RPC systems.
It's sole task is to marshal method invocations into messages and unmarshal reply messages.  (a thin interface)
This thin interface is often referred to as a **skeleton** and serves as the bare means of letting the Middleware
access user-defined objects.  In practice, it often contains incomplete code that the developer must further
specialize to meet their needs.

Most often, (and counterintuitively so), the **state** of a distributed object is **_not distributed_**, rather
it resides on a single machine.  The interfaces may live on the other machines, and these are what we call
**remote objects**.

**Encapsulation**: the attribute of an object that is realized as a _self-contained_ entity.

Clearly separating the various services such that they can operate independently allows
for the existence of **service-oriented architectures (SOAs)**.

We can see through this architecture that a central component of developing a distributed system
is to solve the problem of _service composition_ and orchestration.

### Resource-based Architectures

This is where we get into my dear friend, **Representational State Transfer (REST)**.

There are four key characteristics of what are known as **RESTful Architectures**:

1. Resources are identified through a single naming scheme (**namespace consistency**)
2. All services offer the same interface, consisting of at most four operations ([**CRUD operations**](#crud-operations)) [^1]
3. Requests to and responses from a service are _self-descriptive_. (**self-documenting**)
4. A service _forgets_ or simply _does not permanently store_ information about the caller ([**stateles execution**](#stateless-execution))

#### <span id="crud-operations">The four main CRUD REST operations</span>

| **Operation** | **Description** |
| --- | --- |
| `PUT` | Modify a resource by transferring a new state |
| `POST` | Create a new resource |
| `GET` | Retrieve the state of a resource in some representation |
| `DELETE` | Delete a resource |

[^1]: I really disagree with it being exactly 4, `PATCH` and _upsert_ have different semantic meanings but are sub-categories of the update operations

An example of RESTful is Amazon's **Simple Storage Service (Amazon S3)**.  S3 defines
two resources _objects_(files) and _buckets_(directories).  Buckets can not be moved
recursively into other buckets, and the URI (uniform resource identifier) serves as
the interface to move a file into a bucket.  As an example in the book, they provide
that an object named `ObjectName` contained in the bucket named `Bucketname` is referred
to by the uri `http://s3.amazonaws.com/BucketName/Objectname`
