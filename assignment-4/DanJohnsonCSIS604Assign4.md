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

# Assignment 4

## 1. Scalability

### Prompt

> Briefly explain the meaning of scalability in distributed systems, and use
> examples to illustrate different types of scalability.

### Answer

In distributed systems, **_scalability_** can be defined as _a system's ability to accommodate growing workloads or expanded capacity by **adding resources**, without suffering unbounded performance degradation or requiring a comprehensive redesign_. Scalability, and the methods used to achieve it, vary across several main categories. For instance, a system may be scalable with respect to the volume of consumers (users) that simultaneously utilize the system by increasing the number of resources it makes available to those users, an attribute known as **size scalability**.<span hidden>[@distributedSystems, 15-17]</span> Specifically, an online service operating within a cluster may expose several _replicas_ to handle incoming requests, allowing the system to expand its throughput and resilience towards a high volume of incoming requests. Scalability may also refer to the ability of the system to provide uniform functionality across vast distances, often referred to as **geographic scalability**.<span hidden>[@distributedSystems, 15]</span> In many enterprise and government applications, personnel working in field offices interact directly with a front-end application which provides remote procedure calls to services that are hosted hundreds or even thousands of miles away, such as a centralized database in Chicago providing data to nodes in Los Angeles, New York, etc. The primary challenge in implementing geographic scaling is that network communications over vast distances are fundamentally bounded by the speed limit of the universe, namely, the _speed of light_. This means that issues of synchronicity and latency begin to dominate the considerations engineers and architects must face when implementing these systems, leading to design trade-offs like database sharding and the application of CAP theorem. At times, a single system must provide services to multiple distinct organizations across domain boundaries. Such a system's ability to be managed easily is known as **administrative scalability**.<span hidden>[@distributedSystems, 15]</span> To reinforce the concept, consider that a government agency such as the Internal Revenue Service (IRS) must access the same data maintained by the Social Security Administration (SSA). In such a case, it is highly desirable to maintain a database as a _source of ground truth_ for both of these, but this introduces unique design challenges since the domains of these two agencies are vastly different. The ability to scale the system in such a way as to make services available to each of these entities introduces hurdles such as cross-boundary security, access control, and trust.<span hidden>[@distributedSystems, 15]</span> Note that these are but two agencies, where in reality the federal government has many such agencies with overlapping data needs.

While these are the primary architectural dimensions considered in the problem of scalability, the strategies undertaken to achieve this scaling are fundamentally bound by the hardware mechanism chosen to expand capacity, i.e. **vertical (scale-up)** versus **horizontal (scale-out)**. **Vertical scaling** involves enhancing a single node's capacity by upgrading its physical components, e.g. expanding RAM, adding more CPU cores, or adding high-speed persistent storage. This approach is conceptually simpler because it avoids network partitioning and consensus complexity, yet there exist hard physical and economic limits to this form of scaling induced by manufacturing limits, thermal dissipation thresholds, and the exorbitant cost of custom enterprise hardware. Conversely, **horizontal scaling** expands capacity by adding independent commodity servers to a cluster, distributing the workload across many nodes. Though horizontal scaling circumvents single-machine hardware limits, it introduces its own architectural ceilings governed by network latency, state synchronization overhead, and serialization bottlenecks. Consequently, modern distributed systems must carefully architect coordination and consistency models to reap the benefits of horizontal scale-out without succumbing to distributed coordination overhead.

<span hidden>\newpage</span>

# References
