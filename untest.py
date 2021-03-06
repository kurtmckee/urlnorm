# untest.py - Run unit tests against urlnorm.py
# Copyright (C) 2010 Kurt McKee <contactme@kurtmckee.org>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest
import sys

import urlnorm

def make_testcase(*args):
    return lambda self: self.worker(*args)

class TestHostname(unittest.TestCase):
    def worker(self, hostname, result):
        self.assertEqual(urlnorm._normalize_hostname(hostname), result)

hostnames = (
    ('domain.test', 'domain.test'),
    ('DOMAIN.TEST', 'domain.test'),
    ('domain.test.', 'domain.test'),
    # IP addresses (dotted decimal, octal, hex)
    ('12.43.56.87', '12.43.56.87'),
    ('014.053.070.0127', '12.43.56.87'),
    ('0xC.0x2B.0x38.0x57', '12.43.56.87'),
    ('0xc.0x2b.0x38.0x57', '12.43.56.87'),
    # IP addresses (with fewer than four octets)
    ('12.43.14423', '12.43.56.87'),
    ('12.2832471', '12.43.56.87'),
    ('204159063', '12.43.56.87'),
    ('014.053.034127', '12.43.56.87'),
    ('014.012634127', '12.43.56.87'),
    ('01412634127', '12.43.56.87'),
    ('0xc.0x2b.0x3857', '12.43.56.87'),
    ('0xc.0x2b3857', '12.43.56.87'),
    ('0xC2B3857', '12.43.56.87'),
    # IP addresses (zero-padded)
    ('00014.00053.00070.000127', '12.43.56.87'),
    ('0x000C.0x0002B.0x00038.0x00057', '12.43.56.87'),
    ('00001412634127', '12.43.56.87'),
    ('0x000C2B3857', '12.43.56.87'),
    # IP addresses (with 7*256^4 added)
    ('30268930135', '12.43.56.87'),
    ('0341412634127', '12.43.56.87'),
    ('0x70C2B3857', '12.43.56.87'),
    # IP addresses (with 2*256 added to each octet)
    ('524.555.568.599', '12.43.56.87'),
    ('01014.01053.01070.01127', '12.43.56.87'),
    ('0x20C.0x22B.0x238.0x257', '12.43.56.87'),
    # Domain with only hex characters (.ee is a valid TLD)
    ('ab.cd.ee.ee', 'ab.cd.ee.ee'),
)
for i in range(len(hostnames)):
    testcase = make_testcase(hostnames[i][0], hostnames[i][1])
    testcase.__doc__ = 'hostname %02i: %s' % (i, hostnames[i][0])
    setattr(TestHostname, 'test_hostname_%02i' % i, testcase)

class TestPath(unittest.TestCase):
    def worker(self, path, result):
        self.assertEqual(urlnorm._normalize_path(path), result)

paths = (
    ('', '/'),
    ('/', '/'),
    ('/.', '/'),
    ('/./', '/'),
    ('/..', '/'),
    ('/../', '/'),
    ('/blog', '/blog'),
    ('/blog/', '/blog/'),
    ('/a/./b/', '/a/b/'),
    ('/a/../b/', '/b/'),
)
for i in range(len(paths)):
    testcase = make_testcase(paths[i][0], paths[i][1])
    testcase.__doc__ = 'path %02i: %s' % (i, paths[i][0])
    setattr(TestPath, 'test_path_%02i' % i, testcase)

class TestScheme(unittest.TestCase):
    def worker(self, scheme, result):
        self.assertEqual(urlnorm._normalize_scheme(scheme), result)

schemes = (
    ('', 'http'),
    ('http', 'http'),
    ('HTTP', 'http'),
)
for i in range(len(schemes)):
    testcase = make_testcase(schemes[i][0], schemes[i][1])
    testcase.__doc__ = 'scheme %02i: %s' % (i, schemes[i][0])
    setattr(TestScheme, 'test_scheme_%02i' % i, testcase)

class TestPort(unittest.TestCase):
    def worker(self, port, scheme, result):
        self.assertEqual(urlnorm._normalize_port(port, scheme), result)

ports = (
    ('', '', ''),
    ('80', 'http', ''),
    ('81', 'http', '81'),
)
for i in range(len(ports)):
    testcase = make_testcase(*ports[i])
    testcase.__doc__ = 'port %02i: %s' % (i, ports[i][0])
    setattr(TestPort, 'test_port_%02i' % i, testcase)

class TestQuery(unittest.TestCase):
    def worker(self, query, result):
        self.assertEqual(urlnorm._join_query(urlnorm._split_query(query)), result)

queries = (
    # Basics
    ('', ''),
    ('a', 'a'),
    ('a=', 'a='),
    ('a=1', 'a=1'),
    # Sorting
    ('a=1&a=', 'a=&a=1'),
    ('a=1&a=1', 'a=1&a=1'),
    ('a=1&b=2', 'a=1&b=2'),
    ('a=2&a=1', 'a=1&a=2'),
    ('b=1&a=2', 'a=2&b=1'),
    # Escaping
    ('^', '%5E'),
    ('^=', '%5E='),
    ('^=^', '%5E=%5E'),
    ('a==', 'a=%3D'),
    ('/feeds/rss', '/feeds/rss'),
)
for i in range(len(queries)):
    testcase = make_testcase(queries[i][0], queries[i][1])
    testcase.__doc__ = 'query %02i: %s' % (i, queries[i][0])
    setattr(TestQuery, 'test_query_%02i' % i, testcase)

