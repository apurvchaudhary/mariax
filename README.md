# mariax==1.0.0

## MariaDB extended helpers focused on Vector support.

Quick start (dev):
1. pip install mariax

### Architecture

                     ┌───────────────────────┐
                     │   Python App          │
                     │(Django / Raw Scripts) │
                     └─────────┬─────────────┘
                               │
                 ┌─────────────▼─────────────┐
                 │       Library Layer       │
                 │       (Mariax)            │
                 └─────────────┬─────────────┘
                               │
               ┌───────────────┴───────────────┐
               │                               │
        ┌──────▼──────┐                 ┌──────▼──────┐
        │ Django ORM  │                 │ SQL/CLI     │
        │ Integration │                 │ Utilities   │
        │ (VectorField│                 │ (DBClient,  │
        │ + Manager)  │                 │ DDL helpers │
        │ + QuerySet) │                 │ query.py)   │
        └──────┬──────┘                 └──────┬──────┘
               │                               │
               │                               │
               ▼                               ▼
        ┌───────────────┐                ┌───────────────┐
        │ Vector Utils  │                │ MariaDB 11.x  │
        │ (serialize /  │<──────────────>│ Vector Column │
        │ deserialize)  │                │ + Vector Index│
        └───────────────┘                └───────────────┘
