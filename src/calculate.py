from bazaar import fetch_bazaar, get_prices
from recipies import fetch_recipes, all_craftable, get_recipe
import argparse


def best_cost(item_id: str, recipes: dict, prices: dict, visiting: set) -> float | None:
    if item_id in visiting:
        return prices.get(item_id, {}).get("insta_buy")

    bazaar_price = prices.get(item_id, {}).get("insta_buy")
    recipe = get_recipe(item_id, recipes)

    if recipe is None:
        return bazaar_price

    visiting.add(item_id)
    craft_total = 0.0
    for ingredient_id, quantity in recipe.items():
        ingredient_cost = best_cost(ingredient_id, recipes, prices, visiting)
        if ingredient_cost is None:
            craft_total = None
            break
        craft_total += ingredient_cost * quantity
    visiting.discard(item_id)

    if craft_total is None:
        return bazaar_price
    if bazaar_price is None:
        return craft_total
    return min(craft_total, bazaar_price)


def find_opportunities(recipes: dict, prices: dict) -> list[dict]:
    results = []
    TAX = 0.99

    for item_id in all_craftable(recipes):
        recipe = get_recipe(item_id, recipes)
        if recipe is None:
            continue

        visiting = set()
        visiting.add(item_id)
        craft_total = 0.0
        valid = True
        for ingredient_id, quantity in recipe.items():
            cost = best_cost(ingredient_id, recipes, prices, visiting)
            if cost is None:
                valid = False
                break
            craft_total += cost * quantity

        if not valid or craft_total == 0.0:
            continue

        if item_id not in prices:
            continue

        sell_price = prices[item_id]["insta_sell"]
        profit = (sell_price * TAX) - craft_total

        results.append({
            "item":       item_id,
            "craft_cost": craft_total,
            "sell_price": sell_price,
            "profit":     profit,
        })

    results.sort(key=lambda x: x["profit"], reverse=True)
    return results


def display(results: list[dict]) -> None:
    header = f"{'Item':<40} {'Craft Cost':>14} {'Sell Price (after tax)':>14} {'Profit':>2}"
    print(header)
    print("-" * len(header))
    for r in results:
        marker = " ***" if r["profit"] > 0 else ""
        print(
            f"{r['item']:<40}"
            f"{r['craft_cost']:>14,.1f}"
            f"{r['sell_price']:>14,.1f}"
            f"{r['profit']:>2,.1f}"
            f"{marker}"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hypixel Bazaar Crafting EV Optimiser")
    parser.add_argument("--refresh", action="store_true", help="Force re-download of NEU recipe cache")
    args = parser.parse_args()

    recipies = fetch_recipes(force_refresh=args.refresh)

    print("Fetching bazaar prices...")
    prices = get_prices(fetch_bazaar())

    print("Loading recipes...")
    recipes = fetch_recipes()

    print()
    results = find_opportunities(recipes, prices)
    display(results)
    print(f"\n{sum(1 for r in results if r['profit'] > 0)} profitable crafts found.")
