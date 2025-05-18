from abc import ABC, abstractmethod
from typing import List

from GameserverLister.common.servers import Server
from GameserverLister.common.types import Game, Principal, Platform


class Provider(ABC):
    @abstractmethod
    def list(self, principal: Principal, game: Game, platform: Platform, **kwargs) -> List[Server]:
        pass
