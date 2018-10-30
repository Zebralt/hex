
import time
import curses
import string
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
        
    def start(self):
        """
        Starts the Curses wrapper.
        """
        
        curses.initscr()
        
        self.width, self.height = curses.COLS, curses.LINES
        self.true_width, self.true_height = self.width - 2, self.height - 1
        
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
        
        return self.yesno('Are you sure you want to quit ?')
    
    def add(self, elem):
        self.elements.append(elem)
        
    def paint(self):
        for el in self.elements:
            el.paint(self)
#            self.writelines(el.x, el.y, el.paint())

    def color_pair(self, idx, fg=0, bg=0):
        if not fg and not bg:
            return self.color_pairs.get(idx)
        else:
            name = idx
            if type(idx) == str:
                idx = len(self.color_pairs.keys()) + 1
            curses.init_pair(idx, fg, bg)
            self.color_pairs[name] = curses.color_pair(idx)
    
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
            
if __name__ == '__main__':
    app = Application()
    
    # GUI Elements
    p = Panel()
    for i in range(1,13):
        l = Label('[Label %d]' % (i), padding=(0,2,0,2), color=i + 1)
        p.add(l)
    p.x, p.y = 10, 10
    p.pack('row')
    app.add(p)
    
    
    l = Label('This inverted\n but better', color=34)
    l.x, l.y = 30, 30
    app.add(l)
    
    # Shortcuts
    app.shortcut('x', action=lambda *_: app.write(0, 20, 'You pressed X!'))
    
    app.start()