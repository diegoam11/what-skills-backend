## Antes de hacer commit

```bash
# Ordenar imports
isort .

# Formatear el código
black .

## Ejecutar programa
```bash
uvicorn src.main:app --reload
