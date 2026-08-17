# Shared types and schemas for TekTribe Trainer

This directory contains TypeScript interfaces and Python Pydantic models that are mirrored between frontend and backend. This ensures type safety across the API boundary.

## Structure

- `types/` — TypeScript interfaces (mirrored from Pydantic models)
- `schemas/` — JSON Schema definitions for API validation

## Usage

Import shared types in the frontend:
```typescript
import type { Companion } from '@shared/types/companion'
```

The backend uses Pydantic models in `backend/app/models/` that match these interfaces.
