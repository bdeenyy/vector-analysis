# src/utils/app_manager.py

import os
import sys
import shutil
import tempfile
import logging
import time
from datetime import datetime
from pathlib import Path
from PyQt6.QtCore import QSettings
from src.config.config import AppConfig


class AppManager:
    """Менеджер приложения для управления ресурсами и настройками"""

    def __init__(self):
        self.config = AppConfig
        self.settings = QSettings(self.config.APP_NAME, self.config.APP_NAME)

        # Инициализация путей
        self.paths = self._initialize_paths()

        # Настройка базовой структуры
        self._setup_directories()
        self._setup_logging()

        # Очистка при запуске
        self._cleanup_old_files()

        # Загрузка пользовательских настроек
        self.load_settings()

    def _initialize_paths(self):
        """Инициализация всех путей приложения"""
        if getattr(sys, 'frozen', False):
            # Если приложение собрано PyInstaller
            base_path = os.path.dirname(sys.executable)
        else:
            # Если запущено из исходников
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        paths = {
            'base': base_path,
            'temp': os.path.join(tempfile.gettempdir(), f'{self.config.APP_NAME}_temp'),
            'user_data': self._get_app_data_dir(),
            'resources': os.path.join(base_path, self.config.RESOURCES_DIR),
            'icons': os.path.join(base_path, self.config.ICONS_DIR),
            'fonts': os.path.join(base_path, self.config.FONTS_DIR)
        }

        # Добавляем пути для пользовательских данных
        paths.update({
            'logs': os.path.join(paths['user_data'], 'logs'),
            'config': os.path.join(paths['user_data'], 'config'),
            'exports': os.path.join(paths['user_data'], 'exports'),
            'cache': os.path.join(paths['user_data'], 'cache')
        })

        return paths

    def _get_app_data_dir(self):
        """Получить директорию для пользовательских данных приложения"""
        if sys.platform == 'win32':
            base_dir = os.environ.get('APPDATA')
        elif sys.platform == 'darwin':
            base_dir = os.path.expanduser('~/Library/Application Support')
        else:
            base_dir = os.path.expanduser('~/.local/share')

        return os.path.join(base_dir, self.config.APP_NAME)

    def _setup_directories(self):
        """Создание всех необходимых директорий"""
        for path in self.paths.values():
            if isinstance(path, str) and not path.endswith('.exe'):
                os.makedirs(path, exist_ok=True)

    def _setup_logging(self):
        """Настройка системы логирования"""
        log_file = os.path.join(
            self.paths['logs'],
            f"{self.config.APP_NAME}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(self.config.APP_NAME)
        self.logger.info(f"Приложение запущено. Версия: {self.config.VERSION}")

    def _cleanup_old_files(self):
        """Очистка старых файлов"""
        try:
            # Очистка временных файлов
            self._cleanup_directory(
                self.paths['temp'],
                days=self.config.TEMP_FILES_TTL_DAYS
            )

            # Очистка логов
            self._cleanup_directory(
                self.paths['logs'],
                days=self.config.LOG_FILES_TTL_DAYS
            )

            # Очистка кэша
            self._cleanup_directory(
                self.paths['cache'],
                days=7  # Неделя для кэша
            )

            # Очистка пустых директорий
            for path in [self.paths['temp'], self.paths['cache']]:
                self._cleanup_empty_dirs(path)

            self.logger.info("Очистка старых файлов выполнена успешно")
        except Exception as e:
            self.logger.error(f"Ошибка при очистке файлов: {e}")

    def load_settings(self):
        """Загрузка пользовательских настроек"""
        # Загружаем настройки или используем значения по умолчанию
        self.settings_data = {
            'font_size': self.settings.value('font_size', self.config.FONT_SIZE),
            'result_font_size': self.settings.value('result_font_size', self.config.RESULT_FONT_SIZE),
            'last_export_dir': self.settings.value('last_export_dir', ''),
            'plot_dpi': self.settings.value('plot_dpi', self.config.PLOT_DPI),
            'pdf_dpi': self.settings.value('pdf_dpi', self.config.PDF_DPI)
        }

    def save_settings(self):
        """Сохранение пользовательских настроек"""
        for key, value in self.settings_data.items():
            self.settings.setValue(key, value)
        self.settings.sync()

    def get_resource_path(self, resource_type, filename):
        """Получить путь к ресурсу"""
        if resource_type in self.paths:
            path = os.path.join(self.paths[resource_type], filename)
            if os.path.exists(path):
                return path
        return None

    def get_temp_file_path(self, filename):
        """Получить путь для временного файла"""
        return os.path.join(self.paths['temp'], filename)

    def get_export_path(self, filename):
        """Получить путь для экспорта файла"""
        if not self.settings_data['last_export_dir']:
            self.settings_data['last_export_dir'] = os.path.expanduser('~')
        return os.path.join(self.settings_data['last_export_dir'], filename)

    def cleanup_on_exit(self):
        """Очистка при выходе из приложения"""
        try:
            # Сохраняем настройки
            self.save_settings()

            # Очищаем временные файлы
            if os.path.exists(self.paths['temp']):
                shutil.rmtree(self.paths['temp'], ignore_errors=True)

            # Логируем завершение работы
            self.logger.info("Приложение завершено корректно")

            # Закрываем логирование
            logging.shutdown()
        except Exception as e:
            print(f"Ошибка при завершении работы: {e}")

    def _cleanup_directory(self, directory, days):
        """Очистка файлов в директории старше указанного количества дней"""
        if not os.path.exists(directory):
            return

        cutoff_time = time.time() - (days * 86400)

        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    if os.path.getctime(file_path) < cutoff_time:
                        os.remove(file_path)
                        self.logger.debug(f"Удален старый файл: {file_path}")
                except Exception as e:
                    self.logger.error(f"Ошибка при удалении файла {file_path}: {e}")

    def _cleanup_empty_dirs(self, directory):
        """Рекурсивное удаление пустых директорий"""
        for root, dirs, files in os.walk(directory, topdown=False):
            for dirname in dirs:
                dir_path = os.path.join(root, dirname)
                try:
                    if not os.listdir(dir_path):
                        os.rmdir(dir_path)
                        self.logger.debug(f"Удалена пустая директория: {dir_path}")
                except Exception as e:
                    self.logger.error(f"Ошибка при удалении директории {dir_path}: {e}")