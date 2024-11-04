from PyQt6.QtWidgets import QFileDialog, QMessageBox
import pandas as pd
from src.models.vector_data import VectorData


class ExcelHandler:
    @staticmethod
    def load_from_excel():
        """
        Открывает диалоговое окно для выбора Excel файла и загружает векторные данные.
        Берет первые 4 колонки, начиная со второй строки.

        Возвращает:
            list: Список объектов VectorData, содержащий загруженные данные.
                  Возвращает пустой список, если загрузка не удалась или пользователь отменил.
        """
        try:
            # Открытие диалогового окна для выбора файла
            file_name, _ = QFileDialog.getOpenFileName(
                None,
                "Выберите Excel файл",
                "",
                "Excel Files (*.xlsx *.xls)"
            )

            if not file_name:
                return []

            # Чтение Excel файла, пропуская первую строку
            df = pd.read_excel(file_name, skiprows=1)

            # Обработка данных
            vector_data_list = []
            for index, row in df.iterrows():
                try:
                    # Берем только первые 4 колонки
                    values = row.values[:4]
                    if len(values) < 4:
                        continue

                    vector_data = VectorData(
                        name=str(values[0]),
                        length1=ExcelHandler._safe_float_convert(values[1]),
                        length2=ExcelHandler._safe_float_convert(values[2]),
                        length3=ExcelHandler._safe_float_convert(values[3])
                    )
                    vector_data_list.append(vector_data)

                except Exception as e:
                    print(f"Ошибка в строке {index + 2}: {str(e)}")
                    continue

            if not vector_data_list:
                QMessageBox.warning(
                    None,
                    "Предупреждение",
                    "Не удалось загрузить данные из файла"
                )
                return []

            return vector_data_list

        except pd.errors.EmptyDataError:
            QMessageBox.critical(None, "Ошибка", "Excel файл пуст")
            return []

        except Exception as e:
            QMessageBox.critical(None, "Ошибка", f"Ошибка при загрузке файла: {str(e)}")
            return []

    @staticmethod
    def save_to_excel(vector_data_list, file_path):
        """
        Сохраняет векторные данные в Excel файл.

        Аргументы:
            vector_data_list (list): Список объектов VectorData для сохранения
            file_path (str): Путь, по которому сохраняется Excel файл
        """
        try:
            data = []
            for vector_data in vector_data_list:
                data.append({
                    'Сечение': vector_data.name,
                    'ОП1': vector_data.length1,
                    'ОП2': vector_data.length2,
                    'ОП3': vector_data.length3
                })

            df = pd.DataFrame(data)
            df.to_excel(file_path, index=False)

        except Exception as e:
            QMessageBox.critical(
                None,
                "Ошибка",
                f"Ошибка при сохранении файла: {str(e)}"
            )

    @staticmethod
    def _safe_float_convert(value):
        """
        Безопасно преобразует значение в float.

        Аргументы:
            value: Значение для преобразования

        Возвращает:
            float: Преобразованное значение или 0.0, если преобразование не удалось
        """
        try:
            result = float(value)
            return result if not pd.isna(result) else 0.0
        except (ValueError, TypeError):
            return 0.0
