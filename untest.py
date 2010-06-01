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

def make_testcase(arg, expected):
    return lambda self: self.worker(arg, expected)

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
    # Domain with only hex characters
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
    testcase.__doc__ = 'hostname %02i: %s' % (i, paths[i][0])
    setattr(TestPath, 'test_hostname_%02i' % i, testcase)

testsuite = unittest.TestSuite()
testloader = unittest.TestLoader()
testsuite.addTest(testloader.loadTestsFromTestCase(TestHostname))
testsuite.addTest(testloader.loadTestsFromTestCase(TestPath))
testresults = unittest.TextTestRunner(verbosity=1).run(testsuite)

# Return 0 if successful, 1 if there was a failure
sys.exit(not testresults.wasSuccessful())
