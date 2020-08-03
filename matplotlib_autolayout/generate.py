"""
Contains the functions necessary to read the
ascii-art plot specification and generate
the corresponding matplotlib code or objects.
"""

import sys
import warnings
from io import StringIO
from typing import IO, TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from .tree import find_bottom_nodes, make_tree

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure
    from matplotlib.gridspec import GridSpecBase


def generate_source_code(
    art: str,
    annotate: bool = True,
    file: IO = sys.stdout,
    hspace: Optional[float] = 0.5,
    wspace: Optional[float] = 0.6,
    width: Optional[float] = 12,
    height: Optional[float] = 8,
    width_factor: Optional[float] = None,
    height_factor: Optional[float] = None,
    dpi: float = 96,
) -> None:
    """
    Given the ascii-art representation of the plot's layout,
    generates the source code necessary to create matplotlib
    axes in the specified arrangement.

    Parameters
    ----------
    art (str):
        Ascii-art representing the layout.

    annotate (bool, optional):
        Whether to include a sample snippet annotating the axes. Defaults to True.

    file (IO, optional):
        Where to write the source code. Defaults to sys.stdout.

    hspace (Optional[float], optional):
        The horizontal space between axes. Defaults to 0.5.

    wspace (Optional[float], optional):
        The vertical space between axes. Defaults to 0.6.

    width (Optional[float], optional):
        Figure width in inches. Defaults to 12.

    height (Optional[float], optional):
        Figure height in inches. Defaults to 8.

    width_factor (Optional[float], optional):
        To determine the width, each character in the ascii-art corresponds to this
        many inches. Overrides `width`. Defaults to None.

    height_factor (Optional[float], optional):
        To determine the height, each
        character in the ascii-art corresponds to this many inches. Overrides
        `height`. Defaults to None.

    dpi (float, optional):
        DPI (dots-per-inch of the figure). Defaults to 96.

    Returns
    -------
    None. The source code is written in `file`.
    """

    nodes = find_bottom_nodes(art)
    tree = make_tree(nodes)
    tree.sort_axes()

    file.write("import matplotlib as mpl\n")
    file.write("import matplotlib.pyplot as plt\n")

    if width_factor is not None:
        if width is not None:
            warnings.warn("both width and width_factor specified; using width_factor")
        width = width_factor * tree.width

    if height_factor is not None:
        if height is not None:
            warnings.warn(
                "both height and height_factor specified; using height_factor"
            )
        height = height_factor * tree.height

    file.write(f"fig = plt.figure(figsize=({width}, {height}), dpi={dpi})\n\n")
    file.write("gridspecs = {}\n")
    file.write("axes = {}\n")

    tree.generate_source_code(file=file, wspace=wspace, hspace=hspace)

    if annotate:
        file.write("\nfor name, ax in axes.items():\n")
        file.write('    ax.annotate(name, (0.5, 0.5), ha="center", va="center")\n')


def generate_layout(
    art: str,
    wspace: Optional[float] = 0.5,
    hspace: Optional[float] = 0.5,
    width: Optional[float] = 12,
    height: Optional[float] = 8,
    width_factor: Optional[float] = None,
    height_factor: Optional[float] = None,
    dpi: float = 96,
) -> Tuple["Figure", List["Axes"], List["GridSpecBase"]]:
    """
    Given the ascii-art representation of the plot's layout,
    generates suitable figure, axes and grid specifications.


    Parameters
    ----------
    art (str):
        Ascii-art representing the layout.

    hspace (Optional[float], optional):
        The horizontal space between axes. Defaults to 0.5.

    wspace (Optional[float], optional):
        The vertical space between axes. Defaults to 0.6.

    width (Optional[float], optional):
        Figure width in inches. Defaults to 12.

    height (Optional[float], optional):
        Figure height in inches. Defaults to 8.

    width_factor (Optional[float], optional):
        To determine the width, each character in the ascii-art corresponds to this
        many inches. Overrides `width`. Defaults to None.

    height_factor (Optional[float], optional):
        To determine the height, each
        character in the ascii-art corresponds to this many inches. Overrides
        `height`. Defaults to None.

    dpi (float, optional):
        Dots-per-inch of the figure. Defaults to 96.

    Returns
    -------
    A tuple of three elements:

      1. A matplotlib figure
      2. A dictionary of axes named as in the art
      3. A dictionary of `GridSpec`'s named as the axes they contain
    """
    src = StringIO()
    generate_source_code(
        art,
        annotate=False,
        file=src,
        wspace=wspace,
        hspace=hspace,
        width=width,
        height=height,
        width_factor=width_factor,
        height_factor=height_factor,
        dpi=dpi,
    )
    src.seek(0)

    defs: Dict[str, Any] = {}
    exec(src.read(), defs)  # pylint: disable=exec-used
    return defs["fig"], defs["axes"], defs["gridspecs"]
