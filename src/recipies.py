import io
import json
import zipfile
from pathlib import Path

import requests

NEU_ZIP_URL = (
    "https://github.com/NotEnoughUpdates/NotEnoughUpdates-REPO"
    "/archive/refs/heads/master.zip"
)
CACHE_PATH = Path("neu_recipes_cache.json")
RECIPE_SLOTS = ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3"]


def _parse_item(item_data: dict) -> tuple[str, dict[str, float]] | None:
    item_id = item_data.get("internalname", "").upper().replace("-", "_")
    if not item_id:
        return None

    raw_recipe = item_data.get("recipe")
    if not raw_recipe:
        return None

    output_count = int(raw_recipe.get("count", 1)) or 1

    # accumulate ingredient quantities across all 9 grid slots
    ingredients: dict[str, float] = {}
    for slot in RECIPE_SLOTS:
        slot_value = raw_recipe.get(slot, "")
        if not slot_value:
            continue

        parts = slot_value.split(":")
        ingredient_id = parts[0].upper().replace("-", "_")
        quantity = int(parts[1]) if len(parts) > 1 else 1

        if ingredient_id:
            ingredients[ingredient_id] = ingredients.get(ingredient_id, 0) + quantity

    if not ingredients:
        return None

    # normalise to per-single-output so profit calcs are consistent
    if output_count > 1:
        ingredients = {k: v / output_count for k, v in ingredients.items()}

    return item_id, ingredients


def _build_recipes_from_zip(zip_bytes: bytes) -> dict[str, dict[str, float]]:
    recipes: dict[str, dict[str, float]] = {}

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        for name in zf.namelist():
            if not (name.endswith(".json") and "/items/" in name):
                continue
            try:
                with zf.open(name) as f:
                    item_data = json.load(f)
            except (json.JSONDecodeError, KeyError):
                continue

            result = _parse_item(item_data)
            if result is not None:
                item_id, ingredients = result
                recipes[item_id] = ingredients

    return recipes


def _load_cache() -> dict | None:
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text())
        except (json.JSONDecodeError, OSError):
            return None
    return None


def _save_cache(recipes: dict) -> None:
    try:
        CACHE_PATH.write_text(json.dumps(recipes, indent=2))
    except OSError as e:
        print(f"[recipes] Warning: could not write cache: {e}")


def fetch_recipes(force_refresh: bool = False) -> dict[str, dict[str, float]]:
    if not force_refresh:
        cached = _load_cache()
        if cached is not None:
            print(f"[recipes] Loaded {len(cached):,} recipes from cache.")
            return cached

    print("[recipes] Downloading NEU repo ZIP...")
    response = requests.get(NEU_ZIP_URL, timeout=60)
    response.raise_for_status()
    print(f"[recipes] Downloaded {len(response.content) / 1_000_000:.1f} MB. Parsing...")

    recipes = _build_recipes_from_zip(response.content)
    _save_cache(recipes)
    print(f"[recipes] Parsed and cached {len(recipes):,} recipes.")
    return recipes


def get_recipe(item_id: str, recipes: dict) -> dict[str, float] | None:
    return recipes.get(item_id.upper().replace("-", "_"))


def all_craftable(recipes: dict) -> list[str]:
    return list(recipes.keys())


if __name__ == "__main__":
    recipes = fetch_recipes()
