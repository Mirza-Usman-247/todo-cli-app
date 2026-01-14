# API Design Skill (Strict Contract Mode)

## Purpose
Generate RESTful APIs that strictly and exactly match the provided endpoint contract.

## Mandatory Rules (Non-Negotiable)

### 1. HTTP Methods
- You MUST match HTTP methods EXACTLY as defined in the contract.
- Do NOT change methods.
- Do NOT infer methods.

### 2. URL Paths
- You MUST match URL paths EXACTLY.
- No renaming.
- No version changes.
- No path normalization.

### 3. Request Schemas
- Implement request schemas EXACTLY as defined.
- Field names, types, required/optional flags must match.
- Do NOT add, remove, or infer fields.

### 4. Response Schemas
- Implement response schemas EXACTLY as defined.
- Match response bodies, status codes, and field structure.
- Do NOT add metadata, wrappers, or extra fields.

### 5. Endpoint Control
- ❌ NO extra endpoints.
- ❌ NO missing endpoints.
- ❌ NO helper, health, debug, or convenience endpoints.

### 6. Framework
- Use **FastAPI** only.
- Use **Pydantic** models for schema validation.
- Use FastAPI decorators exactly matching the contract.

### 7. Behavioral Constraints
- Do NOT improve, optimize, or redesign the API.
- Do NOT guess undocumented behavior.
- Do NOT add convenience features.
- Follow the contract to the letter.