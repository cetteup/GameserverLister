import unittest
from datetime import datetime, timedelta

from GameserverLister.common.constants import UNIX_EPOCH_START
from GameserverLister.common.servers import Server, QueryableServer, ClassicServer, FrostbiteServer, BadCompany2Server, \
    GametoolsServer, ViaStatus, WebLink


class ServerTest(unittest.TestCase):
    def test_update(self):
        # GIVEN two different servers
        guid, first_seen_at = 'a-guid', datetime(1990, 1, 1, 19, 30, 30, 30)
        a = Server(guid, [], first_seen_at)
        b = Server('b-guid', [], datetime(2000, 1, 1, 20, 0, 1, 1))

        # WHEN server a is updated with server b
        a.update(b)

        # THEN
        # Server a's uid remains unchanged
        self.assertEqual(a.uid, a.uid)
        # Server a's first seen at time remains unchanged
        self.assertEqual(a.first_seen_at, a.first_seen_at)
        # Server a's last seen at time is updated
        self.assertEqual(b.last_seen_at, a.last_seen_at)

    def test_update_links_add_new(self):
        # GIVEN two different servers
        a = Server('a-guid', [])
        link = WebLink('a-site', 'a-url', True)
        b = Server('b-guid', link)

        # WHEN server a is updated with server b
        a.update(b)

        # THEN
        # Server b's link is added to server a
        self.assertEqual(1, len(a.links))
        self.assertEqual(link, a.links[0])

    def test_update_links_update_existing(self):
        # GIVEN two different servers
        site = 'a-site'
        a_link = WebLink(site, 'a-url', True)
        a = Server('a-guid', a_link)
        b_link = WebLink(site, 'b-url', False)
        b = Server('b-guid', b_link)

        # WHEN server a is updated with server b
        a.update(b)

        # THEN
        # Server a's link is updated with server b's link
        self.assertEqual(1, len(a.links))
        self.assertEqual(site, a.links[0].site)
        self.assertEqual(b_link.url, a.links[0].url)
        self.assertEqual(b_link.official, a.links[0].official)


class QueryableServerTest(unittest.TestCase):
    def test_update(self):
        a = QueryableServer('a-guid', '1.1.1.1', 19567, [], datetime(1990, 1, 1, 19, 30, 30, 30))
        b = QueryableServer('b-guid', '1.0.0.1', 25200, [], None, datetime(2000, 1, 1, 20, 0, 1, 1))
        a.update(b)
        self.assertEqual(a.uid, a.uid)
        self.assertEqual(b.ip, a.ip)
        self.assertEqual(b.query_port, a.query_port)
        self.assertEqual(a.first_seen_at, a.first_seen_at)
        self.assertEqual(b.last_seen_at, a.last_seen_at)

    def test_is_json_repr_valid(self):
        parsed = {'guid': 'a-guid', 'ip': '1.1.1.1', 'queryPort': 47200}
        self.assertTrue(QueryableServer.is_json_repr(parsed))

    def test_is_json_repr_guid_missing(self):
        parsed = {'ip': '1.1.1.1', 'queryPort': 47200}
        self.assertFalse(QueryableServer.is_json_repr(parsed))

    def test_is_json_repr_ip_missing(self):
        parsed = {'guid': 'a-guid', 'queryPort': 47200}
        self.assertFalse(QueryableServer.is_json_repr(parsed))

    def test_is_json_repr_query_port_missing(self):
        parsed = {'guid': 'a-guid', 'ip': '1.1.1.1'}
        self.assertFalse(QueryableServer.is_json_repr(parsed))


