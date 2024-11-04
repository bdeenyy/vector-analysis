from PyQt6.QtWidgets import (QGraphicsScene, QGraphicsView, QFrame,
                             QVBoxLayout, QGraphicsProxyWidget, QSizePolicy)
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np
from matplotlib.patches import Polygon


class VectorPlotView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Настройка сцены
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # Настройка отображения
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFrameStyle(QFrame.Shape.NoFrame)

        # Настройка фона
        self.setBackgroundBrush(QColor(255, 255, 255))

        # Создание matplotlib figure
        self.figure = Figure(figsize=(6, 6), dpi=100)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.axes = self.figure.add_subplot(111)
        self.triangle = None

        # Добавление canvas на сцену через прокси-виджет
        self.proxy = QGraphicsProxyWidget()
        self.proxy.setWidget(self.canvas)
        self.scene.addItem(self.proxy)

        # Настройка размеров и политики
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding)
        self.setMinimumSize(200, 200)

    def plot_vector_diagram(self, vector_data, azimuth, is_clockwise):
        """Plot vector diagram with improved error handling"""
        try:
            self.axes.clear()

            # Plot the diagram
            azimuth_rad = np.radians(azimuth)
            self.triangle = self._create_triangle(azimuth_rad)
            self.axes.add_patch(self.triangle)
            self._draw_perpendiculars(self.triangle.get_xy(), is_clockwise)

            lengths = vector_data.as_list()
            vectors = self._calculate_vectors(lengths, is_clockwise)
            resultant = np.sum(vectors, axis=0)
            rotated_resultant = self._rotate_vector(resultant, azimuth_rad)

            self._draw_resultant(rotated_resultant, vector_data.name,
                                 np.linalg.norm(resultant))
            self._set_plot_properties()

            # Update canvas and adjust view
            self.canvas.draw()
            self._adjust_view()

        except Exception as e:
            print(f"Error plotting vector diagram: {str(e)}")

    def _create_triangle(self, azimuth):
        """Create triangle with specified rotation"""
        points = np.array([
            [0, 1],
            [-np.sqrt(3) / 2, -0.5],
            [np.sqrt(3) / 2, -0.5]
        ])

        rotated_points = self._rotate_points(points, azimuth)
        return Polygon(rotated_points, fill=False, color='black')

    def _rotate_points(self, points, angle):
        """Rotate points by given angle"""
        rotation_matrix = np.array([
            [np.cos(angle), -np.sin(angle)],
            [np.sin(angle), np.cos(angle)]
        ])
        return points @ rotation_matrix

    def _calculate_vectors(self, lengths, is_clockwise):
        """Calculate vectors from lengths and direction"""
        vectors = np.zeros((3, 2))
        angle = 0
        for i, length in enumerate(lengths):
            radians = np.radians(angle)
            vectors[i] = [length * np.cos(radians), length * np.sin(radians)]
            angle += -120 if is_clockwise else 120
        return vectors

    def _rotate_vector(self, vector, angle):
        """Rotate vector by given angle"""
        rotation_matrix = np.array([
            [np.cos(angle), -np.sin(angle)],
            [np.sin(angle), np.cos(angle)]
        ])
        return np.dot(rotation_matrix, vector)

    def _draw_perpendiculars(self, triangle_points, is_clockwise):
        """Draw perpendicular lines with labels"""
        labels = ["ОП2", "ОП1", "ОП3"] if is_clockwise else ["ОП3", "ОП1", "ОП2"]

        for i in range(3):
            p1 = triangle_points[i]
            p2 = triangle_points[(i + 1) % 3]
            mid = (p1 + p2) / 2

            center = np.array([0, 0])
            to_mid = mid - center
            perp = to_mid / np.linalg.norm(to_mid) * 0.3

            self.axes.plot([mid[0], mid[0] + perp[0]],
                           [mid[1], mid[1] + perp[1]],
                           'gray', linestyle='--')

            label_pos = mid + perp * 1.2
            self.axes.text(label_pos[0], label_pos[1],
                           labels[i],
                           color='gray',
                           horizontalalignment='center',
                           verticalalignment='center')

    def _draw_resultant(self, resultant, name, length):
        """Draw resultant vector with labels"""
        norm = np.linalg.norm(resultant)
        if norm != 0:
            normalized_resultant = resultant / norm * 0.8
        else:
            normalized_resultant = resultant

        self.axes.quiver(0, 0,
                         normalized_resultant[0], normalized_resultant[1],
                         angles='xy', scale_units='xy', scale=1,
                         color='red', width=0.005)

        self.axes.text(0, 1.3,
                       f"отм. + {name} м\n{round(length)} мм",
                       horizontalalignment='center',
                       verticalalignment='center')

    def _adjust_view(self):
        """Adjust view to fit content with proper scaling"""
        self.scene.setSceneRect(self.proxy.boundingRect())
        self.fitInView(self.scene.sceneRect(),
                       Qt.AspectRatioMode.KeepAspectRatio)

    def resizeEvent(self, event):
        """Handle resize events properly"""
        super().resizeEvent(event)
        if hasattr(self, 'proxy'):
            self._adjust_view()

    def _set_plot_properties(self):
        """Set matplotlib plot properties"""
        self.axes.set_aspect('equal')
        self.axes.grid(True, linestyle='--', alpha=0.3)
        self.axes.set_xlim(-1.5, 1.5)
        self.axes.set_ylim(-1.5, 1.5)
        self.axes.axis('off')
        self.figure.tight_layout(pad=0.1)