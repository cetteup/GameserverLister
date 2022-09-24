from dataclasses import dataclass
from typing import List, Optional, Dict


@dataclass
class GamespyConfig:
    game_name: str
    game_key: str
    enc_type: int
    query_type: int
    port: int
    servers: List[str]
    gamedig_type: str
    link_template_refs: Optional[Dict[str, List[str]]] = None
