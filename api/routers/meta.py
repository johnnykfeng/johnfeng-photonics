import tomllib
from pathlib import Path

from fastapi import APIRouter

from api.schemas import DefaultsResponse, EquationsSourceResponse

router = APIRouter(prefix="/meta", tags=["meta"])

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULTS_PATH = REPO_ROOT / "defaults.toml"
EQUATIONS_PATH = REPO_ROOT / "src" / "johnfeng_photonics" / "equations.py"


@router.get("/defaults", response_model=DefaultsResponse)
def get_defaults() -> DefaultsResponse:
    with open(DEFAULTS_PATH, "rb") as f:
        data = tomllib.load(f)
    return DefaultsResponse(**data)


@router.get("/equations-source", response_model=EquationsSourceResponse)
def get_equations_source() -> EquationsSourceResponse:
    source = EQUATIONS_PATH.read_text(encoding="utf-8")
    return EquationsSourceResponse(source=source)
