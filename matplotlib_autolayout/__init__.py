"""
Converts an ascii-art representing the layout of a matplotlib plot
into the source code neccessary to generate said plot, or directly
into a figure and axes.

The ascii-art represents a grid and every character denotes a part
of an axis. An axis is comprised of a rectangular region containing
the same characters.

For example:

```
aac
bbc
```

This represents a plot with three axes: a, b and c. a and b have the
same height, are on top of each other and to the left of c. Additionally,
a and b are twice as wide as c, and c is tall as a and b combined.
"""

from .generate import generate_layout, generate_source_code
