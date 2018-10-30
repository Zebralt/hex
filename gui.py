
class TextAlign:
    LEFT, MIDDLE, RIGHT = range(3)

padding_char = ' '

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class Element:
    def __init__(self, width=1, height=1, x=0, y=0, traversable=False):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        
    def paint(self):
        return ['x' * self.width] * self.height

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class Label(Element):

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
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
        
    def align_text(self, text=None, align=None):
        self.text = text or self.text
        self.align = align or self.align
        
    
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

