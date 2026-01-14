# MCP Context7 Guard Skill

## Description
Ensures that any code written or modified is based on the latest official documentation available through MCP using Context7.

## Activation Rules
- Activate this behavior ONLY when:
  - Writing new code
  - Modifying existing code
  - Generating implementation-level output (functions, classes, configs, scripts)
- Do NOT activate during:
  - Concept explanations
  - Architecture discussions
  - Planning or spec writing
  - High-level reviews

## Behavior
1. Check whether MCP is available
2. Check whether Context7 is enabled and reachable
3. Attempt to retrieve the latest relevant documentation from Context7
4. Base all code strictly on verified documentation

## Constraints
- Never invent undocumented APIs
- Never assume SDK versions
- Prefer official documentation over blogs or examples
- If documentation conflicts, prefer Context7 data