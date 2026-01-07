# 01 — Proposed Solution

**AFW: A Context-Aware AI Decision Pipeline**

---

## 1. Purpose of the Proposed Solution

The purpose of AFW is **not** to automate security actions,
but to design a system that can **reason about events** and produce **defensible decision recommendations**.

AFW addresses the problem defined in `00_problem_context.md` by introducing:

* explicit context
* structured reasoning
* controlled use of machine learning
* auditability at every step

The solution is intentionally **layered**, **explainable**, and **human-centered**.

---

## 2. Core Design Idea

At the heart of AFW is a simple principle:

> **No decision should be made based on a raw log alone.**

Every decision recommendation must be supported by:

* normalized event data
* historical and relational context
* explicit features
* a clearly defined reasoning step

Machine learning is used to **assist reasoning**, not replace it.

---

## 3. High-Level Solution Overview

AFW proposes a **context-aware decision pipeline** with the following stages:

1. **Ingestion**
   Raw logs are collected from multiple sources.

2. **Parsing & Normalization**
   Logs are transformed into structured, comparable events.

3. **Context Enrichment**
   Events are augmented with historical, behavioral, and relational data.

4. **Feature Representation**
   Relevant attributes are extracted and organized for analysis.

5. **Machine Learning Evaluation**
   A model evaluates the event within its context.

6. **Decision Recommendation**
   The system produces a reasoned recommendation, not an automatic action.

Each stage adds **meaning**, not just processing.

---

## 4. Why a Layered Approach

AFW deliberately separates concerns across layers.

This allows:

* clear reasoning boundaries
* targeted evaluation of errors
* independent improvement of components
* traceability from input to recommendation

A layered design prevents the system from becoming a **black box**.

---

## 5. Context as a First-Class Concept

Context is the central differentiator of AFW.

Instead of embedding context implicitly inside a model, AFW makes it:

* explicit
* inspectable
* auditable

Examples of context include:

* historical behavior patterns
* frequency of prior events
* relationships between users, systems, and actions

This design ensures that **most reasoning happens before modeling**.

---

## 6. Role of Machine Learning

Machine learning in AFW:

* operates on structured, contextualized features
* provides probabilistic assessment or prioritization
* is evaluated and questioned, not blindly trusted

The model is treated as:

* a component
* a hypothesis generator
* a decision support mechanism

It is **not** treated as the source of truth.

---

## 7. Decision Recommendations, Not Actions

AFW intentionally separates **recommendation** from **execution**.

This allows:

* human oversight
* policy enforcement
* ethical review
* institutional accountability

The system answers:

> *“Based on available information, how should this event be interpreted?”*

It does **not** automatically answer:

> *“What must be done right now?”*

---

## 8. Explainability and Auditability

Every recommendation produced by AFW must be explainable through:

* the original event
* the contextual data used
* the features considered
* the model output
* the decision logic applied

This enables:

* post-hoc analysis
* error investigation
* governance and compliance
* learning from mistakes

---

## 9. What This Solution Does *Not* Claim

AFW does not claim to:

* eliminate false positives
* predict all malicious behavior
* remove the need for human judgment
* provide perfect security outcomes

Instead, it provides a **structured, reasoned approach** to a complex problem.

---

## 10. Why This Solution Is Academically Valuable

This proposed solution allows students to explore:

* system-level AI design
* tradeoffs between automation and control
* limits of machine learning
* ethical and governance considerations

AFW is intentionally designed as a **learning system**, not an optimization contest.

---

## 11. What Comes Next

This document defines **the conceptual solution**.

The next step is to examine:

* **how this solution is implemented**
* **why specific architectural choices were made**

📄 Continue with:
**[02_system_architecture.md](./02_system_architecture.md)**

---

### End of Document