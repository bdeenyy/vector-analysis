from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtGui import QPainter, QPageSize, QPageLayout, QImage
from PyQt6.QtCore import QRectF, QSizeF, Qt
import tempfile
import os


class PDFExportHandler:
    def __init__(self, main_window):
        self.main_window = main_window

    def _get_save_filename(self, default_name="export.pdf"):
        """Get save filename from dialog"""
        dialog = QFileDialog(self.main_window)
        dialog.setWindowTitle("Сохранить PDF")
        dialog.setNameFilter("PDF Files (*.pdf)")
        dialog.setDefaultSuffix("pdf")
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        dialog.setViewMode(QFileDialog.ViewMode.Detail)

        # Установка начального имени файла
        dialog.selectFile(default_name)

        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            file_name = dialog.selectedFiles()[0]
            if not file_name.lower().endswith('.pdf'):
                file_name += '.pdf'
            return file_name
        return None


    def _setup_printer(self, file_name):
        """Setup printer with common settings"""
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(file_name)

        layout = QPageLayout()
        layout.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
        layout.setOrientation(QPageLayout.Orientation.Portrait)
        printer.setPageLayout(layout)

        return printer


    def export_vectors_to_pdf(self):
        """Export vector plots to PDF file"""
        try:
            file_name = self._get_save_filename("vectors.pdf")
            if not file_name:
                return False

            printer = self._setup_printer(file_name)

            page_rect = printer.pageRect(QPrinter.Unit.DevicePixel)
            margin = 40
            plots_per_page = 6

            plot_width = (page_rect.width() - 3 * margin) / 2
            plot_height = (page_rect.height() - 4 * margin) / 3

            aspect_ratio = 1.0
            if plot_width / plot_height > aspect_ratio:
                plot_width = plot_height * aspect_ratio
            else:
                plot_height = plot_width / aspect_ratio

            painter = QPainter()
            painter.begin(printer)

            # Получаем все графики из контейнера
            vector_plots = []
            layout = self.main_window.vector_container.layout()
            for i in range(layout.count()):
                item = layout.itemAt(i)
                if item and item.widget():
                    # VectorPlotView содержит сцену с графиком
                    plot = item.widget()
                    vector_plots.append(plot)

            for i, plot in enumerate(vector_plots):
                plot_index_on_page = i % plots_per_page
                row = plot_index_on_page // 2
                col = plot_index_on_page % 2

                if plot_index_on_page == 0 and i > 0:
                    printer.newPage()

                x = margin + col * (plot_width + margin)
                y = margin + row * (plot_height + margin)
                plot_rect = QRectF(x, y, plot_width, plot_height)

                # Сохраняем график во временный файл
                temp_path = os.path.join(tempfile.gettempdir(), f'plot_{i}.png')
                # Используем figure из matplotlib canvas
                plot.canvas.figure.savefig(temp_path, bbox_inches='tight', dpi=300)

                image = QImage(temp_path)
                scaled_image = image.scaled(
                    int(plot_width),
                    int(plot_height),
                    aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio
                )

                # Центрируем изображение
                x_offset = (plot_width - scaled_image.width()) / 2 if scaled_image.width() < plot_width else 0
                y_offset = (plot_height - scaled_image.height()) / 2 if scaled_image.height() < plot_height else 0

                draw_rect = QRectF(
                    plot_rect.x() + x_offset,
                    plot_rect.y() + y_offset,
                    scaled_image.width(),
                    scaled_image.height()
                )

                painter.drawImage(draw_rect, scaled_image)
                os.remove(temp_path)

            painter.end()
            return True

        except Exception as e:
            QMessageBox.critical(
                self.main_window,
                "Ошибка",
                f"Ошибка при сохранении PDF: {str(e)}"
            )
            return False

    def export_deviations_to_pdf(self):
        """Export deviation plots to PDF file"""
        try:
            file_name = self._get_save_filename("deviations.pdf")
            if not file_name:
                return False

            printer = self._setup_printer(file_name)

            page_rect = printer.pageRect(QPrinter.Unit.DevicePixel)
            margin = 40

            plot_width = (page_rect.width() - 4 * margin) / 3
            plot_height = plot_width * 1.5

            painter = QPainter()
            painter.begin(printer)

            deviation_plots = []
            for i in range(self.main_window.deviation_container.layout().count()):
                plot = self.main_window.deviation_container.layout().itemAt(i).widget()
                if plot:
                    deviation_plots.append(plot)

            for i, plot in enumerate(deviation_plots):
                x = margin + (plot_width + margin) * i
                y = margin
                plot_rect = QRectF(x, y, plot_width, plot_height)

                # Сохраняем во временный файл
                temp_path = os.path.join(tempfile.gettempdir(), f'dev_plot_{i}.png')
                plot.figure.set_size_inches(8, 12)
                plot.figure.savefig(temp_path, bbox_inches='tight', dpi=300)

                image = QImage(temp_path)
                scaled_image = image.scaled(
                    int(plot_width),
                    int(plot_height),
                    aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio
                )

                # Центрирование изображения в прямоугольнике
                x_offset = (plot_width - scaled_image.width()) / 2 if scaled_image.width() < plot_width else 0
                y_offset = (plot_height - scaled_image.height()) / 2 if scaled_image.height() < plot_height else 0

                draw_rect = QRectF(
                    plot_rect.x() + x_offset,
                    plot_rect.y() + y_offset,
                    scaled_image.width(),
                    scaled_image.height()
                )

                painter.drawImage(draw_rect, scaled_image)

                # Удаляем временный файл
                os.remove(temp_path)

            painter.end()
            return True

        except Exception as e:
            QMessageBox.critical(
                self.main_window,
                "Ошибка",
                f"Ошибка при сохранении PDF: {str(e)}"
            )
            return False