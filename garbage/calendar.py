from typing import Text, List
from dataclasses import dataclass

import ics
import arrow
import aiohttp

from garbage.config import CALENDAR_URL


@dataclass
class Pickup:
    """
    Represents a garbage pickup
    """
    date: arrow.Arrow
    garbage_types: List[Text]


async def _fetch(url: Text) -> Text:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.text()


async def get_next_pickup(calendar_url: Text=CALENDAR_URL) -> Pickup:
    raw_ics = await _fetch(calendar_url)
    calendar = ics.Calendar(raw_ics)
    now = arrow.get()
    next_week = now.replace(weeks=+1)
    events = list(calendar.timeline.included(now, next_week))
    garbage_types = [
        event.name for event in events
        if event.begin == events[0].begin  # only get events for the nearest day
    ]
    return Pickup(date=events[0].begin, garbage_types=garbage_types)

