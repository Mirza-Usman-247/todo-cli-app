# MCP Context7 Guard Skill

The MCP Context7 Guard skill ensures that any code written or modified is based on the latest official documentation available through MCP using Context7.

## Purpose

This skill acts as a safeguard to ensure all code implementations:
- Are based on verified documentation from Context7
- Use official, up-to-date APIs
- Avoid deprecated or speculative features
- Align with documented SDK behavior

## Activation Rules

The skill activates automatically when generating:

- New code
- Modified code
- Implementation-level output (functions, classes, configs, scripts)

The skill does NOT activate during:

- Concept explanations
- Architecture discussions
- Planning or spec writing
- High-level reviews

## Features

- Checks MCP availability
- Verifies Context7 status (enabled and reachable)
- Retrieves latest documentation from Context7
- Validates code against official documentation
- Issues warnings when Context7 is unavailable
- Promotes conservative use of stable APIs when documentation is inaccessible

## Usage

The skill operates automatically when appropriate content types are detected. When Context7 is available, it will:

1. Retrieve the latest relevant documentation
2. Base all code suggestions on verified documentation
3. Validate code against official specifications

When Context7 is not available, the skill will:

1. Issue a warning
2. Proceed conservatively using stable, well-established APIs only
3. Avoid version-specific or recently introduced features

## Constraints

- Never invents undocumented APIs
- Never assumes SDK versions
- Prefers official documentation over blogs or examples
- If documentation conflicts, prefers Context7 data

## Integration

This skill integrates seamlessly into the development workflow and automatically applies its checks when appropriate content types are detected.