# agents-template

Plantilla base para construir agentes con **FastAPI**, gestionada con **uv** e integrada con herramientas de calidad de código.

## Requisitos

- Python >= 3.14
- [uv](https://docs.astral.sh/uv/) (gestor de paquetes y entornos)

## Instalación

```bash
uv sync
```

Esto crea el entorno virtual en `.venv/` e instala todas las dependencias (incluyendo las de desarrollo).

## Desarrollo

### Servidor de desarrollo

```bash
uv run fastapi dev
```

Levanta el servidor en `http://127.0.0.1:8000` con recarga automática (hot-reload). La documentación interactiva está disponible en:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Tests

### Ejecutar tests

```bash
uv run pytest -v                      # todos los tests
uv run pytest tests/test_main.py      # solo unitarios
uv run pytest tests/e2e/              # solo e2e
```

### Estructura de tests

```
tests/
├── __init__.py
├── test_main.py          # Unit tests — prueban las funciones directamente
└── e2e/
    ├── __init__.py
    └── test_main.py      # E2E tests — prueban los endpoints HTTP completos
```

Los tests e2e usan `httpx.AsyncClient` con `ASGITransport`, lo que permite lanzar requests HTTP reales contra la app sin necesidad de un servidor externo. Todo el stack de FastAPI (routing, middlewares, serialización) se ejecuta en memoria.

## Herramientas de calidad

### Ruff — Linter y formateador

```bash
# Verificar errores de estilo y linting
uv run ruff check .

# Corregir automáticamente los errores corregibles
uv run ruff check . --fix

# Formatear código
uv run ruff format .
```

Reglas activas (configuradas en `pyproject.toml`): `E`, `F`, `I`, `B`, `UP`  
(errores, pyflakes, imports, bugbear, pyupgrade)

### mypy — Verificación de tipos estáticos

```bash
uv run mypy app/
```

Configurado en modo `strict`: requiere anotaciones de tipo en todas las funciones y prohíbe el uso implícito de `Any`.

## Estructura del proyecto

```
agents-template/
├── app/
│   ├── __init__.py
│   └── main.py        # Entrypoint de FastAPI
├── tests/
│   ├── __init__.py
│   ├── test_main.py   # Unit tests
│   └── e2e/
│       ├── __init__.py
│       └── test_main.py  # E2E tests
├── pyproject.toml     # Configuración del proyecto, dependencias y herramientas
└── README.md
```