class ClassicServerTest(unittest.TestCase):
    def test_update_via_status_add_new(self):
        a = ClassicServer('a-guid', '1.1.1.1', 29900, [])
        via = ViaStatus('a-principal')
        b = ClassicServer('b-guid', '1.0.0.1', 47200, via)
        a.update(b)
        self.assertEqual(1, len(a.via))
        self.assertEqual(via, a.via[0])

    def test_update_via_status_update_existing(self):
        principal, first_seen_at = 'a-principal', datetime(1990, 1, 1, 19, 30, 30, 30)
        a_via = ViaStatus(principal, first_seen_at, datetime(2000, 2, 2, 15, 15, 15, 30))
        a = ClassicServer('a-guid', '1.1.1.1', 29900, a_via)
        b_via = ViaStatus(principal)
        b = ClassicServer('b-guid', '1.0.0.1', 47200, b_via)
        a.update(b)
        self.assertEqual(1, len(a.via))
        self.assertEqual(principal, a.via[0].principal)
        self.assertEqual(first_seen_at, a.via[0].first_seen_at)
        self.assertEqual(b_via.last_seen_at, a.via[0].last_seen_at)

    def test_load(self):
        guid, ip, query_port = 'a-guid', '1.1.1.1', 47200
        now = datetime.now().astimezone()
        first_seen_at, last_seen_at = now, now + timedelta(minutes=10)
        via = ViaStatus('openspy', first_seen_at, last_seen_at)
        parsed = {
            'guid': guid,
            'ip': ip,
            'queryPort': query_port,
            'firstSeenAt': first_seen_at.isoformat(),
            'lastSeenAt': last_seen_at.isoformat(),
            'via': [via.dump()],
            'links': [],
        }
        expect = ClassicServer(guid, ip, query_port, via, first_seen_at, last_seen_at)
        actual = ClassicServer.load(parsed)
        self.assertEqual(expect, actual)

    def test_load_first_seen_at_none(self):
        guid, ip, query_port = 'a-guid', '1.1.1.1', 47200
        now = datetime.now().astimezone()
        via = ViaStatus('openspy', now, now)
        parsed = {'guid': guid, 'ip': ip, 'queryPort': query_port,
                  'firstSeenAt': None, 'lastSeenAt': now.isoformat(), 'via': [via.dump()], 'links': []}
        expect = ClassicServer(guid, ip, query_port, via, None, now)
        actual = ClassicServer.load(parsed)
        self.assertEqual(expect, actual)

    def test_load_last_seen_at_none(self):
        guid, ip, query_port = 'a-guid', '1.1.1.1', 47200
        now = datetime.now().astimezone()
        via = ViaStatus('openspy', now, now)
        parsed = {'guid': guid, 'ip': ip, 'queryPort': query_port,
                  'firstSeenAt': now.isoformat(), 'lastSeenAt': None, 'via': [via.dump()], 'links': []}
        expect = ClassicServer(guid, ip, query_port, via, now, UNIX_EPOCH_START)
        actual = ClassicServer.load(parsed)
        self.assertEqual(expect, actual)

    def test_dump(self):
        guid, ip, query_port = 'a-guid', '1.1.1.1', 47200
        now = datetime.now().astimezone()
        via = ViaStatus('openspy', now, now)
        server = ClassicServer(guid, ip, query_port, via, now, now)
        expect = {'guid': guid, 'ip': ip, 'queryPort': query_port, 'links': [],
                  'firstSeenAt': now.isoformat(), 'lastSeenAt': now.isoformat(), 'via': [via.dump()]}
        actual = server.dump()
        self.assertEqual(expect, actual)

    def test_load_via_missing(self):
        guid, ip, query_port = 'a-guid', '1.1.1.1', 47200
        now = datetime.now().astimezone()
        first_seen_at, last_seen_at = now, now + timedelta(minutes=10)
        parsed = {
            'guid': guid,
            'ip': ip,
            'queryPort': query_port,
            'firstSeenAt': first_seen_at.isoformat(),
            'lastSeenAt': last_seen_at.isoformat()
        }
        expect = ClassicServer(guid, ip, query_port, [], first_seen_at, last_seen_at)
        actual = ClassicServer.load(parsed)
        self.assertEqual(expect, actual)

    def test_dump_first_seen_at_none(self):
        guid, ip, query_port = 'a-guid', '1.1.1.1', 47200
        now = datetime.now().astimezone()
        via = ViaStatus('openspy', now, now)
        server = ClassicServer(guid, ip, query_port, via, None, now)
        expect = {'guid': guid, 'ip': ip, 'queryPort': query_port, 'links': [],
                  'firstSeenAt': None, 'lastSeenAt': now.isoformat(), 'via': [via.dump()]}
        actual = server.dump()
        self.assertEqual(expect, actual)


