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

import os
import sys
import fcntl
import struct
import signal
import termios
import threading


top_selection = 0
middle_selection = ~0
bottom_selection = ~0


def printf(format, *args):
    text = format % args
    sys.stdout.buffer.write(text.encode('utf-8'))
    sys.stdout.buffer.flush()


def run_interface():
    # Create condition for screen refreshing
    global refresh_cond
    refresh_cond = threading.Condition()
    
    # Get current screen width and listen for updates
    global height, width
    (height, width) = struct.unpack('hh', fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, '1234'))
    signal.signal(signal.SIGWINCH, sigwinch_handler)
    
    saved_stty = termios.tcgetattr(sys.stdout.fileno())
    stty = termios.tcgetattr(sys.stdout.fileno())
    stty[3] &= ~(termios.ICANON | termios.ECHO | termios.ISIG)
    printf('\033[?1049h\033[?25l')
    try:
        termios.tcsetattr(sys.stdout.fileno(), termios.TCSAFLUSH, stty)
        interface_loop()
    finally:
        termios.tcsetattr(sys.stdout.fileno(), termios.TCSAFLUSH, saved_stty)
        printf('\033[?25h\033[?1049l')


def sigwinch_handler(_signal, _frame):
    '''
    Handler for the SIGWINCH singnal
    '''
    global height, width
    (height, width) = struct.unpack('hh', fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, '1234'))
    refresh_cond.acquire()
    try:
        refresh_cond.notify()
    finally:
        refresh_cond.release()


def interface_loop():
    while True:
        refresh_cond.acquire()
        try:
            top = create_interface_top()
            middle = create_interface_middle()
            bottom = create_interface_bottom()
            
            printf('\033[H\033[2J\033[07m%s\033[27m\033[%i;1H%s\033[%i;1H%s',
                   top, max(height - 10, 1), middle, height, bottom)
            refresh_cond.wait()
        finally:
            refresh_cond.release()


def create_interface_top():
    '''
    Construct the master tabs for the top of the screen
    
    @return  :str  The text to print on the top of the screen
    '''
    # Tab titles
    tabs = [ 'Torrents'
           , 'States and trackers'
           , 'Preferences'
           , 'Help'
           ]
    
    # Surround the tab titles with spaces
    tabs = [' %s ' % t for t in tabs]
    
    # Get selection and format of selection depending on focus
    if top_selection >= 0:
        selected_pattern = '\033[44m\033[27m%s\033[07m\033[00;07m'
        selection = top_selection
    else:
        selected_pattern = '\033[01;44m%s\033[00;07m'
        selection = ~top_selection
    
    # Truncate the tab bar if the screen is too small
    if len('  '.join(tabs)) > width:
        tabs = [tabs[selection]]
        if len(tabs[0]) > width:
            tabs[0] = tabs[0][1 : -1]
        if len(tabs[0]) > width:
            tabs[0] = tabs[0][:width]
    
    # Format tabs
    ftabs = [(selected_pattern if selection == i else '%s') % tabs[i] for i in range(len(tabs))]
    
    # Pad the bar to fit the full width of the screen and format the bar
    pad = ' ' * (width - len('  '.join(tabs)))
    top = '  '.join(ftabs)
    return '\033[07m' + top + pad + '\033[00m'


def create_interface_middle():
    '''
    Construct the torrent information tabs for the "middle" of the screen
    
    @return  :str  The text to print in the "middle" of the screen
    '''
    # Exclude if the screen it too small
    if height < 18:
        return ''
    
    # Tab titles
    tabs = [ 'Status'
           , 'Details'
           , 'Peers'
           , 'Options'
           ]
    
    # Surround the tab titles with spaces
    tabs = [' %s ' % t for t in tabs]
    
    # Get selection and format of selection depending on focus
    if middle_selection >= 0:
        selected_pattern = '\033[44m\033[27m%s\033[07m\033[00;07m'
        selection = middle_selection
    else:
        selected_pattern = '\033[01;44m%s\033[00;07m'
        selection = ~middle_selection
    
    # Truncate the tab bar if the screen is too small
    if len('  '.join(tabs)) > width:
        tabs = [tabs[selection]]
        if len(tabs[0]) > width:
            tabs[0] = tabs[0][1 : -1]
        if len(tabs[0]) > width:
            tabs[0] = tabs[0][:width]
    
    # Format tabs
    ftabs = [(selected_pattern if selection == i else '%s') % tabs[i] for i in range(len(tabs))]
    
    # Pad the bar to fit the full width of the screen and format the bar
    pad = ' ' * (width - len('  '.join(tabs)))
    middle = '  '.join(ftabs)
    return '\033[07m' + middle + pad + '\033[00m'


def create_interface_bottom():
    '''
    Construct the status bar for the bottom of the screen
    
    @return  :str  The text to print on the bottom of the screen
    '''
    # Status delimiter
    sep = '  '
    
    # Status titles
    titles = [ 'Connections'
             , 'Transfer speed'
             , 'Protocol traffic'
             , 'DHT nodes'
             ]
    
    # Status field values
    values = [ (100, 200)
             , (100, 'MB', 100, 'MB')
             , (12, 12)
             , (150)
             ]
    
    # Status field patterns
    patterns = [ '%i (%i)'
               , '%.1f %s/s↓ %.1f %s/s↑'
               , '%.2f↓ %.2f↑ KB/s'
               , '%i'
               ]
    
    # Status fields
    fields = [patterns[i] % values[i] for i in range(len(patterns))]
    
    # Add title–value delimiter
    titles = [t + ': ' for t in titles] + ['']
    
    # Calculate length of the text
    len0 = len((sep + '  ').join(fields)) + 2
    
    # Truncate the status bar if the screen is not width enough
    selection = bottom_selection
    if len0 > width:
        sel = max(bottom_selection, 0)
        titles = [titles[sel]]
        values = [values[sel]]
        patterns = [patterns[sel]]
        fields = [fields[sel]]
        selection = 0
        len0 = len((sep + '  ').join(fields)) + 2
        start = final = ''
        if len0 > width:
            fields[0] = fields[0][:width - 2]
            len0 = width
    
    # Calculate the length of the text if it was extended with:
    #   a) The title of the selected field
    #   b) The title of all fields
    len1a = len0 + len(titles[selection])
    len1b = len0 + sum(len(t) for t in titles)
    
    # Extend the text with either the title of all fields,
    # or only the title of the select field, depending on
    # what fits, if any fits
    if len1b <= width:
        fields = [titles[i] + fields[i] for i in range(len(fields))]
        len0 = len1b
    elif len1a <= width:
        titles = [titles[i] if selection == i else '' for i in range(len(fields))]
        fields = [titles[i] + fields[i] for i in range(len(fields))]
        len0 = len1a
    
    # Highlight selected field
    formats = { True  : '\033[00;44m %s \033[00;07m'
              , False : '\033[00;07m %s '
              }
    fields = [formats[selection == i] % fields[i] for i in range(len(fields))]
    
    # Join the fields
    bottom = sep.join(fields)
    
    # Pad the right to the width
    if len0 < width:
        bottom += '\033[07m' + ' ' * (width - len0) + '\033[00m'
    
    return bottom

