# urlnorm.py - Normalize URLs
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

__author__ = "Kurt McKee <contactme@kurtmckee.org>"

import re
import urllib
import urlparse

try:
    from urlparse import parse_qsl
except ImportError:
    from cgi import parse_qsl

DEFAULT_PORTS = {
    'http': u'80',
    'https': u'443',
    'ftp': u'21',
}

NETLOC = re.compile("""
    ^
    (?:
        (?P<username>[^:@]+)?
        (?:
            :
            (?P<password>[^@]*)
        )?
        @
    )?
    (?P<hostname>[^:]+)
    (?:
        :
        (?P<port>[0-9]*)
    )?
    $
    """, re.VERBOSE,
)

PERCENT_ENCODING = re.compile("%([0-9a-f]{2})", re.IGNORECASE)

# http://www.pc-help.org/obscure.htm
# http://www.securelist.com/en/blog/148/
# Translate the IP address from octal, decimal, and hex
# into a base 10 quadruple octet (like 127.0.0.1)
NUMERIC_IP = re.compile("""
    ^
    (?:
        (?P<o0>(?:[0-9]+)|(?:0x[0-9a-f]+))
        [.]
    )?
    (?:
        (?P<o1>(?:[0-9]+)|(?:0x[0-9a-f]+))
        [.]
    )?
    (?:
        (?P<o2>(?:[0-9]+)|(?:0x[0-9a-f]+))
        [.]
    )?
    (?P<o3>(?:[0-9]+)|(?:0x[0-9a-f]+))
    $
    """, re.VERBOSE | re.IGNORECASE
)

def urlnorm(url, base=None):
    if base is not None:
        url = urlparse.urljoin(base, url)
    url = _normalize_percent_encoding(url)
    parts = _urlparse(url)
    parts.update(_split_netloc(parts['netloc']))
    parts['scheme'] = _normalize_scheme(parts['scheme'])
    parts['port'] = _normalize_port(parts['port'], parts['scheme'])
    parts['path'] = _normalize_path(parts['path'])
    parts['hostname'] = _normalize_hostname(parts.get('hostname', ''))
    parts['query'] = _normalize_query(parts['query'])
    print parts #['query']
    return _join_parts(parts)

def _urlparse(url):
    parts = dict(zip(('scheme', 'netloc', 'path', 'params', 'query', 'fragment'),
                     urlparse.urlparse(url)
                ))
    if parts['scheme'].lower() == 'mailto':
        parts = dict(zip(('scheme', 'netloc', 'path', 'params', 'query', 'fragment'),
                         urlparse.urlparse('http://%s' % parts['path'])
                    ))
        parts['scheme'] = 'mailto'
    elif (not parts['scheme'] and not parts['netloc']) or \
        (parts['path'] and not parts['path'].startswith('/') and url.startswith('%s:%s' % (parts['scheme'], parts['path']))):
        # url may not have included a scheme, like 'domain.example'
        # url may have been in the form 'domain.example:8080'
        parts = dict(zip(('scheme', 'netloc', 'path', 'params', 'query', 'fragment'),
                         urlparse.urlparse('http://%s' % url)
                    ))
    return parts

def _join_parts(parts):
    if parts['scheme'] != 'mailto':
        url = '%s://' % parts['scheme']
    else:
        url = '%s:' % parts['scheme']
    if parts['username']:
        url += parts['username']
        if parts['password']:
            url += ':%s' % parts['password']
        url += '@'
    url += parts['hostname']
    if parts['port']:
        url += ':%s' % parts['port']
    if parts['scheme'] != 'mailto':
        url += parts['path']
    if parts['parameters']:
        url += ';%s' % parts['parameters']
    if parts['query']:
        url += '?%s' % parts['query']
    if parts['fragment']:
        url += '#%s' % parts['fragment']
    return url

def _split_netloc(netloc):
    parts_netloc = NETLOC.match(netloc)
    if parts_netloc is not None:
        return parts_netloc.groupdict()
    return {'username': '', 'password': '', 'hostname': '', 'port': ''}

def _normalize_scheme(scheme):
    return scheme.lower() or 'http'

def _normalize_port(port, scheme):
    if scheme in DEFAULT_PORTS and DEFAULT_PORTS[scheme] == port:
        return ''
    return port

def _normalize_percent_encoding(txt):
    unreserved = u'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_.~'
    def repl(hexpair):
        if unichr(int(hexpair.group(1), 16)) in unreserved:
            return unichr(int(hexpair.group(1), 16))
        return u'%%%s' % hexpair.group(1).upper()
    return re.sub(PERCENT_ENCODING, repl, txt)

def _normalize_hostname(hostname):
    hostname = hostname.lower()
    if hostname.endswith('.'):
        hostname = hostname[:-1]
    ip = NUMERIC_IP.match(hostname)
    if ip is not None:
        ip = filter(None, ip.groups())
        decimal_ip = 0
        for i in range(len(ip)):
            base = (10, 8, 16)[(ip[i][0:1] == '0') + (ip[i][1:2] == 'x')]
            decimal_ip += (
                (long(ip[i] or '0', base) &
                (256**[1, 4-i][len(ip)==i+1]-1)) <<
                (8*[3-i, 0][len(ip)==i+1])
            )
        new_ip = '.'.join([unicode((decimal_ip >> (8*octet)) & 255) for octet in (3, 2, 1, 0)])
        hostname = new_ip
    return hostname

def _normalize_path(path):
    path = path.split('/')
    endslash = False
    if path[-1] == '':
        endslash = True
    path = filter(None, path)
    pos = 0
    for i in range(len(path)):
        if path[i] == '.':
            path[i] = None
        elif path[i] == '..':
            path[pos] = None
            if pos > 0:
                pos -= 1
            path[i] = None
        elif path[i]:
            path[pos] = path[i]
            if pos < i:
                path[i] = None
            pos += 1
    path.insert(0, '')
    if endslash:
        path.append('')
    return '/'.join(filter(lambda x: x is not None, path)) or '/'

def _normalize_query(query):
    _no_filter = lambda (k, v): True
    _filter = lambda (k, v): bool(v)
    queries = parse_qsl(query, keep_blank_values=True)
    queries = filter(_no_filter, queries)
    queries.sort()
    return urllib.urlencode(queries, True)