class ViaStatusTest(unittest.TestCase):
    def test_update(self):
        principal, first_seen_at = 'a-principal', datetime(1990, 1, 1, 19, 30, 30, 30)
        a = ViaStatus(principal, first_seen_at)
        b = ViaStatus('b-principal')
        a.update(b)
        self.assertEqual(principal, a.principal)
        self.assertEqual(first_seen_at, a.first_seen_at)
        self.assertEqual(b.last_seen_at, a.last_seen_at)

    def test_load(self):
        principal, first_seen_at, last_seen_at = 'a-principal', datetime(1990, 1, 1, 19, 30, 30, 30), \
                                                 datetime(2010, 10, 10, 20, 0, 1, 1)
        parsed = {'principal': principal, 'firstSeenAt': first_seen_at.isoformat(),
                  'lastSeenAt': last_seen_at.isoformat()}
        expect = ViaStatus(principal, first_seen_at, last_seen_at)
        actual = ViaStatus.load(parsed)
        self.assertEqual(expect, actual)

    def test_is_json_repr_valid(self):
        now = datetime.now().astimezone()
        parsed = {'principal': 'a-principal', 'firstSeenAt': now.isoformat(), 'lastSeenAt': now.isoformat()}
        self.assertTrue(ViaStatus.is_json_repr(parsed))

    def test_is_json_repr_principal_missing(self):
        now = datetime.now().astimezone()
        parsed = {'firstSeenAt': now.isoformat(), 'lastSeenAt': now.isoformat()}
        self.assertFalse(ViaStatus.is_json_repr(parsed))

    def test_is_json_repr_first_seen_at_missing(self):
        now = datetime.now().astimezone()
        parsed = {'principal': 'a-principal', 'lastSeenAt': now.isoformat()}
        self.assertFalse(ViaStatus.is_json_repr(parsed))

    def test_is_json_repr_last_seen_at_missing(self):
        now = datetime.now().astimezone()
        parsed = {'principal': 'a-principal', 'lastSeenAt': now.isoformat()}
        self.assertFalse(ViaStatus.is_json_repr(parsed))

    def test_dump(self):
        principal, first_seen_at, last_seen_at = 'a-principal', datetime(1990, 1, 1, 19, 30, 30, 30), \
                                                 datetime(2010, 10, 10, 20, 0, 1, 1)
        server = ViaStatus(principal, first_seen_at, last_seen_at)
        expect = {'principal': principal, 'firstSeenAt': first_seen_at.isoformat(),
                  'lastSeenAt': last_seen_at.isoformat()}
        actual = server.dump()
        self.assertEqual(expect, actual)


