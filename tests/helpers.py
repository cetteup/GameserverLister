import unittest

from GameserverLister.common.helpers import is_valid_public_ip, is_valid_port, battlelog_server_validator, \
    bfbc2_server_validator, guid_from_ip_port
from GameserverLister.common.servers import FrostbiteServer, BadCompany2Server


class IsValidPublicIPTest(unittest.TestCase):
    def test_public_valid(self):
        self.assertTrue(is_valid_public_ip('1.1.1.1'))

    def test_localhost(self):
        self.assertFalse(is_valid_public_ip('127.0.0.1'))

    def test_private(self):
        self.assertFalse(is_valid_public_ip('192.168.1.1'))

    def test_link_local(self):
        self.assertFalse(is_valid_public_ip('169.254.1.1'))

    def test_invalid(self):
        self.assertFalse(is_valid_public_ip('not-an-ip-address'))


class IsValidPortTest(unittest.TestCase):
    def test_valid(self):
        self.assertTrue(is_valid_port(443))

    def test_low(self):
        self.assertFalse(is_valid_port(0))

    def test_high(self):
        self.assertFalse(is_valid_port(65536))


class ServerValidatorTest(unittest.TestCase):
    def test_battlelog_valid(self):
        ip, game_port = '1.1.1.1', 25200
        server = FrostbiteServer('a-guid', 'a-server-name', ip, game_port, 47200)
        parsed_result = {'connect': f'{ip}:{game_port}'}
        valid = battlelog_server_validator(server, -1, parsed_result)
        self.assertTrue(valid)

    def test_battlelog_ip_mismatch(self):
        ip, game_port = '1.1.1.1', 25200
        server = FrostbiteServer('a-guid', 'a-server-name', ip, game_port, 47200)
        parsed_result = {'connect': f'1.0.0.1:{game_port}'}
        valid = battlelog_server_validator(server, -1, parsed_result)
        self.assertFalse(valid)

    def test_battlelog_port_mismatch(self):
        ip, game_port = '1.1.1.1', 25200
        server = FrostbiteServer('a-guid', 'a-server-name', ip, game_port, 47200)
        parsed_result = {'connect': f'{ip}:{game_port + 1}'}
        valid = battlelog_server_validator(server, -1, parsed_result)
        self.assertFalse(valid)

    def test_battlelog_invalid_result(self):
        ip, game_port = '1.1.1.1', 25200
        server = FrostbiteServer('a-guid', 'a-server-name', ip, game_port, 47200)
        parsed_result = {}
        valid = battlelog_server_validator(server, -1, parsed_result)
        self.assertFalse(valid)

    def test_bfbcb2_valid_battlelog(self):
        name, ip, game_port = 'a-server-name', '1.1.1.1', 19567
        server = BadCompany2Server('a-guid', name, 257, 123456, ip, game_port, 48888)
        parsed_result = {'connect': f'{ip}:{game_port}', 'name': name}
        valid = bfbc2_server_validator(server, -1, parsed_result)
        self.assertTrue(valid)

    def test_bfbcb2_valid_any_ip(self):
        name, ip, game_port = 'a-server-name', '1.1.1.1', 19567
        server = BadCompany2Server('a-guid', name, 257, 123456, ip, game_port, 48888)
        parsed_result = {'connect': f'0.0.0.0:{game_port}', 'name': name}
        valid = bfbc2_server_validator(server, -1, parsed_result)
        self.assertTrue(valid)

    def test_bfbcb2_valid_name(self):
        name, ip, game_port = 'a-server-name', '1.1.1.1', 19567
        server = BadCompany2Server('a-guid', name, 257, 123456, ip, game_port, 48888)
        parsed_result = {'connect': f'0.0.0.0:{game_port + 1}', 'name': name}
        valid = bfbc2_server_validator(server, -1, parsed_result)
        self.assertTrue(valid)

    def test_bfbcb2_ip_name_mismatch(self):
        name, ip, game_port = 'a-server-name', '1.1.1.1', 19567
        server = BadCompany2Server('a-guid', name, 257, 123456, ip, game_port, 48888)
        parsed_result = {'connect': f'1.0.0.1:{game_port}', 'name': 'different-name'}
        valid = bfbc2_server_validator(server, -1, parsed_result)
        self.assertFalse(valid)

    def test_bfbcb2_port_name_mismatch(self):
        name, ip, game_port = 'a-server-name', '1.1.1.1', 19567
        server = BadCompany2Server('a-guid', name, 257, 123456, ip, game_port, 48888)
        parsed_result = {'connect': f'{ip}:{game_port + 1}', 'name': 'different-name'}
        valid = bfbc2_server_validator(server, -1, parsed_result)
        self.assertFalse(valid)

    def test_bfbcb2_invalid_parsed_result(self):
        name, ip, game_port = 'a-server-name', '1.1.1.1', 19567
        server = BadCompany2Server('a-guid', name, 257, 123456, ip, game_port, 48888)
        parsed_result = {}
        valid = bfbc2_server_validator(server, -1, parsed_result)
        self.assertFalse(valid)


class GuidTest(unittest.TestCase):
    def test_guid_from_ip_port(self):
        actual = guid_from_ip_port('1.1.1.1', '443')
        self.assertEqual('1f2-1f2-1f2-1f2', actual)


if __name__ == '__main__':
    unittest.main()
