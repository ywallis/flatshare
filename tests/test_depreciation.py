from datetime import datetime
from src.depreciation import depreciate_price
from src.models import Item


def test_depreciate_price(item_1: Item):

    date_for_calculation = datetime.strptime("2026-01-01", "%Y-%m-%d").date()
    assert depreciate_price(item_1, date_for_calculation) == 800

def test_depreciate_price_min_val(item_2: Item):

    date_for_calculation = datetime.strptime("2026-01-01", "%Y-%m-%d").date()
    assert depreciate_price(item_2, date_for_calculation) == 900

def test_depreciate_price_min_val_pct(item_3: Item):

    date_for_calculation = datetime.strptime("2026-01-01", "%Y-%m-%d").date()
    assert depreciate_price(item_3, date_for_calculation) == 950 
