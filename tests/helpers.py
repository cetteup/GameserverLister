import unittest

from GameserverLister.common.helpers import is_valid_public_ip, is_valid_port, guid_from_ip_port


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


class GuidFromIpPortTest(unittest.TestCase):
    def test_normal(self):
        actual = guid_from_ip_port('1.1.1.1', '443')
        self.assertEqual('1f2-1f2-1f2-1f2', actual)

    def test_zero(self):
        actual = guid_from_ip_port('0.0.0.0', '0')
        self.assertEqual('0-0-0-0', actual)


if __name__ == '__main__':
    unittest.main()
