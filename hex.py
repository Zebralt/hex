
import time
import curses
import string

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

colors = {
    'r':curses.COLOR_RED,
    'g':curses.COLOR_GREEN,
    'y':curses.COLOR_YELLOW,
    'db':curses.COLOR_BLUE,
    'm':curses.COLOR_MAGENTA,
    'b':6
}

class TextAlign:
    LEFT, MIDDLE, RIGHT = range(3)

padding_char = ' '

class Element:
    def __init__(self, width=1, height=1, x=0, y=0, traversable=False):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        
    def paint(self):
        return ['x' * self.width] * self.height
    
class Label(Element):
    def __init__(self, text, padding=(1,2,1,2), margin=(1,)*4, traversable=False, color=0):
        self.ptop, self.pright, self.pbottom, self.pleft = padding
        self.mtop, self.mright, self.mbottom, self.mleft = margin
        
        # Text Formatting includes :
        # * padding : top, right, bottom, left
        # * overflow : should the text extend the overall size of the element if space is lacking ?
        # * of these depends the final number of lines
        # * we can always include line/word wrap
        # * line wrap
        # * text align (left, middle, right)
        # * text justification
        
        max_line_length = max(map(len, text.split('\n')))
        
        Element.__init__(self, width=max_line_length + self.pright + self.pleft, height=text.count('\n') + self.ptop + self.pbottom, traversable=traversable)
        
        self.text = text
        self.color = color
        self.align = TextAlign.LEFT
        
    def align_text(self, text=self.text, align=self.align):
        self.text = text
        self.align = align
        
    
    def paint(self, win):
        
        # generate aligned, line-y text
        max_line_length = max(map(len, self.text.split('\n')))
        lines = [t.center(max_line_length + self.pleft + self.pright) for t in self.text.split('\n')]
        
        
        l = [padding_char * self.width] * self.ptop + lines + [padding_char * self.width] * self.pbottom
        win.writelines(self.x, self.y, l, self.color)
    
class Panel(Element):
    def __init__(self):
        Element.__init__(self)
        self.elements = []
        
    def pack(self, mode, spacing=1, **kw):
        
        if not self.elements:
            return
        
        first = self.elements[0]
        first.x, first.y = self.x, self.y
        
        maxheight = max([x.height for x in self.elements])
        maxwidth = max([x.width for x in self.elements])
        
        if mode == 'column':
#            self.width = maxwidth
#            self.height = maxheight
            for el0, el1 in zip(self.elements, self.elements[1:]):
                el1.x, el1.y = el0.x, el0.y + el0.height + 1 + spacing
                
        if mode == 'row':
#            self.width = maxwidth
#            self.height = maxheight
            for el0, el1 in zip(self.elements, self.elements[1:]):
                el1.x, el1.y = el0.x + el0.width + spacing, el0.y
            
        if mode == 'grid':
            grid_width, grid_height = kw['gwidth'], kw['gheight']
            
            
    
    def add(self, el):
        self.elements.append(el)
        
    def paint(self, win):
        for el in self.elements:
            el.paint(win)
    
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

class Application:
    def __init__(self):
        self.elements = []
        self.color_pairs = []
        self.shortcuts = {'q' : self.quit}
        
        self.refresh_delay = .1
        # ...
        
        
    def start(self):
        """
        Starts the Curses wrapper.
        """
        
        curses.initscr()
        
        self.width, self.height = curses.COLS, curses.LINES
        self.true_width, self.true_height = self.width - 2, self.height - 1
        
        self.wrapper = curses.wrapper(self.main)        
        
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
        self.stdscr.addstr(self.height - 1, 0, sep.join(msg))
        return self.stdscr.getkey()
    
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
        
        pass
    
    def add(self, elem):
        self.elements.append(elem)
        
    def paint(self):
        for el in self.elements:
            el.paint(self)
#            self.writelines(el.x, el.y, el.paint())

    def color_pair(self, idx, fg=0, bg=0):
        if not fg and not bg:
            return self.color_pairs
    
    def main(self, stdscr):
        
        self.stdscr = stdscr
        self.stdscr.nodelay(True)
    
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
            
if __name__ == '__main__':
    app = Application()
    
    # GUI Elements
    p = Panel()
    for i in range(1,13):
        l = Label('[Label %d]' % (i), padding=(0,)*4, color=i + 1)
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