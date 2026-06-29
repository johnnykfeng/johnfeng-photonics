# johnfeng-photonics

A Streamlit app with photonics calculators and simulations: unit converters, linewidth tools, plots, ring resonator models, PID locking, and more.

A **React frontend alternative** is also available under `frontend/` with a FastAPI backend in `api/`. It currently implements the About page, Unit Converter, and Linewidth Converter while reusing the same Python calculation library as Streamlit.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) — fast Python package and project manager
- Python **3.12** (uv will install it automatically if needed; see `.python-version`)

## Install uv

**Linux / macOS**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell)**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Verify the install:

```bash
uv --version
```

## Set up the project

Clone the repository and enter the project directory:

```bash
git clone <repository-url>
cd johnfeng-photonics
```

### Create a virtual environment and install dependencies

The project is configured in `pyproject.toml`. Use `uv sync` to create a local `.venv` and install pinned dependencies from `uv.lock`:

```bash
uv sync
```

This will:

1. Download Python 3.12 if it is not already available
2. Create `.venv/` in the project root
3. Install all runtime dependencies

### Alternative: create the venv manually

If you prefer to create the environment yourself before syncing:

```bash
uv venv              # creates .venv with Python 3.12
uv sync              # installs dependencies into .venv
```

To use a specific Python version:

```bash
uv venv --python 3.12
uv sync
```

## Run the app

With the environment set up, start Streamlit via `uv run` (no manual activation required):

```bash
uv run streamlit run streamlit_app/app.py
```

Streamlit prints a local URL (typically `http://localhost:8501`) — open it in your browser.

### Activate the venv manually (optional)

If you want an interactive shell inside the project environment:

```bash
source .venv/bin/activate   # Linux / macOS
# .venv\Scripts\activate    # Windows

streamlit run streamlit_app/app.py
```

## React frontend (alternative)

The React app is a modern UI alternative to Streamlit. It calls a FastAPI backend that imports the same `johnfeng_photonics` library, so conversion results stay consistent with the Streamlit app.

### Prerequisites

- Python **3.12** with [uv](https://docs.astral.sh/uv/) (same as above)
- **Node.js 18+** (Node 20+ recommended) and npm

### Install backend dependencies

Install the optional API extra (FastAPI + Uvicorn):

```bash
uv sync --extra api
```

### Run the API backend

From the project root:

```bash
uv run uvicorn api.main:app --reload --port 8000
```

The API serves endpoints under `/api/` (health check at `/api/health`).

### Run the React frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the URL Vite prints (typically `http://localhost:5173`). The dev server proxies `/api` requests to the backend on port 8000.

### Build the frontend for production

```bash
cd frontend
npm run build
npm run preview
```

## Run tests

```bash
uv run python -m unittest discover -s unit_tests
```

## Updating dependencies

After editing `pyproject.toml`, refresh the lockfile and environment:

```bash
uv lock
uv sync
```

## Project layout

| File / directory | Purpose |
|------------------|---------|
| `streamlit_app/app.py` | Streamlit entry point |
| `streamlit_app/` | Streamlit multipage app scripts |
| `api/` | FastAPI backend for the React frontend |
| `frontend/` | Vite + React + TypeScript + Tailwind SPA |
| `src/johnfeng_photonics/` | Installable library (units, equations, plots, PID modules) |
| `pyproject.toml` | Project metadata and dependencies |
| `uv.lock` | Locked dependency versions |
| `.python-version` | Default Python version for uv |
| `defaults.toml` | App default configuration |
| `unit_tests/` | Unit tests |
