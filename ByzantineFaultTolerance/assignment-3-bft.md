---
title: "Byzantine Fault Tolerance"
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

# The Byzantine Generals Problem and Byzantine Fault Tolerance

## Introduction

The Byzantine Generals Problem is a classic thought experiment involving the fault tolerance of distributed systems. The fundamental actors in the thought experiment are the _generals_, commanders of the armies that are laying siege to an enemy city. These generals must come to consensus through some means to decide whether to attack or retreat and is subject to the passing of messages. Let $G$ be the set of generals, then for $n=|G|$ we suppose that there exists some $T \subseteq G$ of _traitors_, with $m = |T|$. According to the seminal work on the problem, an algorithm that robustly provides a solution to this problem (known as Byzantine Fault Tolerance) must involve $n \geq 3m + 1$ generals.<span hidden="true">[@Lamport1982Byzantine]</span> Lamport et al. constructed such an algorithm, known as _Oral Message_ for up to $m$ traitors, denoted $OM(m)$. While previous demonstrations have shown that $OM(1)$ for $n=4$ provides BFT, subsequent demonstrations have been left to the reader. Thus, a demonstration that $OM(2)$ for $n=7$ is provided below.

## Analysis of $OM(2)$ for $n=7,m=2$

To illustrate the mechanics of $OM(2)$ in a system where $|G|=7$ and $|T|=2$, two distinct scenarios must be considered:

1. The commander $C \in G$ is a traitor ($C \in T$)
2. The commander is loyal ($C \not \in T$)

### Case 1: The Commander Is Loyal

Suppose that the commanding general $C$ is loyal, and broadcasts the initial order $v \in \{ \text{ATTACK}, \text{RETREAT} \}$ to each of the remaining lieutenants in $G \setminus \{C\}$. There are $6$ lieutenants denoted $L_i$ for $1 \leq i \leq 6$ and precisely two of them are traitors.

1. **Initial Broadcast:** $C$ sends order $v$ to each lieutenant $L_i$. Because $C \not \in T$, every lieutenant receives precisely the value $v$ sent by $C$.
2. **Recursion using $OM(1)$**: Each lieutenant $L_i$ sends a message to every other
