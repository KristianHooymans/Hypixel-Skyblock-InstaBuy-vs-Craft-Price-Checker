from bazaar import fetch_bazaar, get_prices
from recipies import fetch_recipes, all_craftable, get_recipe


def craft_cost(item_id: str, recipes: dict, prices: dict) -> float | None:
    recipe = get_recipe(item_id, recipes)
    if recipe is None:
        return None

    total = 0.0
    for ingredient_id, quantity in recipe.items():
        if ingredient_id not in prices:
            return None
        total += prices[ingredient_id]["insta_buy"] * quantity

    return total


def find_opportunities(recipes: dict, prices: dict) -> list[dict]:
    results = []

    for item_id in all_craftable(recipes):
        cost = craft_cost(item_id, recipes, prices)
        if cost is None or cost == 0.0:
            continue

        if item_id not in prices:
            continue

        sell_price = prices[item_id]["insta_sell"]
        profit = sell_price - cost

        results.append({
            "item":       item_id,
            "craft_cost": cost,
            "sell_price": sell_price,
            "profit":     profit,
        })

    results.sort(key=lambda x: x["profit"], reverse=True)
    return results


def display(results: list[dict]) -> None:
    header = f"{'Item':<40} {'Craft Cost':>14} {'Sell Price':>14} {'Profit':>14}"
    print(header)
    print("-" * len(header))
    for r in results:
        marker = " ***" if r["profit"] > 0 else ""
        print(
            f"{r['item']:<40}"
            f"{r['craft_cost']:>14,.1f}"
            f"{r['sell_price']:>14,.1f}"
            f"{r['profit']:>14,.1f}"
            f"{marker}"
        )


if __name__ == "__main__":
    print("Fetching bazaar prices...")
    prices = get_prices(fetch_bazaar())

    print("Loading recipes...")
    recipes = fetch_recipes()

    print()
    results = find_opportunities(recipes, prices)
    display(results)
    print(f"\n{sum(1 for r in results if r['profit'] > 0)} profitable crafts found.")
