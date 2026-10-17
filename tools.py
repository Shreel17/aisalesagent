
import json
from pathlib import Path


# Load product details and business rules from configuration.
CONFIG_PATH = Path(__file__).resolve().parent / "app_config.json"


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def estimate_price():
    """Return the configured product price without inventing discounts."""
    config = load_config()
    product = config["product"]

    return {
        "success": True,
        "product": product["name"],
        "base_price": product["base_price"],
        "currency": product["currency"],
        "discounts_allowed": product["discounts_allowed"],
    }


def check_budget_eligibility(budget):
    """Compare a customer's budget against the configured minimum."""
    config = load_config()
    minimum_budget = config["qualification_rules"]["minimum_budget"]

    if budget is None or budget < 0:
        return {
            "success": False,
            "error": "A valid, non-negative budget is required.",
        }

    return {
        "success": True,
        "customer_budget": budget,
        "minimum_budget": minimum_budget,
        "eligible": budget >= minimum_budget,
        "currency": config["product"]["currency"],
    }
