# -*- python -*-
'''
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

# Downloads
#    (either)
#       Use full allocation (y)
#       Use sparse allocation
#    Prioritise first and list pieces of files
#    Preallocate all files (y)
#    Add torrents in paused state
# Network
#    Incoming ports (either)
#       Use random ports (y)
#       Range (6881, 6891)
#    Outgoing ports (either)
#       Use random ports (y)
#       Range (0, 0)
#    Interface ()
#    Type of Service
#       Peer ToS Byte (0x00)
#    Network extras
#       Universal Plug and Play (y)
#       Network Address Translator Port Mapping Protocol (y)
#       Peer Exchange (y)
#       Local Service Discovery (y)
#       Distributed hash table (y)
#    Encryption
#       Inbound (either)
#          Forced (y)
#          Enabled
#          Disabled
#       Outbound (either)
#          Forced (y)
#          Enabled
#          Disabled
#       Level (either)
#          Handshake
#          Full stream (y)
#          Either
#       Encrypt entire stream (y)
# Proxy
#    Peer (either)
#       None (y)
#       Socksv4
#       Socksv5
#       Socksv5 with authentication
#       HTTP
#       HTTP with authentication
#    Web Seed (either)
#       None (y)
#       Socksv4
#       Socksv5
#       Socksv5 with authentication
#       HTTP
#       HTTP with authentication
#    Tracker (either)
#       None (y)
#       Socksv4
#       Socksv5
#       Socksv5 with authentication
#       HTTP
#       HTTP with authentication
#    Distributed hash table (either)
#       None (y)
#       Socksv4
#       Socksv5
#       Socksv5 with authentication
#       HTTP
#       HTTP with authentication
# Bandwidth
#    Global bandwidth usage
#       Maximum connections (200)
#       Maximum upload slots (5)
#       Maximum download speed (unlimited)
#       Maximum upload speed (unlimited)
#       Maximum half-open connections (50)
#       Maximum connection attemps per second (20)
#       Ignore limits on local network (y)
#       Rate limit IP overhead (y)
#    Per torrent bandwidth usage
#       Maximum connections (inherit global limit)
#       Maximum upload slots (inherit global limit)
#       Maximum download speed (inherit global limit)
#       Maximum upload speed (inherit global limit)
# Queue
#    Queue new torrents to the top
#    Active torrents
#       Total active (27)
#       Total active downloading (20)
#       Total active seeding (7)
#       Do not count slow torrents (y)
#    Seeding
#       Share ratio limit (2)
#       Seed limit ratio (7)
#       Seed limit (180 m)
#       Stop seeding when share ratio reaches (never)
#          Remove torrent when share ratio is reached
# Cache
#    Cache size (512 blocks of 16 K)
#    Cache expiry (60 seconds)
# GeoIP database
#    IPv4 location (/usr/share/GeoIP/GeoIP.dat)
#    IPv6 location (/usr/share/GeoIP/GeoIPv6.dat)
