import json
import logging
from typing import Any, List, Dict
from Model.Schedule import Schedule

class JsonOutput:
    @staticmethod
    def write_json(schedule: Schedule, path: str) -> List[Dict[str, Any]]:
        """
        Пишет расписание в JSON-файл.
        """
        classes = schedule._classes  # Рекомендуется заменить на публичное свойство
        data: List[Dict[str, Any]] = []
        try:
            for course_class, reservation in classes.items():
                course = getattr(course_class, "Course", None) or getattr(course_class, "Course_info", None)
                if course is None:
                    logging.warning(f"Не найден course для {course_class}")
                    continue
                day = getattr(reservation, "Day", None)
                time_slot = getattr(reservation, "Time", None) or getattr(reservation, "Timeslot", None)
                room = getattr(reservation, "Room", None)
                room_name = getattr(room, "Name", str(room))
                professors = [getattr(p, "Name", str(p)) for p in getattr(course_class, "Professors", [])]
                groups = [getattr(g, "Name", str(g)) for g in getattr(course_class, "Groups", [])]

                item = {
                    "CourseID": course.Id,
                    "CourseName": course.Name,
                    "Section": getattr(course_class, "Section", ""),
                    "Day": day,
                    "TimeSlot": time_slot,
                    "Room": room_name,
                    "Professors": professors,
                    "Groups": groups
                }
                data.append(item)

            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            return data
        except Exception as e:
            logging.exception(f"Ошибка записи JSON в {path}")
            raise