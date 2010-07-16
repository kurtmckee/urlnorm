# nowww.py - A urlnorm.py plugin: remove www from domain name
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

def plugfn(parts):
    if parts['hostname'].startswith('www.'):
        parts['hostname'] = parts['hostname'][4:]
    return parts

if __name__ == '__main__':
    import unittest
    import sys

    def make_testcase(*args):
        return lambda self: self.worker(*args)

    class TestPluginNoWWW(unittest.TestCase):
        def worker(self, parts, expected):
            self.assertEqual(plugfn(parts)['hostname'], expected)

    pathtests = (
        ('dom.test', 'dom.test'),
        ('www.dom.test', 'dom.test'),
        ('www2.dom.test', 'www2.dom.test'),
    )

    for i in range(len(pathtests)):
        testcase = make_testcase({'hostname': pathtests[i][0]}, pathtests[i][1])
        testcase.__doc__ = 'plugin_nowww %02i: %s' % (i, pathtests[i][0])
        setattr(TestPluginNoWWW, 'test_plugin_nowww_%02i' % i, testcase)

    testsuite = unittest.TestSuite()
    testloader = unittest.TestLoader()
    testsuite.addTest(testloader.loadTestsFromTestCase(TestPluginNoWWW))
    testresults = unittest.TextTestRunner(verbosity=1).run(testsuite)
    sys.exit(not testresults.wasSuccessful())
