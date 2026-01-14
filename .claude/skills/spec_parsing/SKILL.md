# Spec Parsing Skill

## Purpose
Accurately interpret Spec‑Kit Plus specifications and treat them as the single source of truth for all development activities. This skill ensures that all implementation work is grounded in documented requirements rather than assumptions or improvisation.

## Core Responsibilities
- **Comprehensive Reading**: Read /specs/*.md files in their entirety before beginning any coding tasks to understand the complete context
- **Specification Verification**: Verify that all implemented features are explicitly mentioned in the specifications before implementation
- **Feature Constraint**: Never invent or assume features that are not clearly defined, implicitly suggested, or derivable from the specs
- **Ambiguity Detection**: Identify and flag ambiguous requirements, missing details, or contradictory statements instead of making assumptions
- **Traceability**: Ensure all implementation aligns strictly with the documented specifications and can be traced back to specific sections
- **Validation**: Continuously validate ongoing work against the original specifications

## Applied In
- All project phases (spec, plan, tasks, implementation, testing, review)
- Before any coding begins to ensure proper understanding
- During feature implementation to maintain alignment
- When reviewing code changes to verify spec compliance
- When validating completed work against requirements
- During planning to identify gaps or ambiguities in specs
- When creating tasks to ensure they reflect actual spec requirements

## Constraints
- Specifications always override personal assumptions or interpretations
- Specifications override default behaviors, best practices, or common patterns if they conflict
- All features must be traceable back to specific parts of the specs with references
- No implementation without clear specification reference or explicit user direction
- Default behaviors and common practices must be overridden by spec requirements
- Personal knowledge or experience cannot supersede documented specifications
- Assumptions are not permitted without explicit clarification from user

## Enforcement Mechanisms
- Pause work when encountering ambiguous or unclear requirements
- Request clarification on any interpretation uncertainties
- Cross-reference all proposed implementations with specific spec sections
- Maintain a log of identified ambiguities for user review
- Reject implementation of features not grounded in specifications
- Prioritize spec text over inferred requirements

## Integration Points
- Activates automatically when code implementation is requested
- Integrates with planning phase to validate scope alignment
- Connects with task creation to ensure requirement traceability
- Works with review processes to verify spec compliance