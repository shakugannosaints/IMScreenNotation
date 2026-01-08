"""Polygon shape (multi-vertex, optional fill)."""

from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QColor, QPainterPath

from .base import Shape


class Polygon(Shape):
    def __init__(self, points, fill: bool = False, closed: bool = True, preview_point=None, **kwargs):
        super().__init__(**kwargs)
        self.points = [QPointF(p) for p in (points or [])]
        self.fill = bool(fill)
        self.closed = bool(closed)
        self.preview_point = QPointF(preview_point) if preview_point is not None else None

    def draw(self, painter):
        if not self.points:
            return

        painter.setPen(self.pen)

        old_brush = painter.brush()
        if self.fill and self.closed and len(self.points) >= 3:
            painter.setBrush(self.color)

        path = QPainterPath()
        path.moveTo(self.points[0])
        for p in self.points[1:]:
            path.lineTo(p)

        if not self.closed and self.preview_point is not None:
            path.lineTo(self.preview_point)

        if self.closed and len(self.points) >= 3:
            path.closeSubpath()

        painter.drawPath(path)
        painter.setBrush(old_brush)

    def to_dict(self):
        data = super().to_dict()
        data.update(
            {
                'points': [{'x': p.x(), 'y': p.y()} for p in self.points],
                'fill': self.fill,
                'closed': self.closed,
            }
        )
        return data

    @classmethod
    def from_dict(cls, data):
        color = QColor(*data["color"])
        points = [QPointF(p['x'], p['y']) for p in data.get('points', [])]
        fill = bool(data.get('fill', False))
        closed = bool(data.get('closed', True))
        return cls(points, fill=fill, closed=closed, color=color, thickness=data["thickness"], opacity=data["opacity"])
