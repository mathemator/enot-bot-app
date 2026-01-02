import datetime
import logging
import requests

logger = logging.getLogger(__name__)

# year -> {date: is_workday}
_calendar_cache: dict[int, dict[datetime.date, bool]] = {}


def _load_calendar_for_year(year: int) -> dict[datetime.date, bool]:
    url = "https://isdayoff.ru/api/getdata"
    params = {"year": year}

    logger.info(f"Загружаю рабочий календарь на {year} год")

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.text.strip()  # строка из 0/1/2

    start_date = datetime.date(year, 1, 1)
    calendar: dict[datetime.date, bool] = {}

    for i, day_type in enumerate(data):
        current_date = start_date + datetime.timedelta(days=i)
        # 0 — рабочий, 1 — выходной, 2 — сокращённый (считаем рабочим)
        is_workday = day_type in ("0", "2")

        calendar[current_date] = is_workday

    return calendar


def is_workday(date: datetime.date) -> bool:
    year = date.year

    if year not in _calendar_cache:
        try:
            _calendar_cache[year] = _load_calendar_for_year(year)
        except Exception:
            logger.exception(
                "Не удалось загрузить календарь. Считаю день рабочим."
            )
            return True  # fail-open

    return _calendar_cache[year].get(date, True)
