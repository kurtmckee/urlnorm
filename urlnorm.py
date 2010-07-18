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

DEFAULT_PORTS = {
    'http': u'80',
    'https': u'443',
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
UNACCEPTABLE_QUERY_CHARS = re.compile("([^A-Za-z0-9_.~/-])")

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

_pre_plugins = []
_post_plugins = []

def register_pre_plugin(fn):
    _pre_plugins.append(fn)
def register_post_plugin(fn):
    _post_plugins.append(fn)

def urlnorm(url, base=None):
    newurl = url.strip()
    newurl = ''.join((v for u in newurl.split('\n') for v in u.split('\r')))
    if newurl.lower().startswith('feed:'):
        newurl = newurl[5:]
    if base is not None:
        newurl = urlparse.urljoin(base.strip(), newurl)
    for fn in _pre_plugins:
        newurl = fn(newurl)
    newurl = _normalize_percent_encoding(newurl)
    parts = _urlparse(newurl)
    if parts is None:
        return url
    parts.update(_split_netloc(parts['netloc']))
    parts['scheme'] = _normalize_scheme(parts['scheme'])
    parts['port'] = _normalize_port(parts['port'], parts['scheme'])
    parts['path'] = _normalize_path(parts['path'])
    parts['hostname'] = _normalize_hostname(parts.get('hostname', ''))
    parts['query'] = _split_query(parts['query'])
    for fn in _post_plugins:
        parts.update(fn(parts))
    return _join_parts(parts)

def _urlparse(url):
    parts = dict(zip(('scheme', 'netloc', 'path', 'params', 'query', 'fragment'),
                     urlparse.urlparse(url)
                ))
    if (not parts['scheme'] and not parts['netloc']) or \
        (
            not parts['netloc'] and
            parts['path'] and
            parts['path'][0] in map(str, range(10)) and
            url.startswith('%s:%s' % (parts['scheme'], parts['path']))
        ):
        # url may not have included a scheme, like 'domain.example'
        # url may have been in the form 'domain.example:8080'
        parts = dict(zip(('scheme', 'netloc', 'path', 'params', 'query', 'fragment'),
                         urlparse.urlparse('http://%s' % url)
                    ))
    elif parts['scheme'].lower() not in ('http', 'https'):
        return None
    return parts

def _join_parts(parts):
    url = '%s://' % parts['scheme']
    if parts['username']:
        url += parts['username']
        if parts['password']:
            url += ':%s' % parts['password']
        url += '@'
    url += parts['hostname']
    if parts['port']:
        url += ':%s' % parts['port']
    url += parts['path']
    if parts['params']:
        url += ';%s' % parts['params']
    if parts['query']:
        url += '?%s' % _join_query(parts['query'])
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

def _split_query(query):
    # The following code's basic logic was found in the Python 2.6
    # urlparse library, but was modified due to differing needs
    ret = {}
    queries = [j for i in query.split('&') for j in i.split(';')]
    if queries == ['']:
        return ret
    for q in queries:
        nv = q.split('=', 1)
        if len(nv) == 1:
            # Differentiate between `?n=` and ?n`
            nv.append(None)
        ret.setdefault(nv[0], []).append(nv[1])
    return ret

def _join_query(qdict):
    def replace(s):
        return u'%%%s' % hex(ord(s.group(1)))[2:].upper()
    ret = ''
    for k in sorted(qdict.keys()):
        for v in sorted(qdict[k]):
            if v is None:
                ret += '&%s' % (re.sub(UNACCEPTABLE_QUERY_CHARS, replace, k),)
            elif not v:
                ret += '&%s=' % (re.sub(UNACCEPTABLE_QUERY_CHARS, replace, k),)
            else:
                ret += '&%s=%s' % (re.sub(UNACCEPTABLE_QUERY_CHARS, replace, k),
                                   re.sub(UNACCEPTABLE_QUERY_CHARS, replace, v)
                                  )
    return ret[1:]
