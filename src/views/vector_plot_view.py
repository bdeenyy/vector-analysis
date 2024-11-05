from PyQt6.QtWidgets import (QGraphicsScene, QGraphicsView, QFrame,
                             QVBoxLayout, QGraphicsProxyWidget, QSizePolicy)
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.font_manager import FontProperties
import numpy as np
from matplotlib.patches import Polygon


class VectorPlotView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_font()
        self.setup_ui()

    def setup_font(self):
        """Настройка шрифта для графика"""
        try:
            main_window = self.parent()
            while main_window and not hasattr(main_window, 'font_path'):
                main_window = main_window.parent()

            if main_window and hasattr(main_window, 'font_path'):
                # Основной шрифт для обычного текста
                self.custom_font = FontProperties(fname=main_window.font_path)
                self.custom_font.set_size(12)  # Уменьшили базовый размер шрифта

                # Шрифт для результирующего вектора
                self.result_font = FontProperties(fname=main_window.font_path)
                self.result_font.set_size(14)  # Уменьшили размер шрифта результата
                self.result_font.set_weight('bold')
            else:
                self.custom_font = None
                self.result_font = None
        except Exception as e:
            print(f"Error setting up plot font: {str(e)}")
            self.custom_font = None
            self.result_font = None

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFrameStyle(QFrame.Shape.NoFrame)

        # Белый фон
        self.setBackgroundBrush(QColor(255, 255, 255))

        # Уменьшаем размер figure
        self.figure = Figure(figsize=(6, 6), dpi=100)
        self.canvas = FigureCanvasQTAgg(self.figure)
        # Минимальные отступы
        self.figure.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
        self.axes = self.figure.add_subplot(111)

        self.proxy = QGraphicsProxyWidget()
        self.proxy.setWidget(self.canvas)
        self.scene.addItem(self.proxy)

        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                          QSizePolicy.Policy.Expanding)
        self.setMinimumSize(250, 250)




    def _create_triangle(self, azimuth):
        """Create triangle with specified rotation"""
        # Уменьшаем размер треугольника
        scale = 0.8  # Уменьшили масштаб
        points = np.array([
            [0, scale],
            [-np.sqrt(3) / 2 * scale, -0.5 * scale],
            [np.sqrt(3) / 2 * scale, -0.5 * scale]
        ])

        rotated_points = self._rotate_points(points, azimuth)
        return Polygon(rotated_points, fill=False, color='black', linewidth=1.0)


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
            # Уменьшаем длину перпендикулярных линий
            perp = to_mid / np.linalg.norm(to_mid) * 0.2

            self.axes.plot([mid[0], mid[0] + perp[0]],
                           [mid[1], mid[1] + perp[1]],
                           'gray', linestyle='--', linewidth=0.8)

            label_pos = mid + perp * 1.1
            text = self.axes.text(label_pos[0], label_pos[1],
                                  labels[i],
                                  color='gray',
                                  horizontalalignment='center',
                                  verticalalignment='center',
                                  fontsize=10)  # Явно задаем размер шрифта

            if self.custom_font:
                text.set_fontproperties(self.custom_font)

    def _draw_resultant(self, resultant, name, length):
        """Draw resultant vector with labels"""
        norm = np.linalg.norm(resultant)
        if norm != 0:
            normalized_resultant = resultant / norm * 0.7  # Уменьшили длину вектора
        else:
            normalized_resultant = resultant

        # Рисуем результирующий вектор
        self.axes.quiver(0, 0,
                         normalized_resultant[0], normalized_resultant[1],
                         angles='xy', scale_units='xy', scale=1,
                         color='red', width=0.006)

        # Подпись результата
        text = self.axes.text(0, 1.1,  # Уменьшили отступ сверху
                              f"отм. + {name} м\n{round(length)} мм",
                              horizontalalignment='center',
                              verticalalignment='center',
                              color='red',
                              bbox=dict(facecolor='white',
                                        edgecolor='none',
                                        alpha=0.8,
                                        pad=1))  # Уменьшили отступ вокруг текста

        if self.result_font:
            text.set_fontproperties(self.result_font)

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

    def _set_plot_properties(self):
        """Set matplotlib plot properties"""
        self.axes.set_aspect('equal')
        self.axes.grid(True, linestyle='--', alpha=0.2, linewidth=0.5)
        # Уменьшаем область отображения
        self.axes.set_xlim(-1.0, 1.0)
        self.axes.set_ylim(-1.0, 1.0)
        self.axes.axis('off')
        self.figure.tight_layout(pad=0.1)  # Минимальные отступы