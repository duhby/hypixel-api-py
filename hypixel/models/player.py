"""
The MIT License (MIT)

Copyright (c) 2021-present duhby

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from dataclasses import dataclass, fields, field
from datetime import datetime
from typing import Optional

from .. import utils

from .playerdata import Arcade
from .playerdata import Bedwars
from .playerdata import Socials

__all__ = (
    'Player',
)

@dataclass
class Player:
    _data: dict = field(repr=False)
    raw: dict = field(repr=False)
    id: str = None
    uuid: str = None
    first_login: datetime = None
    name: str = None
    last_login: datetime = None
    last_logout: datetime = None
    known_aliases: list = None
    # todo: change type to List[Achievement]
    achievements: list = field(default_factory=list, repr=False)
    achievements_multiple: dict = field(default_factory=dict, repr=False)
    network_exp: int = 0 # not sure why hypixel returns a float.. oh well
    karma: int = 0
    version: str = None
    achievement_points: int = 0
    current_gadget: str = None
    channel: str = None
    # todo: change type to Game
    most_recent_game: str = None

    @property
    def rank(self) -> Optional[str]:
        """
        returns:
        None
        VIP
        VIP+
        MVP
        MVP+
        MVP++
        YOUTUBE
        PIG+++
        MOJANG
        GAME MASTER
        ADMIN
        OWNER
        """
        display_rank = None
        pr = self.raw.get('player', {}).get('newPackageRank')
        mpr = self.raw.get('player', {}).get('monthlyPackageRank')
        prefix = self.raw.get('player', {}).get('prefix')
        rank = self.raw.get('player', {}).get('rank')
        if prefix:
            return utils.clean_rank_prefix(prefix)
        elif rank:
            if rank == 'YOUTUBER':
                return 'YOUTUBE'
            return rank.replace('_', ' ')
        elif mpr != 'SUPERSTAR':
            if not pr or pr == 'NONE':
                return None
            else:
                display_rank = pr
        else:
            return 'MVP++'
        return display_rank.replace('_', '').replace('PLUS', '+')

    def __post_init__(self):
        # type conversion
        for f in fields(self):
            value = getattr(self, f.name)
            if not value:
                continue
            elif not isinstance(value, f.type):
                if f.type is datetime:
                    unix = value / 1e3 # miliseconds to unix time
                    setattr(self, f.name, datetime.fromtimestamp(unix))
                else:
                    setattr(self, f.name, f.type(value))

        # level
        self.level: int = utils.get_level(self.network_exp)

        # socials
        social_data = self._data.get('socialMedia', {}).get('links')
        if social_data:
            social_data = utils._clean(social_data, mode='SOCIALS')
            self.socials = Socials(**social_data)
        else:
            self.socials = Socials({})

        # gamemodes
        arcade_data = utils._clean(self._data, mode='ARCADE')
        self.arcade = Arcade(**arcade_data)

        bedwars_data = utils._clean(self._data, mode='BEDWARS')
        self.bedwars = Bedwars(**bedwars_data)

        # tkr_data = utils._clean(self._data, mode='TKR')
        # self.tkr = TurboKartRacers(**tkr_data)
