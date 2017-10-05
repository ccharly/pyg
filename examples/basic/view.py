## That's a basic view.. This should be named `view.py`
from pyg import *

with div('#div-id.div-class.and.another-class'): # A block element
    +span["How wonderful is pyg isn't it?"]      # An inline element
