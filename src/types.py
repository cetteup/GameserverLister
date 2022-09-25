from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict


# https://stackoverflow.com/a/54919285/9395553
class ExtendedEnum(Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class GamespyGame(str, ExtendedEnum):
    BF1942 = 'bf1942'
    BFVIETNAM = 'bfvietnam'
    BF2 = 'bf2'
    FH2 = 'fh2'
    BF2142 = 'bf2142'
    CRYSIS = 'crysis'
    CRYSISWARS = 'crysiswars'
    JBNIGHTFIRE = 'jbnightfire'
    PARAWORLD = 'paraworld'
    POSTAL2 = 'postal2'
    VIETCONG = 'vietcong'
    VIETCONG2 = 'vietcong2'


@dataclass
class GamespyConfig:
    game_name: str
    game_key: str
    enc_type: int
    query_type: int
    port: int
    servers: List[str]
    gamedig_type: str
    info_query: Optional[str] = None
    link_template_refs: Optional[Dict[str, List[str]]] = None
