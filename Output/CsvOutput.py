import csv
import logging
from typing import Any
from Model.Schedule import Schedule

class CsvOutput:
    @staticmethod
    def write_csv(schedule: Schedule, path: str) -> None:
        """
        Пишет расписание в CSV-файл.
        """
        classes = schedule._classes  # Рекомендуется заменить на публичное свойство
        try:
            with open(path, "w", encoding="utf-8", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    "CourseID", "CourseName", "Section",
                    "Day", "TimeSlot", "Room", "Professors", "Groups"
                ])
                for course_class, reservation in classes.items():
                    course = getattr(course_class, "Course", None) or getattr(course_class, "Course_info", None)
                    if course is None:
                        logging.warning(f"Не найден course для {course_class}")
                        continue
                    day = getattr(reservation, "Day", None)
                    time_slot = getattr(reservation, "Time", None) or getattr(reservation, "Timeslot", None)
                    room = getattr(reservation, "Room", None)
                    room_name = getattr(room, "Name", str(room))
                    professors = ";".join(getattr(p, "Name", str(p)) for p in getattr(course_class, "Professors", []))
                    groups = ";".join(getattr(g, "Name", str(g)) for g in getattr(course_class, "Groups", []))

                    writer.writerow([
                        course.Id, course.Name,
                        getattr(course_class, "Section", ""),
                        day, time_slot, room_name,
                        professors, groups
                    ])
        except Exception as e:
            logging.exception(f"Ошибка записи CSV в {path}")
            raise