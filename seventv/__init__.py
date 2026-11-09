"""
# seventv [v2.3.1](https://pypi.org/project/seventv/)
## an asynchronous API-wrapper for [7tv.app](https://7tv.app)
### https://github.com/probablyjassin/seventv.py
"""

from .seventv import Emote, create_emote_objects, seventv

__version__ = "2.4.0"

__all__ = [
    'Emote',
    'create_emote_objects',
    'seventv',
    'seventvException',
]