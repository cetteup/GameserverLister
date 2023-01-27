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

## Required tools

The server list retrieval for GameSpy-games requires an external tool. In order to retrieve GameSpy servers, you need to set up [gslist](http://aluigi.altervista.org/papers.htm#gslist). `gslist` was developed by Luigi Auriemma.

## Supported games

The scripts support retrieval for following games from the listed sources. If you know more sources for any of the listed games or know other games that support the listed protocols, please create an issue, and I will add them.

| Game                                   | Source type/protocol | Server list source(s)                                                                                             |
|----------------------------------------|----------------------|-------------------------------------------------------------------------------------------------------------------|
| 7 Days to Die                          | Valve                | Valve ²                                                                                                           |
| ARK: Survival Evolved                  | Valve                | Valve ²                                                                                                           |
| Arma 2                                 | Valve                | Valve ²                                                                                                           |
| Arma 3                                 | Valve                | Valve ²                                                                                                           |
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
| Counter Strike                         | Valve                | Valve ²                                                                                                           |
| Counter Strike: Condition Zero         | Valve                | Valve ²                                                                                                           |
| Counter Strike: Source                 | Valve                | Valve ²                                                                                                           |
| Counter Strike: Global Offensive       | Valve                | Valve ²                                                                                                           |
| Crysis                                 | GameSpy              | crymp.net                                                                                                         |
| Crysis Wars                            | GameSpy              | jedi95.us                                                                                                         |
| Day of Defeat                          | Valve                | Valve ²                                                                                                           |
| Day of Defeat: Source                  | Valve                | Valve ²                                                                                                           |
| DayZ                                   | Valve                | Valve ²                                                                                                           |
| DayZ (Arma 2 mod)                      | Valve                | Valve ²                                                                                                           |
| Deus Ex                                | GameSpy              | 333networks.com, errorist.eu, newbiesplayground.net, oldunreal.com                                                |
| Duke Nukem Forever                     | GameSpy              | 333networks.com                                                                                                   |
| Forgotten Hope 2                       | GameSpy              | fh2.dev                                                                                                           |
| James Bond 007: Nightfire              | GameSpy              | openspy.net, nightfirepc.com                                                                                      |
| Medal of Honor Warfighter              | Battlelog            | battlelog.com                                                                                                     |
| Nexuiz                                 | Quake3               | deathmask.net                                                                                                     |
| OpenArena                              | Quake3               | deathmask.net                                                                                                     |
| ParaWorld                              | GameSpy              | openspy.net                                                                                                       |
| Postal 2                               | GameSpy              | 333networks.com                                                                                                   |
| Q3Rally                                | Quake3               | deathmask.net                                                                                                     |
| Quake                                  | Quake3               | deathmask.net                                                                                                     |
| Quake 3 Arena                          | Quake3               | quake3arena.com, urbanterror.info, excessiveplus.net, ioquake3.org, huxxer.de, maverickservers.com, deathmask.net |
| Return to Castle Wolfenstein           | Quake3               | id Software                                                                                                       |
| Rising Storm 2: Vietnam                | Valve                | Valve ²                                                                                                           |
| Rune                                   | GameSpy              | 333networks.com, errorist.eu, newbiesplayground.net, oldunreal.com                                                |
| Rust                                   | Valve                | Valve ²                                                                                                           |
| Serious Sam: The First Encounter       | GameSpy              | 333networks.com, errorist.eu, newbiesplayground.net, oldunreal.com                                                |
| Serious Sam: Second Encounter          | GameSpy              | 333networks.com, errorist.eu, newbiesplayground.net, oldunreal.com                                                |
| Soldier of Fortune II: Double Helix    | Quake3               | Raven Software                                                                                                    |
| Star Wars Jedi Knight II: Jedi Outcast | Quake3               | Raven Software, jkhub.org                                                                                         |
| Star Wars Jedi Knight: Jedi Academy    | Quake3               | Raven Software, jkhub.org                                                                                         |
| SWAT 4 ¹                               | GameSpy              | swat4stats.com                                                                                                    |
| Team Fortress Classic                  | Valve                | Valve ²                                                                                                           |
| Team Fortress 2                        | Valve                | Valve ²                                                                                                           |
| Tremulous                              | Quake3               | tremulous.net                                                                                                     |
| Unreal                                 | GameSpy              | 333networks.com, errorist.eu, openspy.net, oldunreal.com, qtracker.com                                            |
| Unreal Tournament                      | GameSpy              | 333networks.com, errorist.eu, openspy.net, oldunreal.com, qtracker.com                                            |
| Unreal Tournament 2003                 | Unreal2              | openspy.net                                                                                                       |
| Unreal Tournament 2004                 | Unreal2              | openspy.net                                                                                                       |
| Unreal Tournament 3                    | GameSpy              | openspy.net                                                                                                       |
| UrbanTerror                            | Quake3               | FrozenSand                                                                                                        |
| Vietcong                               | GameSpy              | vietcong.tk, vietcong1.eu, qtracker.com                                                                           |
| Vietcong 2                             | GameSpy              | openspy.net                                                                                                       |
| Warfork                                | Quake3               | deathmask.net                                                                                                     |
| Warsow                                 | Quake3               | deathmask.net                                                                                                     |
| Wheel of Time                          | GameSpy              | 333networks.com, errorist.eu, newbiesplayground.net, oldunreal.com                                                |
| Wolfenstein: Enemy Territory           | Quake3               | id Software, etlegacy.com                                                                                         |
| Xonotic                                | Quake3               | deathmask.net, tchr.no                                                                                            |

¹ Requires a [modified version of gslist](https://github.com/cetteup/gslist) which provides additional parameters.

² Valve's principal servers are rate limited. If you do not use additional filters to only retrieve matching servers, you will get blocked/timed out. You can pass filters via the `-f`/`--filter` argument, e.g. use `-f "\dedicated\1\password\0\empty\1\full\1"` to only retrieve dedicated servers without a password which are neither full nor empty. You can find a full list of filter options [here](https://developer.valvesoftware.com/wiki/Master_Server_Query_Protocol#Filter) (the `\appid\` filter is applied automatically). 

## Game server query ports

After obtaining a server list, you may want request current details directly from the game server via different query protocols. However, only the GameSpy and Quake3 principal servers return the game server's query port. Battlelog and the EA fesl/theater do not provide details about the server's query port. So, the respective scripts attempt to find the query port if run with the `--find-query-port` flag.
