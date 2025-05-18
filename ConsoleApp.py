import os
import sys
import traceback
import logging

from Model.Configuration import Configuration
from GeneticAlgorithm import GeneticAlgorithm
from Output.HtmlOutput import HtmlOutput
from Output.CsvOutput import CsvOutput
from Output.JsonOutput import JsonOutput

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Конфигурация
CONFIG_FOLDER = "C:/Schedule_test/"

def main(file_name):

    # Формируем путь к файлу в корне диска C
    safe_file_name = os.path.basename(file_name)
    file_path = os.path.join(CONFIG_FOLDER, safe_file_name)

    if not os.path.exists(file_path):
        logging.error(f"Файл {file_path} не найден")
        raise FileNotFoundError(f"{file_path} not found")

    try:
        # Обработаем файл
        configuration = Configuration()
        configuration.parseFile(file_path)

        # Генетический алгоритм
        alg = GeneticAlgorithm(configuration)
        print("ГА Расписание 1.0.0. Начало формирования расписания.", alg, ".\n")
        alg.run()

        # Получаем расписание из alg.result (Schedule)
        schedule = alg.result

        # Выводы
        base_name = os.path.splitext(safe_file_name)[0].rstrip("_data")
        csv_path = os.path.join(CONFIG_FOLDER, f"{base_name}.csv")
        html_path = os.path.join(CONFIG_FOLDER, f"{base_name}.html")
        json_path = os.path.join(CONFIG_FOLDER, f"{base_name}.json")

        # Формирование CSV
        CsvOutput.write_csv(schedule, csv_path)
        # Формирование HTML
        html_content = HtmlOutput.getResult(schedule)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        # Формирование JSON
        schedule_data = JsonOutput.write_json(schedule, json_path)

        return {
            "csv_path": csv_path,
            "html_path": html_path,
            "json_path": json_path,
            "schedule": schedule_data
        }

    except Exception:
        logging.exception("Ошибка при генерации расписания")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    try:
        file_name = sys.argv[1]
    except IndexError:
        file_name = "\Schedule_data.json"
    main(file_name)


