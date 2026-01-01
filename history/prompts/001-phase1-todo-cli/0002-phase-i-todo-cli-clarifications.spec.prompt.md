---
id: 0002
title: Phase I Todo CLI Clarifications
stage: spec
date: 2026-01-01
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-phase1-todo-cli
branch: 001-phase1-todo-cli
user: Unknown User
command: /sp.clarify
labels: ["clarify", "spec", "edge-cases", "validation", "phase-1"]
links:
  spec: specs/001-phase1-todo-cli/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/001-phase1-todo-cli/spec.md
tests:
 - N/A (specification clarifications, test scenarios updated in spec)
---

## Prompt

Clarify Phase-1 behavior and edge cases for the Todo CLI application.

Clarify:
- What happens when no todos exist
- ID generation strategy
- Behavior for invalid IDs
- Update vs partial update rules
- Complete vs incomplete toggle behavior
- File missing or corrupted scenarios

Output:
- Clear clarification notes
- Update the Phase-1 spec if needed
- No implementation yet

## Response snapshot

Conducted systematic clarification session addressing all requested areas:

### Questions Asked & Answered (4 total)

1. **File Corruption Recovery**: When `/db/todos.json` is corrupted/unparseable, create timestamped backup (format: `todos.json.backup.YYYY-MM-DD-HHMMSS`), initialize fresh empty list with `next_id: 1`, continue operation

2. **Update Behavior (Partial vs Full)**: Allow partial updates - users can update title only, description only, or both; unchanged fields preserve their current values (not require full replacement)

3. **Status Toggle Mechanism**: Single toggle operation - command flips status regardless of current state (incomplete → complete, complete → incomplete); no separate "mark complete" vs "mark incomplete" commands

4. **Length Limits**: Enforce strict limits with validation - title maximum 500 characters, description maximum 2000 characters; reject input exceeding limits with clear error message stating specific limit violated

### Spec Updates (8 sections modified)

**New Section Added**:
- Clarifications > Session 2026-01-01 (records all Q&A)

**Sections Updated**:
- User Story 1: Added acceptance scenario for length limit validation
- User Story 3: Reframed as "toggle" operation, added scenario for reversibility
- User Story 4: Added scenarios for partial updates (title-only, description-only)
- Edge Cases: Clarified corruption handling and length limit enforcement
- Functional Requirements: Updated FR-006 (partial updates), FR-007 (toggle), added FR-013 (length validation), renumbered FR-015/FR-016
- Key Entities: Added max character lengths to Todo.title (500) and Todo.description (2000)
- CLI Interaction Behavior: Clarified commands 3 (toggle) and 4 (partial updates)
- File-Based Persistence Strategy: Updated Loading Strategy step 4 and Error Handling for JSON Parse Error with backup procedure
- Assumptions: Updated from vague "< 1000 characters" to specific "500 title, 2000 description"

### Areas Already Clear (no questions needed)

- **No todos exist**: Already addressed in FR-014, US2 acceptance scenario 2 ("display message indicating list is empty")
- **ID generation strategy**: Already specified in Data Model (auto-incrementing integer, `next_id` field, IDs never reused, gaps preserved after deletion)
- **Invalid ID behavior**: Already covered in US3, US4, US5 acceptance scenarios (error message: "todo was not found")

### Coverage Summary

| Category | Status |
|----------|--------|
| Functional Scope & Behavior | ✅ Resolved |
| Domain & Data Model | ✅ Resolved |
| Interaction & UX Flow | ✅ Resolved |
| Non-Functional Quality | ✅ Clear |
| Integration & Dependencies | ✅ Clear |
| Edge Cases & Failure Handling | ⚠️ Deferred (2 low-impact) |
| Constraints & Tradeoffs | ✅ Clear |
| Terminology & Consistency | ✅ Clear |
| Completion Signals | ✅ Clear |

**Deferred Edge Cases** (low impact, adequate for Phase I):
- Read-only file/permissions: Addressed in Error Handling section
- Concurrent access: Explicitly out of scope per Assumptions

## Outcome

- ✅ Impact: 4 critical behavioral ambiguities resolved; spec now has concrete, testable requirements for file corruption, updates, status toggles, and length limits
- 🧪 Tests: 17 acceptance scenarios across 5 user stories (added 4 new scenarios for length limits, partial updates, toggle reversibility)
- 📁 Files: Updated specs/001-phase1-todo-cli/spec.md (16 functional requirements, clarified 3 edge cases)
- 🔁 Next prompts: /sp.plan to generate implementation plan with constitution check validation
- 🧠 Reflection: Clarification session successfully eliminated all user-specified ambiguities; partial update and toggle behaviors now match standard todo app UX patterns; backup strategy ensures data safety; length limits prevent performance issues

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Validation checks - PASS (no contradictions, all clarifications integrated, markdown valid, FR numbering corrected)
- Prompt variant (if applicable): N/A (standard clarification workflow)
- Next experiment (smallest change to try): Proceed to /sp.plan to validate that clarified requirements translate cleanly into technical architecture and task breakdown
