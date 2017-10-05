import sys
import imp
import copy
from StringIO import StringIO

##
_html_level = 0

##
_extends = None

##
_blocks = {}

##
def prefix():
    return _html_level * '  '

def write(what):
    print(prefix() + what)

def spaces(x):
    return ' '.join(x)

def reindent(what):
    ## Make it big for now
    indent = len(what)
    lines = what.split('\n')
    for line in lines:
        ## Make sure to filter empty lines, otherwise indent will always be 0
        if len(line):
            indent = min(indent, len(line) - len(line.lstrip()))
    for i, line in enumerate(lines):
        ## Make sure to filter empty lines as we don't want to print plenty of spaces for no reason
        ## Also, it fixes the problem of the last empty line that get indented which the following
        ## line to be over-indented as well
        if len(line):
            lines[i] = prefix() + line[indent:]
    return '\n'.join(lines)

##
class lazy_print(object):
    def __init__(self, what):
        self.what = what

    def __pos__(self):
        write(self.what)

    def __str__(self):
        return str(self.what)

##
class HTMLNode(object):
    def parse_attrs(self, *args, **attrs):
        def filter_empty(x):
            return filter(None, x)
        if len(args):
            ## TODO: check that len(args) is 1
            classes = args[0].strip().split('.')
        else:
            classes = []
        if len(classes):
            if classes[0].startswith('#'):
                attrs['id'] = classes[0][1:] # Skip #
                classes = classes[1:]
            if len(classes):
                attrs['class'] = filter_empty(classes)
	return attrs

    def html_attrs(self):
        h = []
        for attr in self.attrs:
            if attr == 'id':
                h.append('id="{}"'.format(self.attrs['id']))
            elif attr == 'class':
                h.append('class="{}"'.format(spaces(self.attrs['class'])))
            else:
                h.append('{}="{}"'.format(attr, self.attrs[attr]))
        return spaces(h)

class HTMLBlockNode(HTMLNode):
    def __init__(self, *args, **attrs):
        self.attrs = self.parse_attrs(*args, **attrs)

    def __enter__(self):
        global _html_level
        write(self.html_begin())
        _html_level += 1

    def __exit__(self, type, value, tb):
        global _html_level
        _html_level -= 1
        write(self.html_end())

    def __getitem__(self, content):
        h = self.html_begin()
        for x in content:
            if x is None:
                continue
            h += str(x)
        h += self.html_end()
        return lazy_print(h)

    def html_begin(self):
        attrs = self.html_attrs()
        return '<{}{}{}>'.format(self.name, ' ' if len(attrs) else '', attrs)

    def html_end(self):
        return '</{}>'.format(self.name)

class HTMLInlineNode(HTMLNode):
    pass

##
def as_HTMLBlockNode(name):
    _type = None
    def make_HTMLBlockNode():
        return _type()
    class _MetaHTMLBlockNode(type):
        def __enter__(self, *args):
            return make_HTMLBlockNode().__enter__(*args)
        def __exit__(self, *args):
            return make_HTMLBlockNode().__exit__(*args)
    	def __getitem__(self, *args):
            return make_HTMLBlockNode().__getitem__(*args)
    class _HTMLBlockNode(HTMLBlockNode):
        __metaclass__ = _MetaHTMLBlockNode
    _HTMLBlockNode.name = name
    _type = _HTMLBlockNode
    return _HTMLBlockNode
    h = HTMLBlockNode()
    h.name = name
    return h

def as_HTMLInlineNode(name):
    h = HTMLInlineNode()
    h.name = name
    return h

##
div = as_HTMLBlockNode('div')
span = as_HTMLBlockNode('span')
script = as_HTMLBlockNode('script')

##
html = as_HTMLBlockNode('html')
head = as_HTMLBlockNode('head')
body = as_HTMLBlockNode('body')

##
img = as_HTMLInlineNode('img')

##
raw = lazy_print

##
def mixin(f):
    _type = None
    def make_Mixin():
        return _type()
    class _MetaMixin(type):
        def __enter__(self, *args):
            self.mixin = make_Mixin()
            return self.mixin.__enter__(*args)
        def __exit__(self, *args):
            return self.mixin.__exit__(*args)
    	def __getitem__(self, *args):
            return make_Mixin().__getitem__(*args)
    class _Mixin(object):
        __metaclass__ = _MetaMixin
        def __init__(self, *args):
            self.args = list(args)
        def __enter__(self, *args):
            global _html_level
            self.stdout = StringIO()
            self.stdout_was = sys.stdout
            sys.stdout = self.stdout
            _html_level += 1
        def __exit__(self, *args):
            global _html_level
            _html_level -= 1
            sys.stdout = self.stdout_was
            v = self.stdout.getvalue()
            def block(cls):
                ## Use a basic stdout.write here as we already have well-formatted HTML
                ## TODO: Reindent the code cause HTML have already been printed but the _html_level
                ## is not the same when calling this function
                sys.stdout.write(reindent(v))
                #sys.stdout.write(v)
            _Mixin.block = classmethod(block)
            f(*self.args)
    _type = _Mixin
    return _Mixin

def say(something):
    sys.__stdout__.write(str(something) + '\n')

class MagicBlock(object):
    class _MagicBlock(object):
        def __init__(self):
            self.blocks = {}
        def get(self, block):
            return self.blocks[block]
        def set(self, block, f):
            self.blocks[block] = f

    instance = None
    def __init__(self):
        if not MagicBlock.instance:
            MagicBlock.instance = MagicBlock._MagicBlock()

    def __call__(self, f):
        ## Decorator
        self.instance.set(f.__name__, f)

    def __getattr__(self, block):
        return self.instance.get(block)

block = MagicBlock()

def render(path, _globals=globals()):
    global _extends
    _extends = None
    stdout = StringIO()
    sys.stdout = stdout
    exec(open(path).read(), _globals)
    sys.stdout = sys.__stdout__
    if _extends:
        return render(_extends)
    return stdout.getvalue()

def extends(path):
    global _extends
    _extends = path