class TestNetlocSplit(unittest.TestCase):
    def testEmpty(self):
        self.assertEqual(urlnorm._split_netloc(''),
            {'username': '', 'password': '', 'hostname': '', 'port': ''})
    def worker(self, netloc, expected):
        result = urlnorm._split_netloc(netloc)
        for k in expected:
            self.assertTrue(k in result)
            self.assertEqual(result[k], expected[k])

netlocs = (
    ('domain.test', {'hostname': 'domain.test'}),
    ('domain.test:81', {'port': '81', 'hostname': 'domain.test'}),
    ('user@domain.test', {'username': 'user', 'hostname': 'domain.test'}),
    ('user:@domain.test', {'username': 'user', 'password': '', 'hostname': 'domain.test'}),
    ('user:pass@domain.test', {'username': 'user', 'password': 'pass', 'hostname': 'domain.test'}),
    ('user:pass@domain.test:81', {'port': '81', 'username': 'user', 'password': 'pass', 'hostname': 'domain.test'}),
)
for i in range(len(netlocs)):
    testcase = make_testcase(netlocs[i][0], netlocs[i][1])
    testcase.__doc__ = 'netloc %02i: %s' % (i, netlocs[i][0])
    setattr(TestNetlocSplit, 'test_netloc_%02i' % i, testcase)

class TestURLParse(unittest.TestCase):
    def worker(self, url, expected):
        result = urlnorm._urlparse(url)
        for k in expected:
            self.assertTrue(k in result)
            self.assertEqual(result[k], expected[k])

urlparses = (
    ('http://domain.test/', {'scheme': 'http', 'path': '/', 'netloc': 'domain.test'}),
    ('http://domain.test', {'scheme': 'http', 'path': '', 'netloc': 'domain.test'}),
    ('domain.test/', {'scheme': 'http', 'path': '/', 'netloc': 'domain.test'}),
    ('domain.test', {'scheme': 'http', 'path': '', 'netloc': 'domain.test'}),
    ('domain.test:8080/', {'scheme': 'http', 'path': '/', 'netloc': 'domain.test:8080'}),
    ('domain.test:8080', {'scheme': 'http', 'path': '', 'netloc': 'domain.test:8080'}),
)
for i in range(len(urlparses)):
    testcase = make_testcase(urlparses[i][0], urlparses[i][1])
    testcase.__doc__ = 'urlparse %02i: %s' % (i, urlparses[i])
    setattr(TestURLParse, 'test_urlparse_%02i' % i, testcase)

# Test the entire urlnorm() pipeline

class TestURLNorm(unittest.TestCase):
    def worker(self, args, expected):
        self.assertEqual(urlnorm.urlnorm(*args), expected)
fullurls = (
    (("javascript:alert('')",), "javascript:alert('')"),
    (("irc://domain.test/room",), "irc://domain.test/room"),
    (("feed:http://domain/feed",), "http://domain/feed"),
    (("http://d/#",), "http://d/"),
    (("http://d/?",), "http://d/"),
    # Test whitespace stripping
    ((" http://d/p/ ",), "http://d/p/"),
    ((" p ", " http://d2/ "), "http://d2/p"),
    (("http://d/\r1/\n2\r\n/3",), "http://d/1/2/3"),
)
for i in range(len(fullurls)):
    testcase = make_testcase(fullurls[i][0], fullurls[i][1])
    testcase.__doc__ = 'fullurls %02i: %s' % (i, fullurls[i])
    setattr(TestURLNorm, 'test_fullurls_%02i' % i, testcase)

class TestPrePluginHook(unittest.TestCase):
    def _plugfn(self, url):
        return 'http://x/'
    def setUp(self):
        urlnorm.register_pre_plugin(self._plugfn)
    def tearDown(self):
        urlnorm._pre_plugins = []
    def testPostPluginHook(self):
        self.assertEqual(urlnorm.urlnorm('http://d/'), 'http://x/')

class TestPostPluginHook(unittest.TestCase):
    def _plugfn(self, parts):
        parts['path'] += 'ath'
        return parts
    def setUp(self):
        urlnorm.register_post_plugin(self._plugfn)
    def tearDown(self):
        urlnorm._post_plugins = []
    def testPostPluginHook(self):
        self.assertEqual(urlnorm.urlnorm('http://d/p'), 'http://d/path')

# Load all of the testcases into a single testsuite
testsuite = unittest.TestSuite()
testloader = unittest.TestLoader()
testsuite.addTest(testloader.loadTestsFromTestCase(TestHostname))
testsuite.addTest(testloader.loadTestsFromTestCase(TestPath))
testsuite.addTest(testloader.loadTestsFromTestCase(TestScheme))
testsuite.addTest(testloader.loadTestsFromTestCase(TestPort))
testsuite.addTest(testloader.loadTestsFromTestCase(TestQuery))
testsuite.addTest(testloader.loadTestsFromTestCase(TestNetlocSplit))
testsuite.addTest(testloader.loadTestsFromTestCase(TestURLParse))
testsuite.addTest(testloader.loadTestsFromTestCase(TestURLNorm))
testsuite.addTest(testloader.loadTestsFromTestCase(TestPrePluginHook))
testsuite.addTest(testloader.loadTestsFromTestCase(TestPostPluginHook))
testresults = unittest.TextTestRunner(verbosity=1).run(testsuite)

# Return 0 if successful, 1 if there was a failure
sys.exit(not testresults.wasSuccessful())
