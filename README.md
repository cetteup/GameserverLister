# gameserver-lister

A Python 🐍 script to retrieve game server lists for various games.

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

| Game                                                    | Source type/protocol | Server list source(s)                                                                                             |
|---------------------------------------------------------|----------------------|-------------------------------------------------------------------------------------------------------------------|
| Battlefield 1942                                        | GameSpy              | bf1942.sk, bf1942.org, openspy, qtracker                                                                          |
| Battlefield Vietnam                                     | GameSpy              | openspy, qtracker                                                                                                 |
| Battlefield 2                                           | GamsSpy              | bf2hub, playbf2                                                                                                   |
| Battlefield 2142                                        | GameSpy              | novgames, openspy, play2142                                                                                       |
| Battlefield: Bad Company 2                              | fesl/theater         | Electronic Arts                                                                                                   |
| Battlefield 3                                           | Battlelog            | battlelog.com                                                                                                     |
| Battlefield 4                                           | Battlelog            | battlelog.com                                                                                                     |
| Battlefield Hardline                                    | Battlelog            | battlelog.com                                                                                                     |
| Battlefield 1                                           | Gametools API        | api.gametools.network                                                                                             |
| Battlefield 5                                           | Gametools API        | api.gametools.network                                                                                             |
| Call of Duty                                            | Quake3               | Activision                                                                                                        |
| Call of Duty: United Offensive                          | Quake3               | Activision                                                                                                        |
| Call of Duty 2                                          | Quake3               | Activision                                                                                                        |
| Call of Duty 4: Modern Warfare                          | Quake3               | Activision                                                                                                        |
| CoD4x Mod                                               | Quake3               | cod4x.me, doszgep.cloud                                                                                           |
| Crysis                                                  | GameSpy              | crymp.net                                                                                                         |
| Crysis Wars                                             | GameSpy              | jedi95.us                                                                                                         |
| James Bond 007: Nightfire                               | GameSpy              | openspy, nightfirepc.com                                                                                          |
| Medal of Honor Warfighter                               | Battlelog            | battlelog.com                                                                                                     |
| Nexuiz                                                  | Quake3               | deathmask.net                                                                                                     |
| OpenArena                                               | Quake3               | deathmask.net                                                                                                     |
| ParaWorld                                               | GameSpy              | openspy                                                                                                           |
| Postal 2                                                | GameSpy              | 333networks.com                                                                                                   |
| Q3Rally                                                 | Quake3               | deathmask.net                                                                                                     |
| Quake                                                   | Quake3               | deathmask.net                                                                                                     |
| Quake 3 Arena                                           | Quake3               | quake3arena.com, urbanterror.info, excessiveplus.net, ioquake3.org, huxxer.de, maverickservers.com, deathmask.net |
| Return to Castle Wolfenstein                            | Quake3               | id Software                                                                                                       |
| Soldier of Fortune II: Double Helix (Demo/sof2mp-1.02t) | Quake3               | Raven Software                                                                                                    |
| Soldier of Fortune II: Double Helix (Full/sof2mp-1.00)  | Quake3               | Raven Software                                                                                                    |
| Soldier of Fortune II: Double Helix (Gold/sof2mp-1.02)  | Quake3               | Raven Software                                                                                                    |
| Star Wars: Jedi Knight: Jedi Academy                    | Quake3               | Raven Software                                                                                                    |
| Tremulous                                               | Quake3               | tremulous.net                                                                                                     |
| UrbanTerror                                             | Quake3               | FrozenSand                                                                                                        |
| Vietcong                                                | GameSpy              | vietcong.tk, vietcong1.eu, qtracker                                                                               |
| Vietcong 2                                              | GameSpy              | openspy                                                                                                           |
| Warfork                                                 | Quake3               | deathmask.net                                                                                                     |
| Warsow                                                  | Quake3               | deathmask.net                                                                                                     |
| Wolfenstein: Enemy Territory                            | Quake3               | id Software, etlegacy.com                                                                                         |
| Xonotic                                                 | Quake3               | deathmask.net, tchr.no                                                                                            |

## Game server query ports

After obtaining a server list, you may want request current details directly from the game server via different query protocols. However, only the GameSpy and Quake3 principal servers return the game server's query port. Battlelog and the EA fesl/theater do not provide details about the server's query port. So, the respective scripts attempt to find the query port if run with the `--find-query-port` flag.
