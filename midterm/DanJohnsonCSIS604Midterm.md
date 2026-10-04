---
title: "CSIS 604 - Distributed Systems - Midterm"
subtitle: "A Discussion of Controversial Topics in Distributed Systems"
author: "Dan Johnson"
documentClass: article
geometry: margin=1in
linestretch: 2
header-includes:
  - \usepackage{setspace}
  - \usepackage{etoolbox}
  - \AtBeginEnvironment{quote}{\singlespacing}
bibliography: references.bib
csl: https://raw.githubusercontent.com/citation-style-language/styles/master/chicago-notes-bibliography.csl
---

# Midterm

<!--toc:start-->

- [Midterm](#midterm)
  - [1. Robustness of public peer-to-peer systems](#1-robustness-of-public-peer-to-peer-systems)
    - [Prompt](#prompt)
    - [Recommendation](#recommendation)
  - [2. Edge Computing](#2-edge-computing)
    - [Prompt](#prompt-1)
    - [Recommendation](#recommendation-1)
  - [3. Virtual Machines Versus Container Technology](#3-virtual-machines-versus-container-technology)
    - [Prompt](#prompt-2)
  - [References](#references)

<!--toc:end-->

## 1. Robustness of public peer-to-peer systems

### Prompt

> The first wave of public peer-to-peer systems has passed and by now most are operating
> within the boundaries of a single organization. This shift reflects the difficulty in getting public
> peer-to-peer systems secured against, notably Eclipse and Sybil attacks. Nevertheless, there
> are still a number of systems that operate in the open, such as the DHT-based system for so-
> called magnet links (used by, for example, Bittorrent), as well as the Kademlia system.
>
> Understanding the ins and outs of various types of peer-to-peer systems, you are asked to
> advise a new startup on developing a fully decentralized file-sharing system on whether or
> not they should base this system on an existing product. One particular concern they have is
> the robustness against churn, for which they are thinking of using a gossip-based approach
> which are known to quickly converge to specific overlays, yet are vulnerable to attacks.

### Recommendation

Development of a fully decentralized peer-to-peer (P2P) file-sharing system
from scratch is a _monumental_ engineering effort for an established
organization to undertake, let alone a humble startup. For this reason, the startup
should base their infrastructure around a churn-resistant and security-hardened framework like
the [Bamboo DHT](https://www.cs.princeton.edu/courses/archive/fall09/cos518/papers/bamboo).<span hidden="true">[@rhea2004handling]</span>
Bamboo was specifically designed to handle extreme session churn rates that are historically comparable
to real-world P2P file-sharing networks,<span hidden="true">[@rhea2004handling]</span> proving its resilience as the underlying substrate
for public deployments like [OpenDHT](https://conferences.sigcomm.org/sigcomm/2005/paper-RheGod.pdf).<span hidden="true">[@rhea2005opendht]</span>
Leveraging this structurally optimized routing layer allows the startup to focus development resources on
application-layer features while ensuring baseline predictability and hardening the system against routing attacks.

While the startup's inclination to exploit an unstructured, gossip-based approach correctly solves the problem of rapid convergence
while mitigating node churn, this approach introduces severe structural vulnerabilities in open or public environments. Due to the
gossiping protocol's reliance on probabilistic (non-deterministic) neighbor exchanges to maintain topology, implementations that rely on it
inherently lack the formal cryptographic verification constraints required to secure routing state or data stewardship necessary to mitigate
malicious node introduction.<span hidden="true">[@surveyDHTsecurity]</span> Consequently, protocols including the pervasively popular Kademlia
protocol are "still vulnerable to Sybil and Eclipse attacks as nodes can generate their own identifiers".<span hidden="true">[@surveyDHTsecurity, p 47]</span>
Notably, Bamboo mitigates this to an extent by using a hash of the node's IP address as the key,<span hidden="true">[@surveyDHTsecurity, p 48]</span>
e.g. since nodes are disallowed from choosing their own keys under this protocol, a malicious node can not simply spoof a key when joining.

In order to reconcile these adversarial risks to data consistency within a file-sharing context, the architecture must prioritize the Consistency (C) and
Partition Tolerance (P) of the [CAP Theorem](https://dl.acm.org/doi/10.1145/564585.564601) over unconditional Availability (A).<span hidden="true">[@gilbert2002brewer]</span>
While geographically distributed systems routinely sacrifice consistency to maximize throughput, a public file-sharing system can not afford to return unverified
or corrupted data chunks during period of network instability. Using a structured framework like Bamboo allows the implementation the leverage of deterministic routing
paths to safely achieve eventual consistency.<span hidden="true">[@surveyDHTsecurity, p 48]</span> By utilizing Bamboo's fixed, periodic failure recovery
mechanisms along with an explicit cryptographic verification layer - such as validating each data chunk against its immutable hash [much like the venerable Bittorrent](https://www.libtorrent.org/bittorrent.pdf)<span hidden="true">[@norberg2006introduction, p 9]</span> or requiring cryptographic signatures on `put`s - the platform can preserve
strict data integrity even across highly partitioned networks.

<div hidden="true">
\pagebreak
</div>

## 2. Edge Computing

### Prompt

> One of your fellow students is considering setting up a startup for developing an edge-
> computing platform that can be easily connected to a range of cloud-service providers. One
> of the key issues your colleague sees is not only provisioning the basic infrastructure, but also
> a complete set of tools that will automatically manage resource allocation for the
> applications to be allocated to the edge. Many of those applications either currently run on
> edge devices or in the cloud.
>
> Your expert team is aware of the hype around edge-computing systems and notably the
> discussions on the apparent advantages concerning security, performance, etc. You also
> notice that your colleague student may not be aware of the ins and outs and you decide to
> give a substantiated advice on whether or not she should carry on with her ideas, and if so,
> what the main issues are that she should consider to make the startup attractive from an
> end-user's perspective.

### Recommendation

While edge computing architectures offer some compelling advantages for certain applications such as
low latency, location awareness, and reduced WAN bandwidth<span hidden="true">[@edge_computing2019, pp 221-222]</span>,
there are also extensive trade-offs which make these systems a poor fit for other applications. As such, the architectural
complexity of building a cross-provider orchestration platform which automatically manages applications to the edge
ranges from challenging at best to prohibitive at worst. The core impediment to such a business model is the
reality of hardware, software, and API heterogeneity which is the "main challenge in the successful deployment
of Edge computing".<span hidden="true">[@edge_computing2019, p 222]</span> A startup attempting to deploy a
single, universal control plane would likely drown in technical debt due to interoperability limitations.

To mitigate the extreme interoperability tax, the startup should pivot the platform's core architecture towards
a fog computing paradigm.<span hidden="true">[@fog_computing2018]</span> Whereas pure edge models struggle against
a fragmented ocean of heterogeneous client hardware devices, fog computing seamlessly extends cloud services down
to uniform network infrastructure like "edge routers, switches, gateways, and access points, PCs, smartphones, set-top boxes, etc."<span hidden="true">[@fog_computing2018]</span>
While heterogeneity is _still a factor_ in fog computing<span hidden="true">[@fog_computing2018, p 426]</span>, the relative homogeneity of the underlying computing hardware (such as x86 vs ARM architecture), network communication protocols, etc. is orders of magnitude smaller than in the world of edge IoT devices. Shifting the target orchestration plane
to these more-standardized conventional devices eliminates the need to develop multitudes of custom software variations for highly localized, ever-changing devices.
Furthermore, by leveraging pre-existing, virtualized network layers to manage resource allocation, the startup preserves deterministic, scalable execution trees
while silently handling the complexity of state reconciliation underneath.<span hidden="true">[@fog_computing2018]</span>

From the perspective of the end-user, the transition of focus from raw edge hardware provisioning to a managed fog service layer delivers _immediate_ operational value.
Enterprise consumers prioritize distributed deployments to enforce local data sovereignty, maintain privacy boundaries and guarantee offline autonomy during network
failures, not to micromanage heterogeneous physical infrastructure.<span hidden="true">[@edge_computing2019, p 229]</span> Exposing a standardized fog layer as a
secure, predictable application, the startup shields end-users from the underlying complexity of hardware maintenance and network jitter.<span hidden="true">[@edge_computing2019, p 221]</span> Ultimately, treating the platform as a modular, privacy-preserving extension of a customer's pre-existing cloud architecture creates a highly attractive,
low-cost integratin model that directly mitigates enterprise deployment risk.<span hidden="true">[@edge_computing2019, p 230]</span>

<div hidden="true">
\pagebreak
</div>

## 3. Virtual Machines Versus Container Technology

### Prompt

> A small data center that operates for a largely regional, yet functionally wide range set of
> companies, is considering a complete transition to container technology instead of their
> current use of virtual machines. Their main reason is the suspected gain in performance and
> scalability (so they say). Their customers rely on a diverse set of applications, requiring the
> need for supporting office-based operating systems such as Windows, but also a range of
> different Unix machines. So far, the data center has used Debian distributions as their base
> operating system.
>
> Your expert team is more than just knowledgeable when it comes to virtualization and is very
> much aware of the strengths and limitations of containerization. Instead of advising what to
> do, you offer to enhance the awareness around containerization and virtualization so that
> the data center operators can make a founded decision on if, where, and how to apply
> containers. You suspect that in the end, they may need to use both containers and virtual
> machines, side-by-side. Providing the proper requirements for whatever solution they decide
> on, is what you will be offering.

<div hidden="true">
\pagebreak
</div>

## References

<div hidden="true">
::: {#refs}
:::
</div>
