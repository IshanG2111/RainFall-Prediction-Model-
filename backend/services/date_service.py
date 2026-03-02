from datetime import datetime, timedelta
from typing import List

def generate_7_day_forecast(start_date: datetime) -> List[datetime]:
    return [start_date + timedelta(days=i) for i in range(7)]