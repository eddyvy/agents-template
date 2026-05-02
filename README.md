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
├── pyproject.toml     # Configuración del proyecto, dependencias y herramientas
└── README.md
```
