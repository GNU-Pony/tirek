# -*- python -*-
copyright='''
tirek — A torrent client with a terminal user interface
Copyright © 2014  Mattias Andrée (maandree@member.fsf.org)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import os


authors = [ ('2014', 'Mattias Andrée', 'maandree@member.fsf.org')
          ]
'''
:(years:str, name:str, email:str)  Authors of the program
'''


copyright_text = copyright[1 : -1]
'''
:list<str>  Copyright text lines for the overall program
'''

if not (('TERM' in os.environ) and (os.environ['TERM'].startswith('xterm'))):
    copyright_text = copyright_text.replace('—', '-')
copyright_text = copyright_text.split('\n')
copyright_text[1 : 2] = ['Copyright © %s  %s (%s)' % a for a in authors]

