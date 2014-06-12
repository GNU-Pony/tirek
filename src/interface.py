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

from copyright import copyright_text

_ = lambda x : x


MIDDLE_REQUIRE_HEIGHT = 19

top_titles = [ _('Torrents')
             , _('States and trackers')
             , _('Preferences')
             , _('Help')
             ]
    
middle_titles = [ _('Status')
                , _('Details')
                , _('Peers')
                , _('Options')
                ]

bottom_titles = [ _('Connections')
                , _('Transfer speed')
                , _('Protocol traffic')
                , _('DHT nodes')
                ]

bar_selection = 0
top_selection = 0
middle_selection = ~0
bottom_selection = ~0
first_line_help = 0
running = True

update_queue = []
    

def printf(format, *args, flush = True):
    text = format % args
    sys.stdout.buffer.write(text.encode('utf-8'))
    if flush:
        sys.stdout.buffer.flush()


def run_interface():
    # Create condition for screen refreshing
    global refresh_cond
    refresh_cond = threading.Condition()
    
    # Get current screen width and listen for updates
    global height, width
    try:
        (height, width) = struct.unpack('hh', fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, '1234'))
    except OSError as e:
        if e.errno == 25:
            print(_('A terminal on stdout is required.'))
            sys.exit(1)
        else:
            raise e
    signal.signal(signal.SIGWINCH, sigwinch_handler)
    
    # Get TTY settings
    saved_stty = termios.tcgetattr(sys.stdout.fileno())
    stty = termios.tcgetattr(sys.stdout.fileno())
    # Modify TTY settings
    stty[3] &= ~(termios.ICANON | termios.ECHO | termios.ISIG)
    # Initialise terminal and hide cursor
    printf('\033[?1049h\033[?25l')
    try:
        # Apply now TTY settings
        termios.tcsetattr(sys.stdout.fileno(), termios.TCSAFLUSH, stty)
        
        # Start input loop
        input_thread = threading.Thread(target = input_loop)
        input_thread.setDaemon(True)
        input_thread.start()
        
        # Start interface redraw loop
        interface_loop()
    finally:
        # Restore old TTY setting
        termios.tcsetattr(sys.stdout.fileno(), termios.TCSAFLUSH, saved_stty)
        # Show cursor, clear screen and terminate terminal
        printf('\033[?25h\033[H\033[2J\033[?1049l')


def sigwinch_handler(_signal, _frame):
    '''
    Handler for the SIGWINCH signal
    '''
    global height, width, bar_selection, top_selection, middle_selection
    (height, width) = struct.unpack('hh', fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, '1234'))
    refresh_cond.acquire()
    try:
        if (height < MIDDLE_REQUIRE_HEIGHT) and (bar_selection == 1):
            top_selection = ~top_selection
            middle_selection = ~middle_selection
            bar_selection = 0
        refresh_cond.notify()
    finally:
        refresh_cond.release()


def input_loop():
    global running, top_selection, middle_selection, bottom_selection, bar_selection, first_line_help
    while running:
        c = next_input()
        if c == 'q':
            refresh_cond.acquire()
            try:
                running = False
                refresh_cond.notify()
            finally:
                refresh_cond.release()
        elif c == chr(ord('L') - ord('@')):
            refresh_cond.acquire()
            try:
                refresh_cond.notify()
            finally:
                refresh_cond.release()
        elif c == '\033[C':
            refresh_cond.acquire()
            try:
                if bar_selection == 0:
                    top_selection = min(top_selection + 1, len(top_titles) - 1)
                elif bar_selection == 1:
                    middle_selection = min(middle_selection + 1, len(middle_titles) - 1)
                elif bar_selection == 2:
                    bottom_selection = min(bottom_selection + 1, len(bottom_titles) - 1)
                update_queue.append('bar %i' % bar_selection)
                refresh_cond.notify()
            finally:
                refresh_cond.release()
        elif c == '\033[D':
            refresh_cond.acquire()
            try:
                if bar_selection == 0:
                    top_selection = max(top_selection - 1, 0)
                elif bar_selection == 1:
                    middle_selection = max(middle_selection - 1, 0)
                elif bar_selection == 2:
                    bottom_selection = max(bottom_selection - 1, 0)
                update_queue.append('bar %i' % bar_selection)
                refresh_cond.notify()
            finally:
                refresh_cond.release()
        elif c == '\033[1;5A':
            refresh_cond.acquire()
            try:
                update_queue.append('bar %i' % bar_selection)
                if bar_selection == 1:
                    top_selection = ~top_selection
                    middle_selection = ~middle_selection
                    bar_selection = 0
                elif bar_selection == 2:
                    if (height < MIDDLE_REQUIRE_HEIGHT) or (top_selection != ~0):
                        top_selection = ~top_selection
                        bottom_selection = ~bottom_selection
                        bar_selection = 0
                    else:
                        middle_selection = ~middle_selection
                        bottom_selection = ~bottom_selection
                        bar_selection = 1
                update_queue.append('bar %i' % bar_selection)
                refresh_cond.notify()
            finally:
                refresh_cond.release()
        elif c == '\033[1;5B':
            refresh_cond.acquire()
            try:
                update_queue.append('bar %i' % bar_selection)
                if bar_selection == 0:
                    if (height < MIDDLE_REQUIRE_HEIGHT) or (top_selection != 0):
                        top_selection = ~top_selection
                        bottom_selection = ~bottom_selection
                        bar_selection = 2
                    else:
                        top_selection = ~top_selection
                        middle_selection = ~middle_selection
                        bar_selection = 1
                elif bar_selection == 1:
                    middle_selection = ~middle_selection
                    bottom_selection = ~bottom_selection
                    bar_selection = 2
                update_queue.append('bar %i' % bar_selection)
                refresh_cond.notify()
            finally:
                refresh_cond.release()
        elif c == '\033[A':
            if top_selection == 3:
                refresh_cond.acquire()
                try:
                    first_line_help = max(first_line_help - 1, 0)
                    refresh_cond.notify()
                finally:
                    refresh_cond.release()
        elif c == '\033[B':
            if top_selection == 3:
                refresh_cond.acquire()
                try:
                    first_line_help += 1
                    refresh_cond.notify()
                finally:
                    refresh_cond.release()


