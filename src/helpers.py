import ipaddress
import json
import logging
from typing import Callable

import gevent.subprocess


def find_query_port(gamedig_path: str, game: str, server: dict, ports_to_try: list, validator: Callable) -> int:
    query_port = -1

    # Add current query port add index 0 if valid
    if server.get('queryPort', -1) != -1:
        ports_to_try.insert(0, server['queryPort'])
    # Try all unique ports
    for port_to_try in list(set(ports_to_try)):
        if not is_valid_port(port_to_try):
            logging.warning(f'Skipping query port to try which is outside of valid port range ({port_to_try})')
            continue

        gamedig_result = gevent.subprocess.run(
            args=[gamedig_path, '--type', game, f'{server["ip"]}:{port_to_try}',
                  '--maxAttempts 2', '--socketTimeout 2000', '--givenPortOnly'],
            capture_output=True
        )

        # Make sure gamedig did not log any errors to stderr and has some output in stdout
        if len(gamedig_result.stderr) > 0 or len(gamedig_result.stdout) == 0:
            continue

        # Try to parse JSON returned by gamedig
        try:
            parsed_result = json.loads(gamedig_result.stdout)
        except json.JSONDecodeError as e:
            logging.debug(e)
            logging.error('Failed to parse gamedig command output')
            continue

        # Stop searching if query was successful and response came from the correct server
        # (some servers run on the same IP, so make sure ip and game_port match)
        if not parsed_result.get('error', '').startswith('Failed all') and \
                validator(server, port_to_try, parsed_result):
            query_port = port_to_try
            break

    return query_port


def is_valid_public_ip(ip: str) -> bool:
    try:
        ip_address = ipaddress.ip_address(ip)
        valid_public = ip_address.is_global
    except ValueError:
        valid_public = False

    return valid_public


def is_valid_port(port: int) -> bool:
    return 0 < port < 65536


def battlelog_server_validator(server: dict, used_query_port: int, parsed_result: dict) -> bool:
    return parsed_result.get('connect') == f'{server["ip"]}:{server["gamePort"]}'


def mohwf_server_validator(server: dict, used_query_port: int, parsed_result: dict) -> bool:
    return parsed_result.get('connect') == f'{server["ip"]}:{used_query_port}'


def bfbc2_server_validator(server: dict, used_query_port: int, parsed_result: dict) -> bool:
    return battlelog_server_validator(server, used_query_port, parsed_result) or \
           parsed_result.get('connect') == f'0.0.0.0:{server["gamePort"]}' or \
           parsed_result.get('name') == server['name']


def guid_from_ip_port(ip: str, port: str) -> str:
    int_port = int(port)
    guid = '-'.join([f'{int((pow(int(octet) + 2, 2)*pow(int_port, 2))/(int_port*8)):0>x}' for
                     (index, octet) in enumerate(ip.split('.'))])

    return guid
