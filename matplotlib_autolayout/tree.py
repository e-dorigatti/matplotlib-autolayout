"""
Contains the definitions of tree nodes and functionality
to build the tree and the source code.
"""
import sys
from abc import ABC, abstractmethod
from collections import Counter
from typing import IO, Any, Dict, List, Optional  # pylint: disable=unused-import


class TreeNode(ABC):
    """
    Represent a node in the tree, corresponding to
    a connected rectangular region of the whole plot area.
    """

    def __init__(self, name: str, top: int, left: int, bottom: int, right: int):
        self.name = name
        self.top = top
        self.left = left
        self.bottom = bottom
        self.right = right

    @property
    def width(self) -> int:
        """
        Width of the tree, including all children.
        """
        return self.right - self.left + 1

    @property
    def height(self) -> int:
        """
        Height of the tree, including all children.
        """
        return self.bottom - self.top + 1

    def aligned_vertically(self, other: "TreeNode") -> bool:
        """
        Returns true if the two nodes are vertically adjacent and of the same width.
        """
        return (
            self.left == other.left
            and self.right == other.right
            and self.bottom + 1 == other.top
        ) or (
            self.left == other.left
            and self.right == other.right
            and self.top == other.bottom + 1
        )

    def aligned_horizontally(self, other: "TreeNode") -> bool:
        """
        Returns true if the two nodes are horizontally adjacent and of the same height.
        """
        return (
            self.top == other.top
            and self.bottom == other.bottom
            and self.right + 1 == other.left
        ) or (
            self.top == other.top
            and self.bottom == other.bottom
            and self.left == other.right + 1
        )

    def pprint(self, level: int = 0) -> None:
        """
        Pretty-prints the node and its children.
        """

    @abstractmethod
    def generate_source_code(
        self,
        root: Optional[str] = None,
        file: IO = sys.stdout,
        wspace: Optional[float] = None,
        hspace: Optional[float] = None,
    ) -> None:
        """
        Generates the source code to create and arrange the axes in this tree.
        """


class Axis(TreeNode):
    """
    Represents a leaf of the tree, i.e. a matplotlib axis that can be plotted on.
    """

    def pprint(self, level: int = 0) -> None:
        indent = " " * level
        print(indent, f"Axis {self.name}")
        print(indent, f"  top-left: {self.top}-{self.left}")
        print(indent, f"  bottom-right: {self.bottom}-{self.right}")

    def generate_source_code(
        self,
        root: Optional[str] = None,
        file: IO = sys.stdout,
        wspace: Optional[float] = None,
        hspace: Optional[float] = None,
    ) -> None:
        file.write(f'axes["ax_{self.name}"] = fig.add_subplot({root})\n')


