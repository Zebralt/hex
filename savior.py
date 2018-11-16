
import time
import curses
import string
from random import choice

from gui import *

"""
From what I gather, if we want to build a content-agnostic Curses Application:

It should be able to :

* write given text at a given position
* have a basic prompt system (Do you really want to quit ? y/n)
* have an input prompt system (What's your name ? getstr)

Rather than having the user manage its own geometry, we can implement a simple
system where we have graphical elements between which the user can travel with
the arrow keys.

The user should be able to add events to specific keys.

We could also have intra-element key controls. This could be done with ENTER > ... > ESC to
enable key capture for the current element.

"""

#-------------------------------------------------------------------------------
# A simple class to encapsulate the concept of update/refresh delay.
#-------------------------------------------------------------------------------
class RefreshTimer:
    def __init__(self, delay):
        self.now = time.time()
        self.past = self.now
        self.delay = delay
        
    def __call__(self):
        self.now = time.time()
        ans = self.now - self.past > self.delay
        if ans: self.past = self.now
        return ans

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
colors = {
    'r':curses.COLOR_RED,
    'g':curses.COLOR_GREEN,
    'y':curses.COLOR_YELLOW,
    'db':curses.COLOR_BLUE,
    'm':curses.COLOR_MAGENTA,
    'b':6
}

class Application:
    def __init__(self):
        self.elements = []
        self.color_pairs = {}
        self.shortcuts = {'q' : self.quit}
        
        self.refresh_delay = .1
        self.nodelay = True 
        
        curses.initscr()
        
        self.width, self.height = curses.COLS, curses.LINES
        self.true_width, self.true_height = self.width - 2, self.height - 1       
        
    def start(self):
        """
        Starts the Curses wrapper.
        """
        
        self.wrapper = curses.wrapper(self.main)        
    

    def main(self, stdscr):
        
        self.stdscr = stdscr
        self.stdscr.nodelay(self.nodelay)
    
        for i in range(1,8):
            curses.init_pair(i,i,0)
    
        for i, e in enumerate(colors.values()):
            curses.init_pair(i + 1, e, 0)
        
        for i, e in enumerate(colors.values()):
            curses.init_pair(i + 1 + len(colors), 0, e)
            
        curses.init_pair(34, 0, 7)
        
        rti = RefreshTimer(self.refresh_delay)
        
        self.update()
        
        while True:
            
            try:
                self.key = stdscr.getkey()
                self.alert('You pressed', self.key)

                func = self.shortcuts.get(self.key, lambda *_:1)

                if func == self.quit:
                    if func():
                        break
                else:
                    func(self.key)
            
            except curses.error as e: 
                pass
            
            except Exception as e:
                self.alert(str(e))
                        
            if not rti():
                continue
                
            self.update()
            self.paint()
            self.refresh()


    def shortcut(self, name, action=None):
        """
        Associate a key to a function.
        """
        
        if action is None:
            return self.shortcuts.get(name)
        else:
            self.shortcuts[name] = action
    
    def write(self, x, y, *text, sep=' ', color=0):
        """
        Writes text at specified position.
        """
        
        args = []
        if color:
            color = curses.color_pair(color)
            args.append(color)
        
        self.stdscr.addstr(y%self.height, x%self.width, sep.join(text), *args)
        
    def writelines(self, x, y, lines, color=0):
        """
        Writes vertically aligned lines.
        """
        
        if type(lines) == str: lines = lines.split('\n')
        for i, line in enumerate(lines):
            self.write(x, y + i, line, color=color)
    
    def oneKeyPrompt(self, *msg, sep=' '):
        self.stdscr.nodelay(False)
        self.stdscr.addstr(self.height - 1, 0, sep.join(msg))
        x = self.stdscr.getkey()
        self.stdscr.nodelay(self.nodelay)
        return x

    def yesno(self, msg, answers='yn'):
        ans = self.oneKeyPrompt(msg, '(%s)' % (answers.title()))
        return ans == answers[0]
    
    def prompt(self, *msg, sep=' '):
        self.stdscr.addstr(self.height - 1, 0, sep.join(msg))

    def alert(self, *msg, sep=' '):
        """
        Highlights a message to the user in the bottom of the screen.
        """
        
        self.stdscr.addstr(self.height - 1, 0, sep.join(msg))
    
    def getkey(self):
        pass
    
    def update(self):
        self.writelines(10, 0, 'Hello ! \nThis is a basic Hex application.\n\nPress q to quit.')
    
    def refresh(self):
        """
        Refreshes the screen.
        """
        
        self.stdscr.refresh()
    
    def quit(self): 
        """
        A token function for quitting the application. This will just break out of the loop.
        """
        
        return True or self.yesno('Are you sure you want to quit ?')
    
    def add(self, elem):
        self.elements.append(elem)
        
    def paint(self):
        for el in self.elements:
            el.paint(self)