class FrostbiteServerTest(unittest.TestCase):
    def test_update(self):
        guid, first_seen_at = 'a-guid', datetime(1990, 1, 1, 19, 30, 30, 30)
        a = FrostbiteServer(guid, 'a-server-name', '1.1.1.1', 19567, 48888, first_seen_at)
        b = FrostbiteServer('b-guid', 'b-server-name', '1.0.0.1', 25200, 47200, None, datetime(2000, 1, 1, 20, 0, 1, 1),
                            datetime(2010, 10, 10, 20, 0, 1, 1))
        a.update(b)
        self.assertEqual(guid, a.uid)
        self.assertEqual(b.name, a.name)
        self.assertEqual(b.ip, a.ip)
        self.assertEqual(b.game_port, a.game_port)
        self.assertEqual(b.query_port, a.query_port)
        self.assertEqual(first_seen_at, a.first_seen_at)
        self.assertEqual(b.last_seen_at, a.last_seen_at)
        self.assertEqual(b.last_queried_at, a.last_queried_at)

    def test_update_last_queried_at_none(self):
        guid, first_seen_at, last_queried_at = 'a-guid', datetime(1990, 1, 1, 19, 30, 30, 30), \
                                               datetime(1994, 1, 1, 19, 30, 30, 30)
        a = FrostbiteServer(guid, 'a-server-name', '1.1.1.1', 19567, 48888, first_seen_at,
                            datetime(1990, 1, 1, 19, 30, 30, 30), last_queried_at)
        b = FrostbiteServer('b-guid', 'b-server-name', '1.0.0.1', 25200, 47200, None, datetime(2000, 1, 1, 20, 0, 1, 1))
        a.update(b)
        self.assertEqual(guid, a.uid)
        self.assertEqual(b.name, a.name)
        self.assertEqual(b.ip, a.ip)
        self.assertEqual(b.game_port, a.game_port)
        self.assertEqual(b.query_port, a.query_port)
        self.assertEqual(first_seen_at, a.first_seen_at)
        self.assertEqual(b.last_seen_at, a.last_seen_at)
        # Must remain as is, since b has not been queried (b.last_queried_at is None)
        self.assertEqual(last_queried_at, a.last_queried_at)

    def test_update_query_port_dummy(self):
        guid, query_port, first_seen_at = 'a-guid', 48888, datetime(1990, 1, 1, 19, 30, 30, 30)
        a = FrostbiteServer(guid, 'a-server-name', '1.1.1.1', 19567, query_port, first_seen_at)
        b = FrostbiteServer('b-guid', 'b-server-name', '1.0.0.1', 25200, -1, None, datetime(2000, 1, 1, 20, 0, 1, 1),
                            datetime(2010, 10, 10, 20, 0, 1, 1))
        a.update(b)
        self.assertEqual(guid, a.uid)
        self.assertEqual(b.name, a.name)
        self.assertEqual(b.ip, a.ip)
        self.assertEqual(b.game_port, a.game_port)
        # Must remain as-is since updated only has a dummy query port value
        self.assertEqual(query_port, a.query_port)
        self.assertEqual(first_seen_at, a.first_seen_at)
        self.assertEqual(b.last_seen_at, a.last_seen_at)
        self.assertEqual(b.last_queried_at, a.last_queried_at)

    def test_load(self):
        guid, name, ip, game_port, query_port = 'a-guid', 'a-server-name', '1.1.1.1', 25200, 47200
        now = datetime.now().astimezone()
        first_seen_at, last_seen_at, last_queried_at = now, now + timedelta(minutes=10), now + timedelta(minutes=5)
        parsed = {'guid': guid, 'name': name, 'ip': ip, 'gamePort': game_port, 'queryPort': query_port,
                  'firstSeenAt': first_seen_at.isoformat(), 'lastSeenAt': last_seen_at.isoformat(),
                  'lastQueriedAt': last_queried_at.isoformat()}
        expect = FrostbiteServer(guid, name, ip, game_port, query_port, first_seen_at, last_seen_at, last_queried_at)
        actual = FrostbiteServer.load(parsed)
        self.assertEqual(expect, actual)

    def test_load_first_seen_at_none(self):
        guid, name, ip, game_port, query_port = 'a-guid', 'a-server-name', '1.1.1.1', 25200, 47200
        now = datetime.now().astimezone()
        first_seen_at, last_seen_at, last_queried_at = None, now + timedelta(minutes=10), now + timedelta(minutes=5)
        parsed = {'guid': guid, 'name': name, 'ip': ip, 'gamePort': game_port, 'queryPort': query_port,
                  'firstSeenAt': first_seen_at, 'lastSeenAt': last_seen_at.isoformat(),
                  'lastQueriedAt': last_queried_at.isoformat()}
        expect = FrostbiteServer(guid, name, ip, game_port, query_port, first_seen_at, last_seen_at, last_queried_at)
        actual = FrostbiteServer.load(parsed)
        self.assertEqual(expect, actual)

    def test_load_last_seen_at_none(self):
        guid, name, ip, game_port, query_port = 'a-guid', 'a-server-name', '1.1.1.1', 25200, 47200
        now = datetime.now().astimezone()
        first_seen_at, last_seen_at, last_queried_at = now, None, now + timedelta(minutes=5)
        parsed = {'guid': guid, 'name': name, 'ip': ip, 'gamePort': game_port, 'queryPort': query_port,
                  'firstSeenAt': first_seen_at.isoformat(), 'lastSeenAt': last_seen_at,
                  'lastQueriedAt': last_queried_at.isoformat()}
        expect = FrostbiteServer(guid, name, ip, game_port, query_port, first_seen_at, UNIX_EPOCH_START,
                                 last_queried_at)
        actual = FrostbiteServer.load(parsed)
        self.assertEqual(expect, actual)

    def test_load_last_queried_at_none(self):
        guid, name, ip, game_port, query_port = 'a-guid', 'a-server-name', '1.1.1.1', 25200, 47200
        now = datetime.now().astimezone()
        first_seen_at, last_seen_at, last_queried_at = now, now + timedelta(minutes=10), None
        parsed = {'guid': guid, 'name': name, 'ip': ip, 'gamePort': game_port, 'queryPort': query_port,
                  'firstSeenAt': first_seen_at.isoformat(), 'lastSeenAt': last_seen_at.isoformat(),
                  'lastQueriedAt': last_queried_at}
        expect = FrostbiteServer(guid, name, ip, game_port, query_port, first_seen_at, last_seen_at, last_queried_at)
        actual = FrostbiteServer.load(parsed)
        self.assertEqual(expect, actual)

    def test_load_last_queried_at_empty(self):
        guid, name, ip, game_port, query_port = 'a-guid', 'a-server-name', '1.1.1.1', 25200, 47200
        now = datetime.now().astimezone()
        first_seen_at, last_seen_at, last_queried_at = now, now + timedelta(minutes=10), ''
        parsed = {'guid': guid, 'name': name, 'ip': ip, 'gamePort': game_port, 'queryPort': query_port,
                  'firstSeenAt': first_seen_at.isoformat(), 'lastSeenAt': last_seen_at.isoformat(),
                  'lastQueriedAt': last_queried_at}
        expect = FrostbiteServer(guid, name, ip, game_port, query_port, first_seen_at, last_seen_at, None)
        actual = FrostbiteServer.load(parsed)
        self.assertEqual(expect, actual)

    def test_is_json_repr_valid(self):
        parsed = {'guid': 'a-guid', 'name': 'a-server-name', 'ip': '1.1.1.1', 'gamePort': 25200, 'queryPort': 47200}
        self.assertTrue(FrostbiteServer.is_json_repr(parsed))

    def test_is_json_repr_guid_missing(self):
        parsed = {'name': 'a-server-name', 'ip': '1.1.1.1', 'gamePort': 25200, 'queryPort': 47200}
        self.assertFalse(FrostbiteServer.is_json_repr(parsed))

    def test_is_json_repr_name_missing(self):
        parsed = {'guid': 'a-guid', 'ip': '1.1.1.1', 'gamePort': 25200, 'queryPort': 47200}
        self.assertFalse(FrostbiteServer.is_json_repr(parsed))

    def test_is_json_repr_ip_missing(self):
        parsed = {'guid': 'a-guid', 'name': 'a-server-name', 'gamePort': 25200, 'queryPort': 47200}
        self.assertFalse(FrostbiteServer.is_json_repr(parsed))

    def test_is_json_repr_game_port_missing(self):
        parsed = {'guid': 'a-guid', 'name': 'a-server-name', 'ip': '1.1.1.1', 'queryPort': 47200}
        self.assertFalse(FrostbiteServer.is_json_repr(parsed))

    def test_is_json_repr_query_port_missing(self):
        parsed = {'guid': 'a-guid', 'name': 'a-server-name', 'ip': '1.1.1.1', 'gamePort': 25200}
        self.assertFalse(FrostbiteServer.is_json_repr(parsed))

    def test_dump(self):
        guid, name, ip, game_port, query_port = 'a-guid', 'a-server-name', '1.1.1.1', 25200, 47200
        now = datetime.now().astimezone()
        first_seen_at, last_seen_at, last_queried_at = now, now + timedelta(minutes=10), now + timedelta(minutes=5)
        server = FrostbiteServer(guid, name, ip, game_port, query_port, first_seen_at, last_seen_at, last_queried_at)
        expect = {'guid': guid, 'name': name, 'ip': ip, 'gamePort': game_port, 'queryPort': query_port, 'links': [],
                  'firstSeenAt': first_seen_at.isoformat(), 'lastSeenAt': last_seen_at.isoformat(),
                  'lastQueriedAt': last_queried_at.isoformat()}
        actual = server.dump()
        self.assertEqual(expect, actual)

    def test_dump_first_seen_at_none(self):
        guid, name, ip, game_port, query_port = 'a-guid', 'a-server-name', '1.1.1.1', 25200, 47200
        now = datetime.now().astimezone()
        first_seen_at, last_seen_at, last_queried_at = None, now + timedelta(minutes=10), now + timedelta(minutes=5)
        server = FrostbiteServer(guid, name, ip, game_port, query_port, first_seen_at, last_seen_at, last_queried_at)
        expect = {'guid': guid, 'name': name, 'ip': ip, 'gamePort': game_port, 'queryPort': query_port, 'links': [],
                  'firstSeenAt': first_seen_at, 'lastSeenAt': last_seen_at.isoformat(),
                  'lastQueriedAt': last_queried_at.isoformat()}
        actual = server.dump()
        self.assertEqual(expect, actual)

    def test_dump_last_queried_at_none(self):
        guid, name, ip, game_port, query_port = 'a-guid', 'a-server-name', '1.1.1.1', 25200, 47200
        now = datetime.now().astimezone()
        first_seen_at, last_seen_at, last_queried_at = now, now + timedelta(minutes=10), None
        server = FrostbiteServer(guid, name, ip, game_port, query_port, first_seen_at, last_seen_at, last_queried_at)
        expect = {'guid': guid, 'name': name, 'ip': ip, 'gamePort': game_port, 'queryPort': query_port, 'links': [],
                  'firstSeenAt': first_seen_at.isoformat(), 'lastSeenAt': last_seen_at.isoformat(),
                  'lastQueriedAt': last_queried_at}
        actual = server.dump()
        self.assertEqual(expect, actual)


