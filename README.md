# Hypixel Skyblock Bazaar Crafting EV Optimiser

Compares the cost of crafting a Bazaar item with its instasell price to identify profitable crafting opportunities in real time.

## How it works

The Hypixel Bazaar has hundreds of tradeable items, many of which are craftable from cheaper materials. This tool:

1. Fetches live Bazaar prices from the Hypixel API
2. Loads crafting recipes from the [NotEnoughUpdates community repo](https://github.com/NotEnoughUpdates/NotEnoughUpdates-REPO)
3. For each craftable item, recursively computes the cheapest way to obtain every ingredient — either buying it from the Bazaar or crafting it from its own ingredients
4. Compares total craft cost against the item's instasell price and ranks everything by profit

The recursive pricing is the core of the tool. Rather than naively using the Bazaar instabuy price for every ingredient, it walks the full crafting tree and takes the cheapest of craft cost vs buy price at each level. This catches opportunities that a flat one-level comparison would miss.

## Project structure

```
src/
├── bazaar.py       # Fetches live prices from the Hypixel Bazaar API
├── recipies.py     # Downloads and parses crafting recipes from the NEU repo
└── calculate.py    # Recursive cost resolution and profit ranking
```

## Setup

```bash
git clone https://github.com/KristianHooymans/Hypixel-Skyblock-InstaBuy-vs-Craft-Price-Checker.git
cd Hypixel-Skyblock-InstaBuy-vs-Craft-Price-Checker/src
python3 -m venv venv
source venv/bin/activate
pip install requests
```

## Usage

```bash
python3 calculate.py
```

On the first run, the tool downloads the NEU recipe database (~20MB) and caches it locally as `neu_recipes_cache.json`. Subsequent runs load from the cache instantly. To force a refresh of the recipe data:

```bash
python3 calculate.py --refresh
```

## Example output

```
Item                                         Craft Cost   Sell Price (after tax)  Profit
-------------------------------------------------------------------------------------
METEOR_SHARD                                 550,032.9     702,000.8     151,967.9 ***
HORNS_OF_TORMENT                             260,320.9     286,509.7      26,188.8 ***
ENCHANTED_COMPOST                          2,762,428.6   2,780,289.5      17,860.9 ***
SUPER_COMPACTOR_3000                         116,995.8     130,984.6      13,988.8 ***
...

14 profitable crafts found.
```

Items marked `***` are profitable to craft and instasell at current Bazaar prices.

## Caveats

1. Prices are a snapshot at the time of the API call — the Bazaar moves fast
2. Profit figures are now tax-adjusted (1% Hypixel instasell fee applied)
3. High-profit items may have low daily volume, making it difficult to realise the full profit from crafting them
4. Recipe data is sourced from the community NEU repo and may not immediately reflect newly released items

## Planned improvements

1. Volume filtering to surface only items with meaningful daily sell volume
2. Automatic price refresh loop for continuous monitoring
