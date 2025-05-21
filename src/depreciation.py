from datetime import date

from fastapi.exceptions import HTTPException

from src.models import Item


def depreciate_price(item: Item, date_for_calculation: date) -> float:
    """Calculates the depreciated price of an item. Requires a date in YYYY-MM-DD format."""

    if date_for_calculation < item.purchase_date:
        raise HTTPException(
            status_code=400,
            detail="Date of depreciation cannot be before date of purchase",
        )
    days_passed = (date_for_calculation - item.purchase_date).days
    depreciation_factor = (1 - item.yearly_depreciation) ** (days_passed / 365)
    depreciated_price: float = item.initial_value * depreciation_factor

    return depreciated_price
