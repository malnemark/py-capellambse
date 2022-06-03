# Copyright DB Netz AG and the capellambse contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import collections.abc as cabc
import dataclasses
import json
import os
import pathlib
import typing as t

from capellambse.svg.drawing import LabelDict

ContentsDict = t.TypedDict(
    "ContentsDict",
    {
        "type": str,
        "id": str,
        "class": str,
        "points": t.List[t.List[int]],
        "x": float,
        "y": float,
        "width": float,
        "height": float,
        "label": t.Union[LabelDict, str],
    },
    total=False,
)


class SVGDiagram:
    """An SVG diagram that can be drawn on and serialized.

    SVG diagram object that takes the ``metadata`` of a diagram via the
    :class:`DiagramMetadata` and a list of objects that are dictionaries
    describing the components to be drawn on the diagram canvas of type
    :class:`Drawing`.

    Example of expected json-file/string::

        {
            "name": "FA00 - Functional Architecture Example",
            "class": "LogicalArchitectureBlank",
            "x": 10,
            "y": 20,
            "width": 100,
            "height": 200,
            "contents": [
                {
                    "type": "box",
                    "id": "_ZNVPYDHuEeqOg4absf8kjA",
                    "class": "LogicalFunction",
                    "x": 150,
                    "y": 130,
                    "width": 101,
                    "height": 101,
                    "label": "example label"
                }
            ]
        }
    """

    def __init__(
        self,
        metadata: DiagramMetadata,
        objects: cabc.Sequence[ContentsDict],
    ) -> None:
        self.drawing = Drawing(metadata)
        for obj in objects:
            self.draw_object(obj)

    @classmethod
    def from_json(cls, jsonstring: str) -> SVGDiagram:
        """Create an SVGDiagram from the given JSON string.

        Parameters
        ----------
        jsonstring
            Json/dictionary in ``str`` format

        Returns
        -------
        diagram
            SVG diagram object
        """
        jsondict = json.loads(jsonstring)
        metadata = DiagramMetadata.from_dict(jsondict)
        return cls(metadata, jsondict["contents"])

    @classmethod
    def from_json_path(cls, path: str | os.PathLike) -> SVGDiagram:
        """Create an SVGDiagram from the given JSON file.

        Parameters
        ----------
        path
            path to .json file

        Returns
        -------
        diagram
            SVG diagram object
        """
        conf = pathlib.Path(path).read_text(encoding="utf-8")
        return cls.from_json(conf)

    def draw_object(self, obj: ContentsDict) -> None:
        self.drawing.draw_object(obj)

    def save_drawing(self, pretty: bool = False, indent: int = 2) -> None:
        self.drawing.save(pretty=pretty, indent=indent)

    def to_string(self) -> str:
        return self.drawing.tostring()


DiagramMetadataDict = t.TypedDict(
    "DiagramMetadataDict",
    {
        "name": str,
        "contents": t.Sequence[ContentsDict],
        "x": float,
        "y": float,
        "width": float,
        "height": float,
        "class": t.Union[str, None],
    },
)


@dataclasses.dataclass
class DiagramMetadata:
    """Holds metadata about a diagram.

    The metadata of a diagram includes the diagram-name, ``(x, y)``
    position, ``(w, h)`` size, the viewbox string and the diagram class,
    e.g. ``LogicalArchitectureBlank``.
    """

    def __init__(
        self,
        pos: tuple[float, float],
        size: tuple[float, float],
        name: str,
        class_: str | None,
        **_kw: t.Any,
    ) -> None:
        # Add padding to viewbox to account for drawn borders
        self.pos: tuple[float, float] = tuple(i - 10 for i in pos)  # type: ignore[assignment]
        self.size: tuple[float, float] = tuple(i + 20 for i in size)  # type: ignore[assignment]
        self.viewbox = " ".join(map(str, self.pos + self.size))
        self.class_ = class_
        self.name = name

    @classmethod
    def from_dict(cls, data: DiagramMetadataDict) -> DiagramMetadata:
        name = data.get("name")
        if not name:
            raise TypeError("No diagram name defined")
        return cls(
            (data["x"], data["y"]),
            (data["width"], data["height"]),
            name,
            data["class"],
        )


from .drawing import Drawing
