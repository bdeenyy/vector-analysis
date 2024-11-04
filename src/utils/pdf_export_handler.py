from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtGui import QPainter, QPageSize, QPageLayout, QImage
from PyQt6.QtCore import QRectF, QSizeF, Qt
import tempfile
import os


class PDFExportHandler:
    def __init__(self, main_window):
        self.main_window = main_window

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

    def _get_save_filename(self, default_name="export.pdf"):
        """Get save filename from dialog"""
        file_name, _ = QFileDialog.getSaveFileName(
            parent=self.main_window,
            caption="Сохранить PDF",
            directory=os.path.join(os.path.expanduser("~"), default_name),
            filter="PDF Files (*.pdf)",
            initialFilter="PDF Files (*.pdf)"
        )

        if file_name and not file_name.lower().endswith('.pdf'):
            file_name += '.pdf'

        return file_name

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

            vector_plots = []
            for i in range(self.main_window.vector_container.layout().count()):
                widget = self.main_window.vector_container.layout().itemAt(i).widget()
                if widget:
                    plot_container = widget.layout().itemAt(0).widget()
                    vector_plots.append(plot_container)

            for i, plot in enumerate(vector_plots):
                plot_index_on_page = i % plots_per_page
                row = plot_index_on_page // 2
                col = plot_index_on_page % 2

                if plot_index_on_page == 0 and i > 0:
                    printer.newPage()

                x = margin + col * (plot_width + margin)
                y = margin + row * (plot_height + margin)
                plot_rect = QRectF(x, y, plot_width, plot_height)

                # Save plot to temporary file
                temp_path = os.path.join(tempfile.gettempdir(), f'plot_{i}.png')
                plot.figure.savefig(temp_path, bbox_inches='tight', dpi=300)

                image = QImage(temp_path)
                scaled_image = image.scaled(
                    int(plot_width),
                    int(plot_height),
                    aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio
                )
                painter.drawImage(plot_rect, scaled_image)

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

                temp_path = os.path.join(tempfile.gettempdir(), f'dev_plot_{i}.png')
                plot.fig.set_size_inches(8, 12)
                plot.fig.savefig(temp_path, bbox_inches='tight', dpi=300)

                image = QImage(temp_path)
                scaled_image = image.scaled(
                    int(plot_width),
                    int(plot_height),
                    aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio
                )

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