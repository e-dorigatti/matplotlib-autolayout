"""
Command line interface to generate the matplotlib source code
to generate the desired layout
"""
import sys
from io import StringIO
from typing import IO, Any, Dict, Optional

import click

from matplotlib_autolayout import generate_source_code


@click.command()
@click.argument("art-file", type=click.File("r"), default="-")
@click.option("-s", "--show", is_flag=True, default=False, help="Preview the plot")
@click.option("-ws", "--wspace", default=0.6, help="Horizontal separation between axes")
@click.option("-hs", "--hspace", default=0.5, help="Vertical separation between axes")
@click.option("-w", "--width", default=12.0, help="Figure width in inches")
@click.option("-h", "--height", default=8.0, help="Figure height in inches")
@click.option(
    "-wf",
    "--width-factor",
    type=float,
    help="To determine the width, each character in the ascii-art"
    "corresponds to this many inches. Overrides `width`.",
)
@click.option(
    "-wh",
    "--height-factor",
    type=float,
    help="To determine the height, each character in the ascii-art"
    "corresponds to this many inches. Overrides `height`.",
)
@click.option("-d", "--dpi", default=96.0, help="Dots-per-inch of the figure")
def main(art_file: IO, show: Optional[bool], **kwargs: Any) -> None:
    """
    Reads the layout ascii-art from a file (or stdin) and
    generates the necessary matplotlib code.
    """

    print("Enter ascii-art for plot layout, empty line to confirm", file=sys.stderr)
    rows = []
    for row in art_file:
        if row == "\n":
            break
        rows.append(row)

    src = StringIO()
    generate_source_code("\n".join(rows), annotate=True, file=src, **kwargs)
    src.seek(0)
    print(src.read())

    if show:
        import matplotlib.pyplot as plt  # pylint: disable=import-outside-toplevel

        src.seek(0)
        defs: Dict[str, Any] = {}
        exec(src.read(), defs)  # pylint: disable=exec-used
        plt.show()


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
