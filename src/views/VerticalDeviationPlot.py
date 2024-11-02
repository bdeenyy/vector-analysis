from PyQt6.QtWidgets import QWidget
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class VerticalDeviationPlot(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=4, height=8):
        self.fig = Figure(figsize=(width, height))
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)

    def plot_deviations(self, data_list, reference_point, tolerance_mm_per_m=1.0):
        """
        Plot vertical deviations for specific reference point (ОП)

        Args:
            data_list (list): List of VectorData objects
            reference_point (int): Index of reference point (0 for ОП1, 1 for ОП2, 2 for ОП3)
            tolerance_mm_per_m (float): Allowable deviation in mm per meter of height
        """
        self.axes.clear()

        # Extract heights and deviations
        heights = [float(data.name) if data.name else 0 for data in data_list]
        if reference_point == 0:
            deviations = [data.length1 for data in data_list]
            title = "Отклонения ОП1"
        elif reference_point == 1:
            deviations = [data.length2 for data in data_list]
            title = "Отклонения ОП2"
        else:
            deviations = [data.length3 for data in data_list]
            title = "Отклонения ОП3"

        # Calculate tolerance lines
        min_height = min(heights)
        max_height = max(heights)
        height_range = np.array([min_height, max_height])
        tolerance_lines = height_range * tolerance_mm_per_m

        # Plot tolerance lines
        self.axes.plot(tolerance_lines, height_range, 'r--', alpha=0.5, label='Допустимое отклонение')
        self.axes.plot(-tolerance_lines, height_range, 'r--', alpha=0.5)

        # Fill tolerance area
        self.axes.fill_betweenx(height_range, -tolerance_lines, tolerance_lines,
                                color='red', alpha=0.1)

        # Plot vertical line at x=0 (vertical axis)
        self.axes.axvline(x=0, color='black', linestyle='-', linewidth=0.5)

        # Plot deviations
        self.axes.scatter(deviations, heights, color='blue', zorder=3)
        self.axes.plot(deviations, heights, color='blue', linestyle='-', zorder=2)

        # Highlight points outside tolerance
        for height, deviation in zip(heights, deviations):
            tolerance = height * tolerance_mm_per_m
            if abs(deviation) > tolerance:
                self.axes.scatter(deviation, height, color='red', s=100,
                                  zorder=4, alpha=0.5)

        # Add labels and title
        self.axes.set_xlabel('Отклонение (мм)')
        self.axes.set_ylabel('Высота (м)')
        self.axes.set_title(f"{title}\n(допуск {tolerance_mm_per_m} мм/м)")

        # Add grid
        self.axes.grid(True, linestyle='--', alpha=0.3)

        # Add legend
        self.axes.legend()

        # Adjust layout
        self.fig.tight_layout()
        self.draw()

    def clear_plot(self):
        """Clear the plot"""
        self.axes.clear()
        self.draw()