from PyQt6.QtWidgets import QFileDialog, QMessageBox
import pandas as pd
from src.models.vector_data import VectorData


class ExcelHandler:
    @staticmethod
    def load_from_excel():
        """
        Opens a file dialog for Excel file selection and loads vector data.
        Takes first 4 columns starting from second row.

        Returns:
            list: List of VectorData objects containing the loaded data.
                 Returns empty list if loading fails or user cancels.
        """
        try:
            # Open file dialog
            file_name, _ = QFileDialog.getOpenFileName(
                None,
                "Выберите Excel файл",
                "",
                "Excel Files (*.xlsx *.xls)"
            )

            if not file_name:
                return []

            # Read Excel file, skip first row
            df = pd.read_excel(file_name, skiprows=1)

            # Process data
            vector_data_list = []
            for index, row in df.iterrows():
                try:
                    # Take only first 4 columns
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
                    print(f"Error in row {index + 2}: {str(e)}")
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
        Saves vector data to an Excel file.

        Args:
            vector_data_list (list): List of VectorData objects to save
            file_path (str): Path where to save the Excel file
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
        Safely converts a value to float.

        Args:
            value: Value to convert

        Returns:
            float: Converted value or 0.0 if conversion fails
        """
        try:
            result = float(value)
            return result if not pd.isna(result) else 0.0
        except (ValueError, TypeError):
            return 0.0