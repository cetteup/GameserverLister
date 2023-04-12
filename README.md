# GameserverLister

[![ci](https://img.shields.io/github/actions/workflow/status/cetteup/GameserverLister/ci.yml?label=ci)](https://github.com/cetteup/GameserverLister/actions?query=workflow%3Aci)
[![License](https://img.shields.io/github/license/cetteup/GameserverLister)](/LICENSE)
[![Package](https://img.shields.io/pypi/v/GameserverLister)](https://pypi.org/project/GameserverLister/)
[![Last commit](https://img.shields.io/github/last-commit/cetteup/GameserverLister)](https://github.com/cetteup/GameserverLister/commits/main)

A Python 🐍 command line tool to retrieve game server lists for various games.

## Features

- create/update lists of game servers stored as JSON
- removal of servers not seen in a configurable timespan
- search game server's query ports if not contained in server list
- handle completely broken pagination on Battlelog
- proxy support for requests to Battlelog

## Usage

You can easily install GameserverLister via pip.

```bash
pip install GameserverLister
```

Upgrading from an older version is equally simple.

```bash
pip install --upgrade GameserverLister
```

After installing through pip, you can get some help for the command line options through

```bash
$ python3 -m GameserverLister --help
Usage: python -m GameserverLister [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  battlelog
  bfbc2
  gamespy
  gametools
  medalofhonor
  quake3
  unreal2
  valve
```

## Required tools

The server list retrieval for GameSpy-games requires an external tool. In order to retrieve GameSpy servers, you need to set up [gslist](http://aluigi.altervista.org/papers.htm#gslist). `gslist` was developed by Luigi Auriemma.

## Supported games

The scripts support retrieval for following games from the listed sources. If you know more sources for any of the listed games or know other games that support the listed protocols, please create an issue, and I will add them.

| Game                                   | Source type/protocol | Server list source(s)                                                                                             |
|----------------------------------------|----------------------|-------------------------------------------------------------------------------------------------------------------|
| 7 Days to Die                          | Valve                | Valve ¹                                                                                                           |
| America's Army: Proving Grounds        | Valve                | Valve ¹                                                                                                           |
| ARK: Survival Evolved                  | Valve                | Valve ¹                                                                                                           |
| Arma 2                                 | Valve                | Valve ¹                                                                                                           |
| Arma 3                                 | Valve                | Valve ¹                                                                                                           |
| Battlefield 1942                       | GameSpy              | bf1942.org, openspy.net, qtracker.com                                                                             |
| Battlefield Vietnam                    | GameSpy              | openspy.net, qtracker.com                                                                                         |
| Battlefield 2                          | GamsSpy              | bf2hub.com, playbf2.ru                                                                                            |
| Battlefield 2142                       | GameSpy              | novgames.ru, openspy.net, play2142.ru                                                                             |
| Battlefield: Bad Company 2             | fesl/theater         | Electronic Arts                                                                                                   |
| Battlefield 3                          | Battlelog            | battlelog.com                                                                                                     |
| Battlefield 4                          | Battlelog            | battlelog.com                                                                                                     |
| Battlefield Hardline                   | Battlelog            | battlelog.com                                                                                                     |
| Battlefield 1                          | Gametools API        | api.gametools.network                                                                                             |
| Battlefield 5                          | Gametools API        | api.gametools.network                                                                                             |
| Call of Duty                           | Quake3               | Activision                                                                                                        |
| Call of Duty: United Offensive         | Quake3               | Activision                                                                                                        |
| Call of Duty 2                         | Quake3               | Activision                                                                                                        |
| Call of Duty 4: Modern Warfare         | Quake3               | Activision                                                                                                        |
| CoD4x Mod                              | Quake3               | cod4x.ovh                                                                                                         |
| Counter Strike                         | Valve                | Valve ¹                                                                                                           |
| Counter Strike: Condition Zero         | Valve                | Valve ¹                                                                                                           |
| Counter Strike: Source                 | Valve                | Valve ¹                                                                                                           |
| Counter Strike: Global Offensive       | Valve                | Valve ¹                                                                                                           |
| Crysis                                 | GameSpy              | crymp.net                                                                                                         |
| Crysis Wars                            | GameSpy              | jedi95.us                                                                                                         |
| Day of Defeat                          | Valve                | Valve ¹                                                                                                           |
| Day of Defeat: Source                  | Valve                | Valve ¹                                                                                                           |
| DayZ                                   | Valve                | Valve ¹                                                                                                           |
| DayZ (Arma 2 mod)                      | Valve                | Valve ¹                                                                                                           |
| Deus Ex                                | GameSpy              | 333networks.com, errorist.eu, newbiesplayground.net, oldunreal.com                                                |
| Duke Nukem Forever                     | GameSpy              | 333networks.com                                                                                                   |
| Forgotten Hope 2                       | GameSpy              | fh2.dev                                                                                                           |
| Garry's Mod                            | Valve                | Valve ¹                                                                                                           |
| Insurgency                             | Valve                | Valve ¹                                                                                                           |
| Insurgency: Sandstorm                  | Valve                | Valve ¹                                                                                                           |
| James Bond 007: Nightfire              | GameSpy              | openspy.net, nightfirepc.com                                                                                      |
| Left 4 Dead                            | Valve                | Valve ¹                                                                                                           |
| Left 4 Dead 2                          | Valve                | Valve ¹                                                                                                           |
| Medal of Honor Warfighter              | Battlelog            | battlelog.com                                                                                                     |
| Nexuiz                                 | Quake3               | deathmask.net                                                                                                     |
| OpenArena                              | Quake3               | deathmask.net                                                                                                     |
| ParaWorld                              | GameSpy              | openspy.net                                                                                                       |
| Postal 2                               | GameSpy              | 333networks.com                                                                                                   |
| Q3Rally                                | Quake3               | deathmask.net                                                                                                     |
| Quake                                  | Quake3               | deathmask.net                                                                                                     |
| Quake 3 Arena                          | Quake3               | quake3arena.com, urbanterror.info, excessiveplus.net, ioquake3.org, huxxer.de, maverickservers.com, deathmask.net |
| Return to Castle Wolfenstein           | Quake3               | id Software                                                                                                       |
| Rising Storm 2: Vietnam                | Valve                | Valve ¹                                                                                                           |
| Rune                                   | GameSpy              | 333networks.com, errorist.eu, newbiesplayground.net, oldunreal.com                                                |
| Rust                                   | Valve                | Valve ¹                                                                                                           |
| Serious Sam: The First Encounter       | GameSpy              | 333networks.com, errorist.eu, newbiesplayground.net, oldunreal.com                                                |
| Serious Sam: Second Encounter          | GameSpy              | 333networks.com, errorist.eu, newbiesplayground.net, oldunreal.com                                                |
| Soldier of Fortune II: Double Helix    | Quake3               | Raven Software                                                                                                    |
| Squad                                  | Valve                | Valve ¹                                                                                                           |
| Star Wars Jedi Knight II: Jedi Outcast | Quake3               | Raven Software, jkhub.org                                                                                         |
| Star Wars Jedi Knight: Jedi Academy    | Quake3               | Raven Software, jkhub.org                                                                                         |
| SWAT 4                                 | GameSpy              | swat4stats.com                                                                                                    |
| Team Fortress Classic                  | Valve                | Valve ¹                                                                                                           |
| Team Fortress 2                        | Valve                | Valve ¹                                                                                                           |
| Tremulous                              | Quake3               | tremulous.net                                                                                                     |
| Unreal                                 | GameSpy              | 333networks.com, errorist.eu, openspy.net, oldunreal.com, qtracker.com                                            |
| Unreal Tournament                      | GameSpy              | 333networks.com, errorist.eu, openspy.net, oldunreal.com, qtracker.com                                            |
| Unreal Tournament 2003                 | Unreal2              | openspy.net                                                                                                       |
| Unreal Tournament 2004                 | Unreal2              | openspy.net, 333networks.com, errorist.eu                                                                         |
| Unreal Tournament 3                    | GameSpy              | openspy.net                                                                                                       |
| UrbanTerror                            | Quake3               | FrozenSand                                                                                                        |
| Vietcong                               | GameSpy              | vietcong.tk, vietcong1.eu, qtracker.com                                                                           |
| Vietcong 2                             | GameSpy              | openspy.net                                                                                                       |
| Warfork                                | Quake3               | deathmask.net                                                                                                     |
| Warsow                                 | Quake3               | deathmask.net                                                                                                     |
| Wheel of Time                          | GameSpy              | 333networks.com, errorist.eu, newbiesplayground.net, oldunreal.com                                                |
| Wolfenstein: Enemy Territory           | Quake3               | id Software, etlegacy.com                                                                                         |
| Xonotic                                | Quake3               | deathmask.net, tchr.no                                                                                            |

¹ Valve's principal servers are rate limited. If you do not use additional filters to only retrieve matching servers, you will get blocked/timed out. You can pass filters via the `-f`/`--filter` argument, e.g. use `-f "\dedicated\1\password\0\empty\1\full\1"` to only retrieve dedicated servers without a password which are neither full nor empty. You can find a full list of filter options [here](https://developer.valvesoftware.com/wiki/Master_Server_Query_Protocol#Filter) (the `\appid\` filter is applied automatically). 

## Game server query ports

After obtaining a server list, you may want request current details directly from the game server via different query protocols. However, only the GameSpy and Quake3 principal servers return the game server's query port. Battlelog and the EA fesl/theater do not provide details about the server's query port. So, the respective scripts attempt to find the query port if run with the `--find-query-port` flag.