class Bfbc2ServerTest(unittest.TestCase):
    def test_load(self):
        guid, name, lid, gid, ip, game_port, query_port = 'a-guid', 'a-server-name', 257, 123456, '1.1.1.1', 25200, 47200
        now = datetime.now().astimezone()
        first_seen_at, last_seen_at, last_queried_at = now, now + timedelta(minutes=10), now + timedelta(minutes=5)
        parsed = {'guid': guid, 'name': name, 'lid': lid, 'gid': gid, 'ip': ip,
                  'gamePort': game_port, 'queryPort': query_port,
                  'firstSeenAt': first_seen_at.isoformat(), 'lastSeenAt': last_seen_at.isoformat(),
                  'lastQueriedAt': last_queried_at.isoformat()}
        expect = BadCompany2Server(guid, name, lid, gid, ip, game_port, query_port, first_seen_at, last_seen_at,
                                   last_queried_at)
        actual = BadCompany2Server.load(parsed)
        self.assertEqual(expect, actual)

    def test_load_first_seen_at_none(self):
        guid, name, lid, gid, ip, game_port, query_port = 'a-guid', 'a-server-name', 257, 123456, '1.1.1.1', 25200, 47200
        now = datetime.now().astimezone()
        first_seen_at, last_seen_at, last_queried_at = None, now + timedelta(minutes=10), now + timedelta(minutes=5)
        parsed = {'guid': guid, 'name': name, 'lid': lid, 'gid': gid, 'ip': ip,
                  'gamePort': game_port, 'queryPort': query_port,
                  'firstSeenAt': first_seen_at, 'lastSeenAt': last_seen_at.isoformat(),
                  'lastQueriedAt': last_queried_at.isoformat()}
        expect = BadCompany2Server(guid, name, lid, gid, ip, game_port, query_port, first_seen_at, last_seen_at,
                                   last_queried_at)
        actual = BadCompany2Server.load(parsed)
        self.assertEqual(expect, actual)

    def test_load_last_seen_at_none(self):
        guid, name, lid, gid, ip, game_port, query_port = 'a-guid', 'a-server-name', 257, 123456, '1.1.1.1', 25200, 47200
        now = datetime.now().astimezone()
        first_seen_at, last_seen_at, last_queried_at = now, None, now + timedelta(minutes=5)
        parsed = {'guid': guid, 'name': name, 'lid': lid, 'gid': gid, 'ip': ip,
                  'gamePort': game_port, 'queryPort': query_port,
                  'firstSeenAt': first_seen_at.isoformat(), 'lastSeenAt': last_seen_at,
                  'lastQueriedAt': last_queried_at.isoformat()}
        expect = BadCompany2Server(guid, name, lid, gid, ip, game_port, query_port, first_seen_at, UNIX_EPOCH_START,
                                   last_queried_at)
        actual = BadCompany2Server.load(parsed)
        self.assertEqual(expect, actual)

    def test_load_last_queried_at_none(self):
        guid, name, lid, gid, ip, game_port, query_port = 'a-guid', 'a-server-name', 257, 123456, '1.1.1.1', 25200, 47200
        now = datetime.now().astimezone()
        first_seen_at, last_seen_at, last_queried_at = now, now + timedelta(minutes=10), None
        parsed = {'guid': guid, 'name': name, 'lid': lid, 'gid': gid, 'ip': ip,
                  'gamePort': game_port, 'queryPort': query_port,
                  'firstSeenAt': first_seen_at.isoformat(), 'lastSeenAt': last_seen_at.isoformat(),
                  'lastQueriedAt': last_queried_at}
        expect = BadCompany2Server(guid, name, lid, gid, ip, game_port, query_port, first_seen_at, last_seen_at,
                                   last_queried_at)
        actual = BadCompany2Server.load(parsed)
        self.assertEqual(expect, actual)

    def test_load_lid_missing(self):
        guid, name, lid, gid, ip, game_port, query_port = 'a-guid', 'a-server-name', -1, 123456, '1.1.1.1', 25200, 47200
        now = datetime.now().astimezone()
        first_seen_at, last_seen_at, last_queried_at = now, now + timedelta(minutes=10), now + timedelta(minutes=5)
        parsed = {'guid': guid, 'name': name, 'gid': gid, 'ip': ip,
                  'gamePort': game_port, 'queryPort': query_port,
                  'firstSeenAt': first_seen_at.isoformat(), 'lastSeenAt': last_seen_at.isoformat(),
                  'lastQueriedAt': last_queried_at.isoformat()}
        expect = BadCompany2Server(guid, name, lid, gid, ip, game_port, query_port, first_seen_at, last_seen_at,
                                   last_queried_at)
        actual = BadCompany2Server.load(parsed)
        self.assertEqual(expect, actual)

    def test_load_gid_missing(self):
        guid, name, lid, gid, ip, game_port, query_port = 'a-guid', 'a-server-name', 257, -1, '1.1.1.1', 25200, 47200
        now = datetime.now().astimezone()
        first_seen_at, last_seen_at, last_queried_at = now, now + timedelta(minutes=10), now + timedelta(minutes=5)
        parsed = {'guid': guid, 'name': name, 'lid': lid, 'ip': ip,
                  'gamePort': game_port, 'queryPort': query_port,
                  'firstSeenAt': first_seen_at.isoformat(), 'lastSeenAt': last_seen_at.isoformat(),
                  'lastQueriedAt': last_queried_at.isoformat()}
        expect = BadCompany2Server(guid, name, lid, gid, ip, game_port, query_port, first_seen_at, last_seen_at,
                                   last_queried_at)
        actual = BadCompany2Server.load(parsed)
        self.assertEqual(expect, actual)

    def test_dump(self):
        guid, name, lid, gid, ip, game_port, query_port = 'a-guid', 'a-server-name', 257, 123456, '1.1.1.1', 25200, 47200
        now = datetime.now().astimezone()
        first_seen_at, last_seen_at, last_queried_at = now, now + timedelta(minutes=10), now + timedelta(minutes=5)
        server = BadCompany2Server(guid, name, lid, gid, ip, game_port, query_port, first_seen_at, last_seen_at,
                                   last_queried_at)
        expect = {'guid': guid, 'name': name, 'lid': lid, 'gid': gid, 'ip': ip,
                  'gamePort': game_port, 'queryPort': query_port, 'links': [],
                  'firstSeenAt': first_seen_at.isoformat(), 'lastSeenAt': last_seen_at.isoformat(),
                  'lastQueriedAt': last_queried_at.isoformat()}
        actual = server.dump()
        self.assertEqual(expect, actual)

    def test_dump_first_seen_at_none(self):
        guid, name, lid, gid, ip, game_port, query_port = 'a-guid', 'a-server-name', 257, 123456, '1.1.1.1', 25200, 47200
        now = datetime.now().astimezone()
        first_seen_at, last_seen_at, last_queried_at = None, now + timedelta(minutes=10), now + timedelta(minutes=5)
        server = BadCompany2Server(guid, name, lid, gid, ip, game_port, query_port, first_seen_at, last_seen_at,
                                   last_queried_at)
        expect = {'guid': guid, 'name': name, 'lid': lid, 'gid': gid, 'ip': ip,
                  'gamePort': game_port, 'queryPort': query_port, 'links': [],
                  'firstSeenAt': first_seen_at, 'lastSeenAt': last_seen_at.isoformat(),
                  'lastQueriedAt': last_queried_at.isoformat()}
        actual = server.dump()
        self.assertEqual(expect, actual)

    def test_dump_last_queried_at_none(self):
        guid, name, lid, gid, ip, game_port, query_port = 'a-guid', 'a-server-name', 257, 123456, '1.1.1.1', 25200, 47200
        now = datetime.now().astimezone()
        first_seen_at, last_seen_at, last_queried_at = now, now + timedelta(minutes=10), None
        server = BadCompany2Server(guid, name, lid, gid, ip, game_port, query_port, first_seen_at, last_seen_at,
                                   last_queried_at)
        expect = {'guid': guid, 'name': name, 'lid': lid, 'gid': gid, 'ip': ip,
                  'gamePort': game_port, 'queryPort': query_port, 'links': [],
                  'firstSeenAt': first_seen_at.isoformat(), 'lastSeenAt': last_seen_at.isoformat(),
                  'lastQueriedAt': last_queried_at}
        actual = server.dump()
        self.assertEqual(expect, actual)


