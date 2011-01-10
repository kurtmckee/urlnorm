Purpose
=======

The primary goal of urlnorm.py is to normalize HTTP and HTTPS URLs in a similar
fashion to browser address bars so that the resource the URL is pointing at can
be retrieved.  For instance, all of the following URLs will be normalized to
`http://domain.example/`:

* domain.example
* http://DOMAIN.EXAMPLE:80/
* http://domain.example/?#

The secondary goal of urlnorm.py is to provide a basic way to "fix" URLs with
additional or unnecessary cruft attached. This is accomplished through a very
simple plugin system.


Usage
=====

urlnorm.py is a single file, so it can copied anywhere you can import it.
Here's a simple example:

    >>> from urlnorm import urlnorm
    >>> urlnorm('domain.example')
    http://domain.example/

It is also possible to specify a base URL:

    >>> urlnorm('/path', 'http://domain.example/')
    http://domain.example/path

The full call pattern is `urlnorm(url, base=None)`, where `url` and `base` are
both strings, and the return result is also a string.


Plugins
=======

There are two functions provided for registering a plugin,
`register_pre_plugin` and `register_post_plugin`. "Pre" plugins must accept a
single string argument - an unparsed URL - and return a URL string. "Post"
plugins must accept a single dictionary argument - a parsed URL - and return a
single dictionary argument. The dictionary will contain multiple keys
representing the different parts of the URL, including `hostname` and `query`
to name two. 

To register a plugin, call the appropriate `register` function with the plugin
function as an argument. Here's an example of a no-op "pre" plugin:

    >>> plugfn = lambda u: u
    >>> urlnorm.register_pre_plugin(plugfn)

Several sample plugins are included in the `plugins/` directory of the source
code to demonstrate both types of plugins.


License
=======

urlnorm.py is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

urlnorm.py is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with urlnorm.py.  If not, see <http://www.gnu.org/licenses/>.


--------------------------------------------------------------------------------

Copyright (C) 2010 Kurt McKee <<contactme@kurtmckee.org>>

This README is licensed under the Creative Commons Attribution-ShareAlike 3.0
Unported License. To view a copy of this license, visit
<http://creativecommons.org/licenses/by-sa/3.0/> or send a letter to Creative
Commons, 171 Second Street, Suite 300, San Francisco, California, 94105, USA.
