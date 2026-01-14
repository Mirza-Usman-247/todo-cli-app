# Auth Integration (Better Auth) Skill

## Purpose
Secure API endpoints and chat interactions using Better Auth.
Ensure strict user isolation and ownership enforcement.

## Core Rules (MANDATORY)
- Use Better Auth for signup and signin
- Validate Bearer tokens on every protected request
- Extract authenticated `user_id` from Better Auth token
- Enforce ownership checks using `user_id`
- Reject cross-user access

## Where This Skill Applies
- All REST API endpoints
- Chat endpoints
- Any request that reads or mutates user-owned data

## Required Behavior
1. Read Authorization header (Bearer token)
2. Verify token using Better Auth SDK
3. Attach authenticated user context to the request
4. Use `user_id` from token for:
   - Database queries
   - Chat session isolation
   - Resource ownership checks
5. Deny access if:
   - Token is missing or invalid → 401 Unauthorized
   - Resource `user_id` ≠ token `user_id` → 403 Forbidden

## Strict Constraints (DO NOT VIOLATE)
- DO NOT implement a custom authentication system
- DO NOT hard-code users or user IDs
- DO NOT mock authentication in production code
- DO NOT bypass Better Auth validation

## Enforcement Pattern
- Use auth middleware or decorators
- Use ownership checks before returning or mutating data
- Always trust Better Auth as the source of truth

## Critical Behavior
If authentication is required and this skill is not applied:
→ STOP and apply this skill before proceeding.