import logging
import sys
from typing import Tuple, Optional, Union, List

import pyq3serverlist
import requests

from GameserverLister.common.helpers import is_valid_public_ip, is_valid_port, guid_from_ip_port, \
    is_server_listed_on_gametracker
from GameserverLister.common.servers import ClassicServer, ViaStatus
from GameserverLister.common.types import MedalOfHonorGame
from GameserverLister.common.weblinks import WebLink, WEB_LINK_TEMPLATES
from .common import ServerLister


class MedalOfHonorServerLister(ServerLister):
    """
    The defacto standard principal server for Medal of Honor games uses a query GameSpy protocol implementation that
    does not work with gslist. However, they also provide server lists as text files, which unfortunately only contain
    the game port. So, instead of extending the GameSpy server lister and trying to find the query port, we use the
    text files to find servers. Since the Medal of Honor games support Quake3-like queries on the game port, we can use
    that to query servers with the information we have.
    """
    game: MedalOfHonorGame

    def __init__(self, game: MedalOfHonorGame, expired_ttl: float, recover: bool, add_links: bool, list_dir: str):
        super().__init__(game, ClassicServer, expired_ttl, recover, add_links, list_dir)

    def update_server_list(self):
        request_ok = False
        attempt = 0
        max_attempts = 3
        raw_server_list = None
        while not request_ok and attempt < max_attempts:
            try:
                logging.info('Fetching server list from mohaaservers.tk')
                resp = self.session.get(self.get_server_list_url(), timeout=self.request_timeout)

                if resp.ok:
                    raw_server_list = resp.text
                    request_ok = True
                else:
                    attempt += 1
            except requests.exceptions.RequestException as e:
                logging.debug(e)
                logging.error(f'Failed to fetch servers from mohaaservers.tk, attempt {attempt + 1}/{max_attempts}')
                attempt += 1

        # Make sure any servers were found
        if raw_server_list is None:
            logging.error('Failed to retrieve server list, exiting')
            sys.exit(1)

        # Parse list
        found_servers = []
        for line in raw_server_list.strip(' \n').split('\n'):
            # Silently skip any completely empty lines
            if len(line) == 0:
                continue

            elems = line.strip().split(':')

            if len(elems) != 2:
                logging.warning(f'Principal returned malformed server list entry ({line}), skipping it')
                continue

            ip, query_port = elems
            if not is_valid_public_ip(ip) or not is_valid_port(int(query_port)):
                logging.warning(f'Principal returned invalid server entry ({ip}:{query_port}), skipping it')
                continue

            via = ViaStatus('mohaaservers.tk')
            found_server = ClassicServer(
                guid_from_ip_port(ip, query_port),
                ip,
                int(query_port),
                via
            )

            if self.add_links:
                # query port = game port for MOH games, so we can use that here to build links
                found_server.add_links(self.build_server_links(
                    found_server.uid,
                    found_server.ip,
                    found_server.query_port
                ))

            found_servers.append(found_server)

        self.add_update_servers(found_servers)

    def get_server_list_url(self) -> str:
        # mohaaservers uses a "key" without the "moh" prefix, e.g. "servers_aa" for "mohaa"
        return f'https://mohaaservers.tk/servlist/servers_{self.game[3:]}.txt'

    def check_if_server_still_exists(self, server: ClassicServer, checks_since_last_ok: int) -> Tuple[bool, bool, int]:
        # Since we query the server directly, there is no way of handling HTTP server errors differently then
        # actually failed checks, so even if the query fails, we have to treat it as "check ok"
        check_ok = True
        found = False
        try:
            pyq3serverlist.MedalOfHonorServer(server.ip, server.query_port).get_status()

            # get_status will raise an exception if the server cannot be contacted,
            # so this will only be reached if the query succeeds
            found = True
        except pyq3serverlist.PyQ3SLError as e:
            logging.debug(e)
            logging.debug(f'Failed to query server {server.uid} for expiration check')

        return check_ok, found, checks_since_last_ok

    def build_server_links(
            self,
            uid: str,
            ip: Optional[str] = None,
            port: Optional[int] = None
    ) -> Union[List[WebLink], WebLink]:
        links = []
        if is_server_listed_on_gametracker(self.game, ip, port):
            links.append(WEB_LINK_TEMPLATES['gametracker'].render(self.game, uid, ip=ip, port=port))

        return links
