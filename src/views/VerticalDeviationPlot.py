from PyQt6.QtWidgets import QWidget
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.font_manager import FontProperties


class VerticalDeviationPlot(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=4, height=8):
        self.fig = Figure(figsize=(width, height))
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        self.setup_font()

    def setup_font(self):
        """Настройка шрифта для графика отклонений"""
        try:
            # Получаем путь к шрифту из главного окна
            main_window = self.parent()
            while main_window and not hasattr(main_window, 'font_path'):
                main_window = main_window.parent()

            if main_window and hasattr(main_window, 'font_path'):
                self.custom_font = FontProperties(fname=main_window.font_path)
                self.custom_font.set_size(14)  # Размер шрифта для графиков
            else:
                self.custom_font = None
        except Exception as e:
            print(f"Error setting up plot font: {str(e)}")
            self.custom_font = None

    def plot_deviations(self, data_list, reference_point, tolerance_mm_per_m=1.0):
        """
        Plot vertical deviations for specific reference point (ОП)

        Args:
            data_list (list): List of VectorData objects
            reference_point (int): Index of reference point (0 for ОП1, 1 for ОП2, 2 for ОП3)
            tolerance_mm_per_m (float): Allowable deviation in mm per meter of height
        """
        try:
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

            # Добавляем начальную точку (0,0)
            heights.insert(0, 0)
            deviations.insert(0, 0)

            # Calculate tolerance lines
            min_height = 0  # Начинаем с нуля
            max_height = max(heights)
            height_range = np.array([min_height, max_height])
            tolerance_lines = height_range * tolerance_mm_per_m

            # Plot tolerance lines
            self.axes.plot(tolerance_lines, height_range, 'r--', alpha=0.5,
                           label='Допустимое отклонение')
            self.axes.plot(-tolerance_lines, height_range, 'r--', alpha=0.5)

            # Fill tolerance area
            self.axes.fill_betweenx(height_range, -tolerance_lines, tolerance_lines,
                                    color='red', alpha=0.1)

            # Plot vertical line at x=0 (vertical axis)
            self.axes.axvline(x=0, color='black', linestyle='-', linewidth=0.5)

            # Plot deviations
            self.axes.scatter(deviations, heights, color='blue', zorder=3)
            self.axes.plot(deviations, heights, color='blue', linestyle='-', zorder=2,
                           label='Отклонения')

            # Highlight points outside tolerance
            for height, deviation in zip(heights, deviations):
                tolerance = height * tolerance_mm_per_m
                if abs(deviation) > tolerance:
                    self.axes.scatter(deviation, height, color='red', s=100,
                                      zorder=4, alpha=0.5)
                    # Добавляем подпись для точек вне допуска
                    if self.custom_font:
                        self.axes.annotate(
                            f'{deviation:.1f}',
                            (deviation, height),
                            xytext=(5, 5),
                            textcoords='offset points',
                            fontproperties=self.custom_font,
                            color='red'
                        )

            # Применяем кастомный шрифт к элементам графика
            if self.custom_font:
                # Заголовок
                self.axes.set_title(f"{title}\n(допуск {tolerance_mm_per_m} мм/м)",
                                    fontproperties=self.custom_font,
                                    pad=20)

                # Подписи осей
                self.axes.set_xlabel('Отклонение (мм)',
                                     fontproperties=self.custom_font,
                                     labelpad=10)
                self.axes.set_ylabel('Высота (м)',
                                     fontproperties=self.custom_font,
                                     labelpad=10)

                # Легенда
                legend = self.axes.legend(prop=self.custom_font)

                # Значения на осях
                for label in self.axes.get_xticklabels() + self.axes.get_yticklabels():
                    label.set_fontproperties(self.custom_font)

            # Настройка сетки
            self.axes.grid(True, linestyle='--', alpha=0.3)

            # Добавляем отступы вокруг графика
            self.axes.margins(x=0.1, y=0.1)

            # Устанавливаем соотношение сторон
            self.axes.set_aspect('auto')

            # Настраиваем плотную компоновку
            self.fig.tight_layout()

            # Обновляем холст
            self.draw()

        except Exception as e:
            print(f"Error plotting deviations: {str(e)}")

    def clear_plot(self):
        """Clear the plot"""
        try:
            self.axes.clear()
            self.draw()
        except Exception as e:
            print(f"Error clearing plot: {str(e)}")

    def save_plot(self, filename):
        """
        Save the plot to a file

        Args:
            filename (str): Path to save the plot
        """
        try:
            self.fig.savefig(filename, bbox_inches='tight', dpi=300)
            return True
        except Exception as e:
            print(f"Error saving plot: {str(e)}")
            return False

    def update_font_size(self, size):
        """
        Update font size for all text elements

        Args:
            size (int): New font size
        """
        try:
            if self.custom_font:
                self.custom_font.set_size(size)
                # Перерисовываем график с новым размером шрифта
                self.draw()
        except Exception as e:
            print(f"Error updating font size: {str(e)}")