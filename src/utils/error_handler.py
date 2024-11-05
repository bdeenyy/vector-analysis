# src/utils/error_handler.py

import sys
import traceback
import logging
from PyQt6.QtWidgets import QMessageBox

class ErrorHandler:
    @staticmethod
    def setup_exception_handling(app_manager):
        """Настройка глобальной обработки исключений"""
        def handle_exception(exc_type, exc_value, exc_traceback):
            # Пропускаем KeyboardInterrupt
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return

            # Логируем ошибку
            app_manager.logger.error(
                "Необработанное исключение",
                exc_info=(exc_type, exc_value, exc_traceback)
            )

            # Показываем пользователю информацию об ошибке
            error_msg = QMessageBox()
            error_msg.setIcon(QMessageBox.Icon.Critical)
            error_msg.setWindowTitle("Ошибка")
            error_msg.setText("В приложении произошла ошибка")
            error_msg.setInformativeText(str(exc_value))
            error_msg.setDetailedText(
                "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            )
            error_msg.exec()

        # Устанавливаем глобальный обработчик исключений
        sys.excepthook = handle_exception