def next_input():
    '''
    Read the next input for stdin
    
    @return  :str  The next input, can be an escape sequence
    '''
    buf = ''
    esc = 0
    while True:
        c = chr(sys.stdin.buffer.read(1)[0])
        buf += c
        if esc == 1:
            if c == '[':
                esc = 2
            elif (len(buf) < 2) and (c == '\033'):
                continue
            else:
                break
        elif esc == 2:
            if ('a' <= c <= 'z') or ('A' <= c <= 'Z') or (c == '~'):
                break
        elif c == '\033':
            esc = 1
        else:
            break
    return buf


def interface_loop():
    global first_line_help
    while running:
        refresh_cond.acquire()
        try:
            top = create_interface_top()
            middle = create_interface_middle()
            bottom = create_interface_bottom()
            
            if len(update_queue) == 0:
                printf('\033[H\033[2J\033[07m%s\033[27m\033[%i;1H%s\033[%i;1H%s',
                       top, max(height - 11, 1), middle, max(height - 1, 1), bottom)
            else:
                while len(update_queue) > 0:
                    update_message = update_queue[0]
                    update_queue[:] = update_queue[1:]
                    if update_message == 'bar 0':
                        printf('\033[H\033[07m%s\033[27m', top)
                    elif update_message == 'bar 1':
                        printf('\033[%i;1H%s', max(height - 11, 1), middle)
                    elif update_message == 'bar 2':
                        printf('\033[%i;1H%s', max(height - 1, 1), bottom)
            
            if top_selection in (3, ~3):
                text = copyright_text
                if first_line_help + height - 3 > len(text):
                    first_line_help = max(len(text) - height + 3, 0)
                text = text[first_line_help : first_line_help + height - 3]
                text = '\n'.join(text)
                printf('\033[2;1H%s', text)
            else:
                blank_lines = max(height - 3, 0)
                printf(''.join('\033[%i;1H\033[2K' % (i + 2) for i in range(blank_lines)))
                printf('\033[%i;1H%s', max(height - 11, 1), middle)
            
            refresh_cond.wait()
        finally:
            refresh_cond.release()


def create_interface_top():
    '''
    Construct the master tabs for the top of the screen
    
    @return  :str  The text to print on the top of the screen
    '''
    # Surround the tab titles with spaces
    tabs = [' %s ' % t for t in top_titles]
    
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
        selection = 0
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
    if height < MIDDLE_REQUIRE_HEIGHT:
        return ''
    
    # Exclude if wrong top tab is selected
    if top_selection not in (0, ~0):
        return ''
    
    # Surround the tab titles with spaces
    tabs = [' %s ' % t for t in middle_titles]
    
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
        selection = 0
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
    titles = [t for t in bottom_titles]
    
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
    titles = [t + _(': ') for t in titles] + ['']
    
    # Calculate length of the text
    len0 = len((sep + '  ').join(fields)) + 2
    
    # Truncate the status bar if the screen is not width enough
    selection = bottom_selection
    if len0 > width:
        sel = max(bottom_selection, ~bottom_selection)
        titles = [titles[sel]]
        values = [values[sel]]
        patterns = [patterns[sel]]
        fields = [fields[sel]]
        selection = ~0 if bottom_selection < 0 else 0
        len0 = len((sep + '  ').join(fields)) + 2
        if len0 > width:
            fields[0] = fields[0][:width - 2]
            len0 = width
    
    # Calculate the length of the text if it was extended with:
    #   a) The title of the selected field
    #   b) The title of all fields
    len1a = len0 + len(titles[max(selection, -1)])
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

