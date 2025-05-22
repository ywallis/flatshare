from datetime import datetime
from src.depreciation import depreciate_price
from src.models import Item


def test_depreciate_price(item_1: Item):

    date_for_calculation = datetime.strptime("2026-01-01", "%Y-%m-%d").date()
    assert depreciate_price(item_1, date_for_calculation) == 800
