# 00 — Problem Context

**AFW: From Logs to Reasoned Decisions**

---

## 1. Why This Problem Matters

Modern digital systems generate continuous streams of logs:
authentication attempts, access records, application events, and infrastructure signals.

These logs are essential for security, reliability, and governance.
However, in most organizations, logs are treated as **records**, not as **decision inputs**.

The result is a widening gap between:

* **Data availability**
  and
* **Decision quality**

AFW exists to explore and address this gap.

---

## 2. The Reality of Log-Based Systems

Most organizations can already:

* collect logs
* store them reliably
* query them when needed

The challenge is **not data collection**.

The challenge is that logs are:

* **High-volume**
* **Low-context**
* **Difficult to interpret in isolation**

A single log entry rarely contains enough information to justify a decision.

---

## 3. Core Challenges

### 3.1 Signal Overload

Logs are generated continuously and at scale.

Security-relevant signals are often buried inside:

* routine activity
* background noise
* repeated benign patterns

Human operators and rule-based systems struggle to consistently identify which events matter **now**.

---

### 3.2 Context Fragmentation

The information required to understand an event is rarely located in one place.

Relevant context may include:

* historical user behavior
* prior authentication attempts
* system usage patterns
* organizational policies

This context often exists in databases or systems that are **not consulted at decision time**.

---

### 3.3 Human Bottlenecks

Many log-based decisions rely on:

* static rules
* manual review
* delayed escalation

This creates:

* slow response times
* inconsistent decisions
* limited scalability

As system complexity grows, purely human-centered workflows do not scale.

---

## 4. Why Rules Alone Are Not Enough

Traditional rule-based approaches:

* require constant maintenance
* assume known patterns
* fail when behavior changes

Rules encode **past assumptions**.

They struggle with:

* novel attack patterns
* subtle anomalies
* evolving system behavior

This does not mean rules are useless —
it means they are **insufficient on their own**.

---

## 5. The Role of AI (and Its Risks)

Machine learning offers the potential to:

* learn from historical data
* generalize across patterns
* assist in prioritization and risk assessment

However, AI introduces new challenges:

* opacity
* bias
* overconfidence
* governance and auditability concerns

An AI system that cannot explain or justify its recommendations
creates a different kind of risk.

---

## 6. The Central Question of AFW

AFW is built around a single guiding question:

> **How can raw logs be transformed into context-aware, explainable, and auditable decision recommendations using AI?**

This question implies several constraints:

* decisions must be traceable
* context must be explicit
* human oversight must be preserved

AFW does **not** assume that automation is always the correct outcome.

---

## 7. What AFW Does *Not* Assume

AFW intentionally avoids several common assumptions:

* That more data automatically leads to better decisions
* That AI should replace human judgment
* That real-time automation is always desirable
* That a single model can solve the entire problem

Instead, AFW treats decision-making as a **reasoning process**, not just an inference step.

---

## 8. Why This Problem Is Academically Valuable

This problem space allows students to engage with:

* real-world data ambiguity
* system-level reasoning
* tradeoffs between accuracy, explainability, and control
* ethical and governance considerations

AFW provides a controlled environment to study **AI as part of a system**, not as an isolated model.

---

## 9. What Comes Next

This document defines **the problem space**.

The next step is to explore:

* the **conceptual solution**
* the **system architecture**
* the **reasoning behind design decisions**

📄 Continue with:
**[01_proposed_solution.md](./01_proposed_solution.md)**

---

### End of Document

---