class GridSpec(TreeNode):
    """
    An internal node in the tree whose children are arranged into a grid.
    """

    def __init__(
        self,
        name: str,
        axes: List[TreeNode],
        top: int,
        left: int,
        bottom: int,
        right: int,
        height_ratios: List[int],
        width_ratios: List[int],
    ):
        super().__init__(name, top, left, bottom, right)
        self.name = name
        self.axes = axes
        self.height_ratios = height_ratios
        self.width_ratios = width_ratios

    def can_merge(self, other: "GridSpec") -> bool:
        """
        Returns true if the two trees can be merged into a larger tree.
        """
        return self != other and (
            self.aligned_horizontally(other) or self.aligned_vertically(other)
        )

    def merge(self, other: "GridSpec") -> "GridSpec":
        """
        Merges the two trees, creating a new tree with two children.
        """
        assert self != other

        hr = wr = None
        if self.aligned_vertically(other):
            wr = [self.width]
            hr = [self.height, other.height]
        elif self.aligned_horizontally(other):
            wr = [self.width, other.width]
            hr = [self.height]
        else:
            raise ValueError("cannot merge")

        return GridSpec(
            self.name + other.name,
            [self, other],
            min(self.top, other.top),
            min(self.left, other.left),
            max(self.bottom, other.bottom),
            max(self.right, other.right),
            hr,
            wr,
        )

    def can_expand(self, other: "GridSpec") -> bool:
        """
        Returns true if this tree can be expanded horizontally or vertically
        to include the other tree.
        """
        return self != other and (
            (self.aligned_vertically(other) and self.width_ratios == other.width_ratios)
            or (
                self.aligned_horizontally(other)
                and self.height_ratios == other.height_ratios
            )
        )

    def expand(self, other: "GridSpec") -> "GridSpec":
        """
        Horizontally or vertically expands this tree to include the other tree.
        """
        assert self != other

        wr = hr = None
        if self.width_ratios == other.width_ratios and self.aligned_vertically(other):
            wr = self.width_ratios
            hr = self.height_ratios + other.height_ratios
        elif self.height_ratios == other.height_ratios and self.aligned_horizontally(
            other
        ):
            wr = self.width_ratios + other.width_ratios
            hr = self.height_ratios
        else:
            raise ValueError("cannot expand")

        return GridSpec(
            self.name + other.name,
            self.axes + other.axes,
            min(self.top, other.top),
            min(self.left, other.left),
            max(self.bottom, other.bottom),
            max(self.right, other.right),
            hr,
            wr,
        )

    def sort_axes(self) -> None:
        """
        Sorts the children from top to bottom and left to right.
        """
        self.axes = list(sorted(self.axes, key=lambda a: (a.top, a.left)))
        wr, hr = [], []
        last_top = None

        for a in self.axes:
            if last_top is None or a.top != last_top:
                last_top = a.top
                hr.append(a.height)
            if a.top == self.axes[0].top:
                wr.append(a.width)

            if isinstance(a, GridSpec):
                a.sort_axes()

        assert Counter(self.width_ratios) == Counter(wr)
        self.width_ratios = wr

        assert Counter(self.height_ratios) == Counter(hr)
        self.height_ratios = hr

    def generate_source_code(
        self,
        root: Optional[str] = None,
        file: IO = sys.stdout,
        wspace: Optional[float] = None,
        hspace: Optional[float] = None,
    ) -> None:
        name = "gs_" + "".join(sorted(self.name))
        if root is None:
            file.write(f'\ngridspecs["{name}"] = mpl.gridspec.GridSpec(\n')
            file.write("    figure=fig,\n")
        else:
            file.write(
                f'\ngridspecs["{name}"] = mpl.gridspec.GridSpecFromSubplotSpec(\n'
            )
            file.write(f"    subplot_spec={root},\n")

        file.write(f"    nrows={len(self.height_ratios)},\n")
        file.write(f"    ncols={len(self.width_ratios)},\n")
        file.write(f"    height_ratios={self.height_ratios},\n")
        file.write(f"    width_ratios={self.width_ratios},\n")

        if wspace is not None:
            ws = wspace / (sum(self.width_ratios) / len(self.width_ratios))
            file.write(f"    wspace={ws},\n")
        if hspace is not None:
            hs = hspace / (sum(self.height_ratios) / len(self.height_ratios))
            file.write(f"    hspace={hs},\n")
        file.write(")\n")

        for i, a in enumerate(self.axes):
            a.generate_source_code(
                f'gridspecs["{name}"][{i}]', file=file, wspace=wspace, hspace=hspace
            )

    def pprint(self, level: int = 0) -> None:
        indent = " " * level
        print(indent, "GridSpec")
        print(indent, f"  top-left: {self.top}-{self.left}")
        print(indent, f"  bottom-right: {self.bottom}-{self.right}")
        print(indent, "  widths: ", ", ".join(map(str, self.width_ratios)))
        print(indent, "  heights: ", ", ".join(map(str, self.height_ratios)))
        print(indent, "  children:")
        for a in self.axes:
            a.pprint(level + 4)


def find_axis_node(mat: List[List[str]], name: str) -> GridSpec:
    """
    Constructs the rectangular region containing the axis of the given name.
    """
    count = 0
    left = len(mat[0])
    top = len(mat)
    bottom = 0
    right = 0

    for i, row in enumerate(mat):
        for j, char in enumerate(row):
            if char == name:
                count += 1
                left = min(j, left)
                right = max(j, right)
                top = min(i, top)
                bottom = max(i, bottom)

    width, height = right - left + 1, bottom - top + 1
    if count != height * width:
        raise ValueError(f"Axis {name} is a disconnected region")

    return GridSpec(
        name,
        [Axis(name, top, left, bottom, right)],
        top,
        left,
        bottom,
        right,
        [height],
        [width],
    )


def find_bottom_nodes(art: str) -> List[GridSpec]:
    """
    Reads an ascii-art representation of the plot area and finds all included axes.
    """
    mat = [list(row.strip()) for row in art.split("\n") if row.strip()]

    row_lengths = set(len(row) for row in mat)
    assert len(row_lengths) == 1

    nodes = []
    for c in set(c for row in mat for c in row):
        if not c.isalnum():
            raise ValueError("Only alphanumeric characters allowed")
        nodes.append(find_axis_node(mat, c))

    return nodes


def expand_one(nodes: List[GridSpec]) -> List[GridSpec]:
    """
    Finds a node that can be expanded to include
    an adjacent node and perform the expansion,
    replacing the two nodes with the result.
    """
    for n1 in nodes:
        for n2 in nodes:
            if n1.can_expand(n2):
                new_node = n1.expand(n2)
                nodes.remove(n1)
                nodes.remove(n2)
                nodes.append(new_node)
                return nodes
    return nodes


def merge_one(nodes: List[GridSpec]) -> List[GridSpec]:
    """
    Finds two nodes that can be merged into a larger
    node and performs the union, replacing the two
    nodes with the result.
    """
    for n1 in nodes:
        for n2 in nodes:
            if n1.can_merge(n2):
                new_node = n1.merge(n2)
                nodes.remove(n1)
                nodes.remove(n2)
                nodes.append(new_node)
                return nodes
    return nodes


def make_tree(nodes: List[GridSpec]) -> GridSpec:
    """
    Starting from a list of disjoint rectangular regions,
    merges all of them to create a single tree.
    """
    while len(nodes) > 1:
        # expand as much as possible
        m, n = 0, len(nodes)
        while m != n:
            nodes = expand_one(nodes)
            m, n = n, len(nodes)

        if len(nodes) > 1:
            nodes = merge_one(nodes)

    return nodes[0]
