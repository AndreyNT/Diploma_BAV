from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import codecs
from pathlib import Path
import os
import tempfile
from datetime import datetime, timedelta
import time
import csv
import logging

from Model.Configuration import Configuration
from GeneticAlgorithm import GeneticAlgorithm
from Output.HtmlOutput import HtmlOutput
from Output.CsvOutput import CsvOutput
from Output.JsonOutput import JsonOutput

# Конфигурация
CONFIG_FOLDER = os.getenv('SCHEDULE_FOLDER', '/app/data')

TEMP_DIR = tempfile.gettempdir()
FILE_LIFETIME_HOURS = 2400  # хранить временные файлы не дольше 24 часов

app = FastAPI(title="Schedule API", version="1.0.0")

class ScheduleRequest(BaseModel):
    file_name: str

def clean_old_temp_files():
    now = datetime.now()
    threshold = now - timedelta(hours=FILE_LIFETIME_HOURS)
    for file in Path(CONFIG_FOLDER).glob("*_schedule.csv"):
        if datetime.fromtimestamp(file.stat().st_mtime) < threshold:
            try:
                file.unlink()
            except Exception as e:
                print(f"Не удалось удалить файл: {file} — {e}")
    for file in Path(CONFIG_FOLDER).glob("*.html"):
        if datetime.fromtimestamp(file.stat().st_mtime) < threshold:
            try:
                file.unlink()
            except Exception as e:
                print(f"Не удалось удалить файл: {file} — {e}")


def convert_path(path):
    if os.path.exists('/.dockerenv'):  # если запущено в Docker
        return path.replace('/app/data', 'C:/Schedule_test')
    return path

@app.post("/schedule")
async def generate_schedule(request: ScheduleRequest):
    start_time = int(round(time.time() * 1000))

    # Проверяем, запущено ли приложение в Docker
    is_docker = os.path.exists('/.dockerenv')
    CONFIG_FOLDER = os.getenv('SCHEDULE_FOLDER', '/app/data' if is_docker else 'C:/Schedule_test/')

    # Формируем путь к файлу в корне диска C
    safe_file_name = os.path.basename(request.file_name)
    file_path = os.path.join(CONFIG_FOLDER, safe_file_name)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Файл '{safe_file_name}' не найден")

    try:
        # Очистка временных файлов перед выполнением
        clean_old_temp_files()

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
            "csv_path": convert_path(csv_path),
            "html_path": convert_path(html_path),
            "json_path": convert_path(json_path),
            "schedule": schedule_data
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при генерации расписания: {str(e)}")


@app.get("/test")
async def process_test():
    return {"message": "Сервис работает!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
