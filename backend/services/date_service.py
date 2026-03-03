from datetime import date, timedelta
from typing import List

def generate_7_day_forecast(start_date: date) -> List[date]:
    return [start_date + timedelta(days=i) for i in range(7)]