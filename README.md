## 1. What This Repository Is

AFW (Applied Firewall / Autonomous Firewall) is a **context-driven academic project** designed to support the Master of Science in Artificial Intelligence (MSAI) as a **shared applied AI system**.

This repository is **not**:

- a finished commercial product
- a cybersecurity certification lab
- a collection of isolated coding assignments

This repository **is**:

- a realistic **end-to-end AI system**
- a **program-level academic project**
- a structured environment to reason about **AI systems, not just models**

AFW exists to help students and faculty explore **how AI systems are designed, justified, evaluated, and governed**.

---

## 2. Start Here (Important)

If this is your first time in this repository:

👉 **Do not start with the code.**

The correct entry sequence is:

1. Understand the **problem being addressed**
2. Understand the **proposed solution**
3. Understand the **system architecture and its rationale**
4. Only then engage with:
    - implementation details
    - academic frameworks
    - assessment artifacts

This order is intentional and required.

---

## 3. The Core Problem

Modern digital systems generate massive volumes of logs:

authentication attempts, access records, application events, and infrastructure signals.

Organizations rarely struggle with collecting logs.

They struggle with:

- identifying meaningful signals
- adding relevant context
- making timely, explainable, and auditable decisions

AFW is built around the following core question:

> How can raw logs be transformed into context-aware, explainable, and auditable decision recommendations using AI?
> 

This question — not any specific tool or algorithm — defines the project.

---

## 4. Conceptual Solution (High Level)

AFW proposes a **layered AI decision pipeline**:

```
Raw Logs
   ↓
Ingestion
   ↓
Parsing & Normalization
   ↓
Context Enrichment (Database)
   ↓
Feature Representation
   ↓
Machine Learning Model
   ↓
Decision Recommendation

```

Key principles:

- context comes **before** modeling
- models are **components**, not the system
- decisions are **recommendations**, not automatic actions
- auditability and explainability are first-class concerns

---

## 5. Repository Structure (Mental Model)

Use the repository as follows:

- `/docs`
    
    → Understand the **problem, solution, and architecture**
    
- `/core`
    
    → See how the system is **implemented**
    
- `/scripts`
    
    → Observe how the system **operates**
    
- `/nexus`
    
    → Understand how learning, capabilities, and evidence are organized
    
- `/assessments`
    
    → Rubrics, exemplars, and evaluation artifacts
    

If you ever feel lost, return to `/docs`.

---

## 6. How AFW Is Used Academically

AFW is **not a single-course project**.

Students will encounter AFW:

- across multiple courses
- at different levels of depth
- with different academic goals

Depending on the course, students may be asked to:

- explain system components
- analyze data or model behavior
- redesign part of the pipeline
- justify architectural decisions
- evaluate ethical and governance implications

Students are **not expected to master the entire system at once**.

---

## 7. Atlantis Nexus Integration

Atlantis Nexus is **not the starting point** of this project.

Nexus is applied **after** students and faculty understand:

- the problem context
- the conceptual solution
- the system architecture

Once integrated, Atlantis Nexus:

- organizes learning progression
- aligns assessment artifacts
- ensures coherence across the MSAI program

AFW becomes a **capability-development system**, not just a technical repository.

---

## 8. Expectations for Students

Students are expected to produce:

- clear explanations
- justified decisions
- analytical comparisons
- ethical and governance reflections

Code is a means.

**Reasoning and academic evidence are the goal.**

---

## 9. Expectations for Faculty

Faculty are expected to:

- use AFW as a shared system, not a fixed assignment
- evaluate reasoning and artifacts, not tool sophistication
- align course objectives with specific system layers or capabilities

AFW supports faculty autonomy while preserving program coherence.

---

## 10. Canonical Status

This README defines the **official academic entrypoint** of the AFW project.

All documentation, learning routes, and Atlantis Nexus mappings are built **on top of this foundation**.

---

### End of README

---