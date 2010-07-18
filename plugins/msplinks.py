# msplinks.py - A urlnorm.py plugin: fix msplinks obfuscated URLs
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

import base64
import binascii

def plugfn(url):
    split = url.split('msplinks.com/')
    if split[0] in ('', 'www.', 'http://', 'http://www.') and split[1]:
        try:
            return base64.decodestring(split[1])[2:]
        except binascii.Error:
            pass
    return url

if __name__ == '__main__':
    import unittest
    import sys

    def make_testcase(*args):
        return lambda self: self.worker(*args)

    class TestPluginMsplinks(unittest.TestCase):
        def worker(self, url, expected):
            self.assertEqual(plugfn(url), expected)

    plgtests = (
        # Make sure these pass through unaltered
        ('msplinks.com/', 'msplinks.com/'),
        ('http://msplinks.com', 'http://msplinks.com'),
        ('http://msplinks.com/', 'http://msplinks.com/'),
        # Valid examples
        ('msplinks.com/MDFodHRwOi8vcGhvdG9idWNrZXQuY29t',
            'http://photobucket.com'),
        ('www.msplinks.com/MDFodHRwOi8vcGhvdG9idWNrZXQuY29t',
            'http://photobucket.com'),
        ('http://msplinks.com/MDFodHRwOi8vcGhvdG9idWNrZXQuY29t',
            'http://photobucket.com'),
        ('http://www.msplinks.com/MDFodHRwOi8vcGhvdG9idWNrZXQuY29t',
            'http://photobucket.com'),
        # An invalid example (base64 cannot be decoded)
        ('http://www.msplinks.com/123fake',
            'http://www.msplinks.com/123fake'),
    )

    for i in range(len(plgtests)):
        testcase = make_testcase(plgtests[i][0], plgtests[i][1])
        testcase.__doc__ = 'plugin_msplinks %02i: %s' % (i, plgtests[i][0])
        setattr(TestPluginMsplinks, 'test_plugin_msplinks_%02i' % i, testcase)

    testsuite = unittest.TestSuite()
    testloader = unittest.TestLoader()
    testsuite.addTest(testloader.loadTestsFromTestCase(TestPluginMsplinks))
    testresults = unittest.TextTestRunner(verbosity=1).run(testsuite)
    sys.exit(not testresults.wasSuccessful())
