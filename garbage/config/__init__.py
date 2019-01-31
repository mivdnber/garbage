from .defaults import *
try:
    from .config import *
except ImportError:
    raise RuntimeError('Please create garbage/config.py (see garbage/defaults.py for options)')

assert CALENDAR_URL, 'Please set a calendar URL from https://www.ophaalkalender.be/Calendar'
