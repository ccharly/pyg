> A pythonic alternative to write `HTML` (highly inspired from `pug.js`) using only plain `Python`.

# Why `pyg`?

`HTML` is _**painful**_ to write. `Python` is **powerful**, **easy** and **fun** to write.
How about combining them then to get something cool for writing `HTML`? This is what `pyg` tries to
achieve by not re-creating (yet) another language.

# What does it look like?

```python
## That's a basic view.. This should be named `view.py`
from pyg import *

with div('#div-id.div-class.and.another-class'): # A block element
    +span["How wonderful is pyg isn't it?"]      # An inline element
```

You can either use `python` interpreter to pretty-print the `HTML` or you can use the `pyg` script
like so:

```bash
python view.py
# or
pyg view.py
```