class GametoolsServerTest(unittest.TestCase):
    def test_update(self):
        game_id, name, first_seen_at = 'a-game-id', 'a-server-name', datetime.now().astimezone()
        a = GametoolsServer(game_id, name, first_seen_at)
        b = GametoolsServer('b-game-id', 'b-server-name', None, datetime(2000, 1, 1, 12, 12))
        a.update(b)
        self.assertEqual(game_id, a.uid)
        self.assertEqual(b.name, a.name)
        self.assertEqual(first_seen_at, a.first_seen_at)
        self.assertEqual(b.last_seen_at, a.last_seen_at)

    def test_load(self):
        game_id, name = 'a-game-id', 'a-server-name'
        now = datetime.now().astimezone()
        first_seen_at, last_seen_at = now, now + timedelta(minutes=10)
        parsed = {'gameId': game_id, 'name': name,
                  'firstSeenAt': first_seen_at.isoformat(), 'lastSeenAt': last_seen_at.isoformat()}
        expect = GametoolsServer(game_id, name, first_seen_at, last_seen_at)
        actual = GametoolsServer.load(parsed)
        self.assertEqual(expect, actual)

    def test_load_first_seen_at_none(self):
        game_id, name = 'a-game-id', 'a-server-name'
        now = datetime.now().astimezone()
        first_seen_at, last_seen_at = None, now + timedelta(minutes=10)
        parsed = {'gameId': game_id, 'name': name,
                  'firstSeenAt': first_seen_at, 'lastSeenAt': last_seen_at.isoformat()}
        expect = GametoolsServer(game_id, name, first_seen_at, last_seen_at)
        actual = GametoolsServer.load(parsed)
        self.assertEqual(expect, actual)

    def test_load_last_seen_at_none(self):
        game_id, name = 'a-game-id', 'a-server-name'
        now = datetime.now().astimezone()
        first_seen_at = now
        parsed = {'gameId': game_id, 'name': name,
                  'firstSeenAt': first_seen_at.isoformat(), 'lastSeenAt': None}
        expect = GametoolsServer(game_id, name, first_seen_at, UNIX_EPOCH_START)
        actual = GametoolsServer.load(parsed)
        self.assertEqual(expect, actual)

    def test_is_json_repr_valid(self):
        parsed = {'gameId': 'a-game-id', 'name': 'a-server-name'}
        self.assertTrue(GametoolsServer.is_json_repr(parsed))

    def test_is_json_repr_game_id_missing(self):
        parsed = {'name': 'a-server-name'}
        self.assertFalse(GametoolsServer.is_json_repr(parsed))

    def test_is_json_repr_name_missing(self):
        parsed = {'name': 'a-server-name'}
        self.assertFalse(GametoolsServer.is_json_repr(parsed))


if __name__ == '__main__':
    unittest.main()
