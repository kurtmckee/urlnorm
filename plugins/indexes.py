# indexes.py - A urlnorm.py plugin: remove directory indexes
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

_DIRECTORY_INDEXES = (
    'index.htm', 'index.html', 'index.php', 'index.jsp',
    'default.asp', 'default.aspx',
)

def plugfn(parts):
    if parts['path']:
        newpath = parts['path'].rsplit('/', 1)
        if newpath[-1] in _DIRECTORY_INDEXES:
            parts['path'] = newpath[0] + '/'
    return parts

if __name__ == '__main__':
    import unittest
    import sys

    def make_testcase(*args):
        return lambda self: self.worker(*args)

    class TestPluginIndexes(unittest.TestCase):
        def worker(self, parts, expected):
            self.assertEqual(plugfn(parts)['path'], expected)

    pathtests = (
        ('/', '/'),
        ('/index.html', '/'),
        ('/index.html/', '/index.html/'),
        ('/index.php/blog/entry/', '/index.php/blog/entry/'),
        ('/skip-index.html', '/skip-index.html'),
    )

    for i in range(len(pathtests)):
        testcase = make_testcase({'path': pathtests[i][0]}, pathtests[i][1])
        testcase.__doc__ = 'plugin_indexes %02i: %s' % (i, pathtests[i][0])
        setattr(TestPluginIndexes, 'test_plugin_indexes_%02i' % i, testcase)

    testsuite = unittest.TestSuite()
    testloader = unittest.TestLoader()
    testsuite.addTest(testloader.loadTestsFromTestCase(TestPluginIndexes))
    testresults = unittest.TextTestRunner(verbosity=1).run(testsuite)
    sys.exit(not testresults.wasSuccessful())
