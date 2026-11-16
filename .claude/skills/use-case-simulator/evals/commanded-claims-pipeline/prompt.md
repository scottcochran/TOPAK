---
tags: [skill-creator]
max_turns: 150
timeout_seconds: 3600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

An insurance claims triage pipeline. An intake agent reads a claim, a fraud-check agent scores it, and a human adjuster must approve any payout over $5,000; smaller payouts go out automatically. Generate the deployment for this and simulate a day of claims, including some attacks. Capture it for replay. Don't commit anything.