#            self.writelines(el.x, el.y, el.paint())

    def color_pair(self, name, fg=0, bg=0):
        
        if not fg and not bg:          
            return self.named_color_pairs.get(name)
        else:
            idx = max(self.index_color_pairs.values()) + 1
            self.index_color_pairs[(fg, bg)] = idx
            self.named_color_pairs[name] = idx
        
        
#-------------------------------------------------------------------------------
# Curses handles color in pairs (fg, bg). Those are registered with an index:
# idx -> (fg, bg)
# What I want to be able to do is :
# To create color pairs in advance, in the form (fg, bg) -> idx
# because I want the user to be able to specify either his own colors
# when creating an element, or to choose a color pair already created by name.
# So I need:
# 1. To create a dict (fg, bg) -> curses.idx
# 2. To create a dict name -> {'fg' : x, 'bg' : y}
# So that the user can do Label('...', **color_pair('LabelStyle'))
# or 
# Label('...', color=idx ? 'LabelStyle' ?)
# color id, color name, color (fg,bg) ...
#-------------------------------------------------------------------------------
# As for laying out elements inside containers ...
#-------------------------------------------------------------------------------
# padding, margin, width, height, fg, bg, font weight, blinking, text-align,
# text-justify, 
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
            

class Savior(Element):
    def __init__(self, width, height):
        self.char = '\u2588'
        self.x, self.y = 0, 1
        self.pc = Label(self.char, color=2, padding=(0,) * 4)
        self.pc.x, self.pc.y = self.x, self.y
        self.width, self.height = width, height
        self.board = [['\u2588' for _ in range(self.width)]] * self.height
        self.i = 0
        
    def update(self):
#         self.board = [[choice('-_#') for _ in range(self.width)]] * self.height
        pass
        
    def paint(self, win):
        win.writelines(self.x, self.y, [*map(lambda x:''.join(x), self.board)], color=0)
        self.pc.paint(win)
        
    def set_pos(self, pos):
        self.pc.x, self.pc.y = (
            (pos[0] % (self.width + 1)),
            (pos[1] % (self.height + 1))
        )
       
    def pcx(self, x):
        self.set_pos((x, self.pc.y))
        
    def pcy(self, y):
        self.set_pos((self.pc.x, y))
    
if __name__ == '__main__':
    
#     scrollbar(23, 100)
#     exit()
    app = Application()
    
    # GUI Elements    
    name_label = Label('Application 28.5', color=12, padding=(0,1,0,1))
    app.add(name_label)
    
    board = Savior(app.width//2, app.height//2)
    app.add(board)
    
    app.update = board.update
    app.refresh_delay = 0.05
#     app.refresh_delay = 0.5
    
    # Shortcuts
    app.shortcut('x', action=lambda *_: board.__setattr__('char', choice(string.punctuation)))
    app.shortcut('KEY_RIGHT', action=lambda *_: board.pcx(board.pc.x + 1))
    app.shortcut('KEY_DOWN', action=lambda *_: board.pcy(board.pc.y + 1))
    app.shortcut('KEY_LEFT', action=lambda *_: board.pcx(board.pc.x - 1))
    app.shortcut('KEY_UP', action=lambda *_: board.pcy(board.pc.y - 1))
    
    
    app.start()