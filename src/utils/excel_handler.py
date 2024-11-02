from PyQt6.QtWidgets import QFileDialog, QMessageBox
import pandas as pd
from src import VectorData


class ExcelHandler:
    @staticmethod
    def load_from_excel():
        """
        Открывает диалог выбора Excel файла и загружает данные

        Returns:
            list: Список объектов VectorData
        """
        try:
            # Открываем диалог выбора файла
            file_name, _ = QFileDialog.getOpenFileName(
                None,
                "Выберите Excel файл",
                "",
                "Excel Files (*.xlsx *.xls)"
            )

            if not file_name:  # Если пользователь отменил выбор
                return []

            # Читаем Excel файл
            df = pd.read_excel(file_name)

            vector_data_list = []

            # Перебираем строки данных
            for index, row in df.iterrows():
                try:
                    # Берём первые 4 столбца
                    values = row.values[:4]
                    if len(values) < 4:
                        continue

                    name = str(values[0])
                    # Преобразуем значения в float, заменяя ошибочные на 0
                    try:
                        length1 = float(values[1])
                    except (ValueError, TypeError):
                        length1 = 0.0

                    try:
                        length2 = float(values[2])
                    except (ValueError, TypeError):
                        length2 = 0.0

                    try:
                        length3 = float(values[3])
                    except (ValueError, TypeError):
                        length3 = 0.0

                    vector_data = VectorData(name, length1, length2, length3)
                    vector_data_list.append(vector_data)

                except Exception as e:
                    print(f"Ошибка в строке {index + 1}: {str(e)}")
                    continue

            if not vector_data_list:
                QMessageBox.warning(None, "Предупреждение", "Не удалось загрузить данные из файла")
                return []

            return vector_data_list

        except Exception as e:
            QMessageBox.critical(None, "Ошибка", f"Ошибка при загрузке файла: {str(e)}")
            return []

    @staticmethod
    def save_to_excel(vector_data_list, file_path):
        """
        Сохраняет данные в Excel файл

        Args:
            vector_data_list (list): Список объектов VectorData
            file_path (str): Путь для сохранения файла
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
            QMessageBox.critical(None, "Ошибка", f"Ошибка при сохранении файла: {str(e)}")