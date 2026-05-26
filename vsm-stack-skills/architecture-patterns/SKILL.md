# Architecture Patterns

Universal system design and architecture principles.

## Design Document Structure
1. Problem statement
2. Data model (immutable once agreed)
3. API specification
4. Architecture diagram
5. Technology choices with rationale
6. Out of scope list
7. Success criteria

## Data Modeling
- Start with entities and relationships, not tables
- Use domain language, not technical jargon
- Every field must have a purpose

## API Design
- REST: nouns not verbs, plural resources, consistent pagination
- GraphQL: types first, resolver responsibility clear, mutation naming convention
- Versioning strategy from day one

## Technology Selection
- Option A (Minimal), B (Balanced), C (Robust) with tradeoffs
- Estimated build time, operational complexity, scalability ceiling, key risks
- S5 selects; architect does not decide
