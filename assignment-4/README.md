---
title: "Assignment 4"
subtitle: "CSIS 604 - Distributed Systems"
author: "Dan Johnson"
documentClass: article
geometry: margin=1in
linestretch: 2
indent: true
header-includes:
  - \usepackage{setspace}
  - \usepackage{etoolbox}
  - \usepackage{indentfirst}
  - \AtBeginEnvironment{quote}{\singlespacing}
bibliography: references.bib
csl: https://raw.githubusercontent.com/citation-style-language/styles/master/chicago-notes-bibliography.csl
---

<!--toc:start-->

- [Assignment 4](#assignment-4)
  - [1. Scalability](#1-scalability)
    - [Prompt](#prompt)
    - [Answer](#answer)
  - [2. Clocks](#2-clocks)
    - [Prompt](#prompt-1)
    - [Answer](#answer-1)
  - [3. X vs. Uber](#3-x-vs-uber)
    - [Prompt](#prompt-2)
    - [Answer](#answer-2)
- [References](#references)

<!--toc:end-->

# Assignment 4

## 1. Scalability

### Prompt

> Briefly explain the meaning of scalability in distributed systems, and use
> examples to illustrate different types of scalability.

### Answer

In distributed systems, **_scalability_** can be defined as _a system's ability to accommodate growing workloads or expanded capacity by **adding resources**, without suffering unbounded performance degradation or requiring a comprehensive redesign_. Scalability, and the methods used to achieve it, vary across several main categories. For instance, a system may be scalable with respect to the volume of consumers (users) that simultaneously utilize the system by increasing the number of resources it makes available to those users, an attribute known as **size scalability**.<span hidden>[@distributedSystems, 15-17]</span> Specifically, an online service operating within a cluster may expose several _replicas_ to handle incoming requests, allowing the system to expand its throughput and resilience towards a high volume of incoming requests. Scalability may also refer to the ability of the system to provide uniform functionality across vast distances, often referred to as **geographic scalability**.<span hidden>[@distributedSystems, 15]</span> In many enterprise and government applications, personnel working in field offices interact directly with a front-end application which provides remote procedure calls to services that are hosted hundreds or even thousands of miles away, such as a centralized database in Chicago providing data to nodes in Los Angeles, New York, etc. The primary challenge in implementing geographic scaling is that network communications over vast distances are fundamentally bounded by the speed limit of the universe, namely, the _speed of light_. This means that issues of synchronicity and latency begin to dominate the considerations engineers and architects must face when implementing these systems, leading to design trade-offs like database sharding and the application of CAP theorem. At times, a single system must provide services to multiple distinct organizations across domain boundaries. Such a system's ability to be managed easily is known as **administrative scalability**.<span hidden>[@distributedSystems, 15]</span> To reinforce the concept, consider that a government agency such as the Internal Revenue Service (IRS) must access the same data maintained by the Social Security Administration (SSA). In such a case, it is highly desirable to maintain a database as a _source of ground truth_ for both of these, but this introduces unique design challenges since the domains of these two agencies are vastly different. The ability to scale the system in such a way as to make services available to each of these entities introduces hurdles such as cross-boundary security, access control, and trust.<span hidden>[@distributedSystems, 15]</span> Note that these are but two agencies, where in reality the federal government has many such agencies with overlapping data needs.

While these are the primary architectural dimensions considered in the problem of scalability, the strategies undertaken to achieve this scaling are fundamentally bound by the hardware mechanism chosen to expand capacity, i.e. **vertical (scale-up)** versus **horizontal (scale-out)**. **Vertical scaling** involves enhancing a single node's capacity by upgrading its physical components, e.g. expanding RAM, adding more CPU cores, or adding high-speed persistent storage. This approach is conceptually simpler because it avoids network partitioning and consensus complexity, yet there exist hard physical and economic limits to this form of scaling induced by manufacturing limits, thermal dissipation thresholds, and the exorbitant cost of custom enterprise hardware. Conversely, **horizontal scaling** expands capacity by adding independent commodity servers to a cluster, distributing the workload across many nodes. Though horizontal scaling circumvents single-machine hardware limits, it introduces its own architectural ceilings governed by network latency, state synchronization overhead, and serialization bottlenecks. Consequently, modern distributed systems must carefully architect coordination and consistency models to reap the benefits of horizontal scale-out without succumbing to distributed coordination overhead.

## 2. Clocks

### Prompt

> Briefly explain how vector clock extends the concept of Lamport clock, and
> give each clock an example to show how it works. Particularly, explain why Lamport
> clock doesn’t work for your example of vector clock. (You may refer to Chapter 6.2 of
> the text, use similar figures and/or pseudo code to illustrate. But your examples must
> NOT be identical to the ones in text.)

### Answer

To understand how a vector clock extends a _Lamport_ or _logical_ clock necessitates a discussion about how logical clocks are used to synchronize and coordinate separate processes from first principles. The key concept underpinning logical clocks is the _happens before_ relation, that is for events $a$ and $b$, if $a$ happens before $b$ (denoted $a \to b$), then $a$ _logically precedes_ $b$<span hidden>[@distributedSystems, 311]</span>. Under the implementation of a Lamport clock, when process $P_i$ receives message $m$ with timestamp $ts(m)$, counter $C_i$ is updated to $\text{max}\{C_i, ts(m)\}$, and thus establishes a _total ordering_ of events across all nodes.<span hidden>[@distributedSystems, 311, 317]</span> This is useful in applications that require a high level of consistency in the ordering of events. However, CAP theorem dictates that if availability is prioritized over such consistency in distributed systems where partitioning is inevitable<span hidden>[@capTheorem]</span>, then the emphasis on global consistency offered by logical clocks may fall short. In these situations, a _vector clock_ grants the implementation to track causality,<span hidden>[@distributedSystems, 311]</span> leading to improved availability through concurrent (possibly conflicting) event detection.

In a vector clock, each process $P_i$ maintains not just a counter but a _vector_ of counters $VC_i$, where each counter $VC_i[j]$ indicates the number of events that have occurred at $P_j$ that $P_i$ _knows_ about.<span hidden>[@distributedSystems, 319]</span> When $P_k$ receives message $m$ from process $P_i$, the vector $VC_k[i] \gets \text{max}\{VC_k[i],ts(m)\}$ and since $VC_j$ with $i \neq j \neq k$ is not updated, events happening at $P_j$ can not be _caused by_ the event $m$.<span hidden>[@distributedSystems, 319]</span>

To illustrate the operational difference between these two approaches, consider a distributed NoSQL document store utilizing multiple replica nodes ($P_1$ and $P_2$) to manage a user record. Under a **Lamport clock**, each node maintains a single scalar counter. If Client A updates the user's email on node $P_1$ and, concurrently, Client B updates the user's phone number on node $P_2$, both nodes might increment their scalar counters to the same logical value (e.g., $L = 5$). To resolve this, the system must enforce a _total order_ by applying an arbitrary tie-breaker, such as comparing node identifiers ($P_1 < P_2$). Consequently, the database blindly applies Lamport's total order and **silently overwrites** the update from $P_1$, resulting in permanent data loss (also known as the lost-update problem) because a scalar clock cannot represent concurrency ($a \parallel b$).

In contrast, a **vector clock** prevents this data loss. When the concurrent updates occur, node $P_1$ stamps its write with the vector $VC_1 = [1, 0]$, while node $P_2$ stamps its write with $VC_2 = [0, 1]$. When the replicas eventually synchronize via a gossip protocol, neither vector dominates the other ($[1,0] \not\le [0,1]$ and $[0,1] \not\le [1,0]$). The vector clock algorithm immediately detects a **concurrent conflict ($a \parallel b$)**. Rather than discarding data, the NoSQL engine retains both conflicting versions as sibling values, surfacing them to the application layer for safe conflict resolution (such as CRDT reconciliation<span hidden>[@CRDTs]</span> or client-side merging) and thereby achieving high availability under eventual consistency.

## 3. X vs. Uber

### Prompt

> Use the knowledge you’ve learned to briefly design your own X (formally
> Twitter) and Uber. List as many system concerns and designs/solutions as you can.
> Particularly, explain the differences (with respect to design goals and implementation)
> between your X and Uber distributed systems.

### Answer

X (formerly known as Twitter) is a social media application where users share _short_ posts with their _followers_. Since the goal is to connect geographically dispersed users together in one platform, a high level of _**geographic scalability**_ is a prime design goal here. Because network partitioning becomes increasingly likely along vast distances, an emphasis on _**consistency**_ would come at the cost of _**availability**_ <span hidden>[@capTheorem]</span>. Due to this trade-off, the application emphasizes availability so users can make posts during network partitions by utilizing distributed NoSQL databases, like a document DB for posts and a graph database for social connections. These databases utilize an _**eventual consistency**_ model complete with _**vector clock**_ powered CRDTs <span hidden>[@CRDTs]</span> to handle conflict resolution. These conflicts are relatively rare since users primarily create or edit their own posts, though eventual consistency must still accommodate edge cases, such as a user deleting a post after another user has re-posted (re-tweeted) it.

Uber is a real-time transactional ride-sharing application where riders book rides with nearby drivers. Because the application brokers physical coordination between riders and drivers, a strict view of _**geospatial consistency**_ is required: a driver and rider _must not see out-of-sync states_ while coordinating pick-up locations, and the system must strictly prevent double-booking or ghost rides. At the same time, the application calls for a high level of _**administrative**_ and _**size scalability**_ to operate across different markets with heterogeneous regulatory environments and usage demands. For instance, New York City has vastly differing regulatory requirements and transaction volumes compared to Atlanta. To meet these needs, the underlying platform should use _**geographically sharded**_ transactional database clones operating within regional clusters. This architecture looks more like a federated _system of systems_ rather than the monolithic network topology used by the X clone. Furthermore, because financial transactions and ride assignments demand strict linearizability, this architecture emphasizes **consistency** throughout the network, leveraging distributed consensus protocols (such as Raft or Paxos) and two-phase locking rather than loose logical clocks.

<span hidden>\newpage</span>

# References
