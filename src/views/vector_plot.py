from PyQt6.QtWidgets import QWidget
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.patches import Polygon


class VectorPlot(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=6, height=6):
        # Создаем фигуру с заданными размерами
        self.fig = Figure(figsize=(width, height), dpi=100)
        # Добавляем оси с правильными отступами
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        self.triangle = None

        # Устанавливаем минимальные размеры
        self.setMinimumSize(200, 200)

        # Настраиваем параметры фигуры
        self.fig.set_tight_layout(True)

    def resizeEvent(self, event):
        """Handle resize event"""
        super().resizeEvent(event)
        self.fig.set_size_inches(event.size().width() / self.fig.dpi,
                                 event.size().height() / self.fig.dpi)
        self.draw()

    def plot_vector_diagram(self, vector_data, azimuth, is_clockwise):
        if self.triangle is None:  # Draw triangle only once
            azimuth_rad = np.radians(azimuth)
            self.triangle = self._create_triangle(azimuth_rad)
            self.axes.add_patch(self.triangle)
            self._draw_perpendiculars(self.triangle.get_xy(), is_clockwise)

        # Calculate and draw vector
        lengths = vector_data.as_list()
        vectors = self._calculate_vectors(lengths, is_clockwise)
        resultant = np.sum(vectors, axis=0)

        # Rotate resultant vector
        azimuth_rad = np.radians(azimuth)
        rotated_resultant = self._rotate_vector(resultant, azimuth_rad)

        # Draw vector
        self._draw_resultant(rotated_resultant, vector_data.name, np.linalg.norm(resultant))
        self._set_plot_properties()
        self.draw()

    def clear_plot(self):
        self.axes.clear()
        self.triangle = None
        self.draw()

    def _calculate_vectors(self, lengths, is_clockwise):
        vectors = np.zeros((3, 2))
        angle = 0
        for i, length in enumerate(lengths):
            radians = np.radians(angle)
            vectors[i] = [length * np.cos(radians), length * np.sin(radians)]
            angle += -120 if is_clockwise else 120
        return vectors

    def _create_triangle(self, azimuth):
        points = np.array([
            [0, 1],
            [-np.sqrt(3) / 2, -0.5],
            [np.sqrt(3) / 2, -0.5]
        ])

        rotated_points = self._rotate_points(points, azimuth)
        return Polygon(rotated_points, fill=False, color='black')

    def _rotate_points(self, points, angle):
        rotation_matrix = np.array([
            [np.cos(angle), -np.sin(angle)],
            [np.sin(angle), np.cos(angle)]
        ])
        return points @ rotation_matrix

    def _rotate_vector(self, vector, angle):
        rotation_matrix = np.array([
            [np.cos(angle), -np.sin(angle)],
            [np.sin(angle), np.cos(angle)]
        ])
        return np.dot(rotation_matrix, vector)

    def _draw_perpendiculars(self, triangle_points, is_clockwise):
        labels = ["ОП2", "ОП1", "ОП3"] if is_clockwise else ["ОП3", "ОП1", "ОП2"]

        for i in range(3):
            p1 = triangle_points[i]
            p2 = triangle_points[(i + 1) % 3]
            mid = (p1 + p2) / 2

            # Calculate vector from center to midpoint
            center = np.array([0, 0])
            to_mid = mid - center

            # Normalize and scale for consistent length
            perp = to_mid / np.linalg.norm(to_mid) * 0.3

            self.axes.plot([mid[0], mid[0] + perp[0]],
                           [mid[1], mid[1] + perp[1]],
                           'gray', linestyle='--')

            # Position label at the end of perpendicular line
            label_pos = mid + perp * 1.2
            self.axes.text(label_pos[0], label_pos[1],
                           labels[i],
                           color='gray',
                           horizontalalignment='center',
                           verticalalignment='center')

    def _draw_resultant(self, resultant, name, length):
        # Normalize vector
        norm = np.linalg.norm(resultant)
        if norm != 0:
            normalized_resultant = resultant / norm * 0.8
        else:
            normalized_resultant = resultant

        self.axes.quiver(0, 0,
                         normalized_resultant[0], normalized_resultant[1],
                         angles='xy', scale_units='xy', scale=1,
                         color='red', width=0.005)

        # Fixed position for section label at top
        self.axes.text(0, 1.3,
                       f"отм. + {name} м\n{round(length)} мм",
                       horizontalalignment='center',
                       verticalalignment='center')

    def _set_plot_properties(self):
        self.axes.set_aspect('equal')
        self.axes.grid(True, linestyle='--', alpha=0.3)
        self.axes.set_xlim(-1.5, 1.5)
        self.axes.set_ylim(-1.5, 1.5)
        self.axes.axis('off')
        # Используем tight_layout для автоматической настройки отступов
        self.fig.tight_layout(pad=0.5)