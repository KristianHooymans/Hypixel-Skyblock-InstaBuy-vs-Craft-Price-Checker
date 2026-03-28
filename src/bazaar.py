import requests

BAZAAR_URL = "https://api.hypixel.net/v2/skyblock/bazaar"

def fetch_bazaar():
    response = requests.get(BAZAAR_URL)
    response.raise_for_status()
    return response.json()

def get_prices(data):
    prices = {}
    for product_id, product in data["products"].items():
        quick = product["quick_status"]
        prices[product_id] = {
            "insta_buy": quick["buyPrice"],
            "insta_sell": quick["sellPrice"],
        }
    return prices

if __name__ == "__main__":
    data = fetch_bazaar()
    prices = get_prices(data)

