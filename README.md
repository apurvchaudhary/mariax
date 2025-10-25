# mariax

## MariaDB extended helpers focused on Vector support.

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

### TL;DR
* Low-level DB client (client.py)
* Vector utilities (vector.py)
* DDL helpers (ddl.py)
* Raw vector query function (query.py)
* CLI tool for index management (cli.py)
* Django ORM integration (VectorField, VectorManager)
* SQLAlchemy integration (VectorType)

### Installation
```bash
pip install mariax==1.0.0
```

### Example DDL
```python
from mariax.django_integration.fields import VectorField
from mariax.django_integration.managers import VectorManager

class Document(models.Model):
    title = models.CharField(max_length=255)
    embedding = VectorField(dim=768)

    objects = VectorManager()
```

### Example Query
```python
similarity_search(db_client, table="docs", embedding_field="embedding", vector=[...], top_k=5)
# OR
top_docs = Document.objects.similarity_search(query_vector, top_k=5)
```

### Example CLI
```bash
mariax create-index --table docs --name idx_docs_embedding --fields embedding --distance cosine
```