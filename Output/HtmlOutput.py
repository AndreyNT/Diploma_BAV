from Model.Constant import Constant
from collections import defaultdict


class HtmlOutput:
    @staticmethod
    def init():
        # Инициализирует данные для HTML-вывода
        HtmlOutput.ROOM_COLUMN_NUMBER = Constant.DAYS_NUM + 1
        HtmlOutput.ROOM_ROW_NUMBER = Constant.DAY_HOURS + 1
        HtmlOutput.COLOR1 = "#319378"
        HtmlOutput.COLOR2 = "#CE0000"
        HtmlOutput.CRITERIAS = ("R", "S", "L", "P", "G", "T")
        HtmlOutput.CRITERIAS_DESCR = (
            "Текущая аудитория имеет {any}пересечения",
            "Текущая аудитория имеет {any}достаточно мест",
            "Аудитория с {any}достаточным количеством компьютеров (если требуется)",
            "У профессоров {any}пересекающиеся занятия",
            "У студенческих групп {any}пересекающиеся занятия",
            "У преподавателя {any}пересекающиеся занятия по времени",
        )
        HtmlOutput.PERIODS = Constant.PERIODS
        HtmlOutput.WEEK_DAYS = Constant.WEEK_DAYS

    @staticmethod
    def getCourseClass(cc, criterias, ci):
        # Генерирует HTML-контент для занятия на основе критериев
        COLOR1 = HtmlOutput.COLOR1
        COLOR2 = HtmlOutput.COLOR2
        CRITERIAS = HtmlOutput.CRITERIAS
        length_CRITERIAS = len(CRITERIAS)
        CRITERIAS_DESCR = HtmlOutput.CRITERIAS_DESCR

        sb = [
            cc.Course.Name,
            "<br />",
            "-".join(map(lambda prof: prof.Name, cc.Professors)),
            "<br />",
            "/".join(map(lambda grp: grp.Name, cc.Groups)),
            "<br />",
        ]
        if cc.LabRequired:
            sb.append("Лаборатория<br />")

        for i in range(length_CRITERIAS):
            sb.append("<span style='color:")
            if criterias[ci + i]:
                sb.append(COLOR1)
                sb.append("' title='")
                sb.append(
                    CRITERIAS_DESCR[i].format(any="" if (i == 1 or i == 2) else "нет ")
                )
            else:
                sb.append(COLOR2)
                sb.append("' title='")
                sb.append(
                    CRITERIAS_DESCR[i].format(any="не " if (i == 1 or i == 2) else "")
                )
            sb.append("'> ")
            sb.append(CRITERIAS[i])
            sb.append(" </span>")

        return sb

    @staticmethod
    def generateTimeTable(solution, slot_table):
        # Создаёт структуру расписания из решения
        ci = 0

        time_table = defaultdict(list)
        items = solution.classes.items
        ROOM_COLUMN_NUMBER = HtmlOutput.ROOM_COLUMN_NUMBER
        getCourseClass = HtmlOutput.getCourseClass

        for cc, reservation in items():
            # Координаты временного слота
            dayId = reservation.Day + 1
            periodId = reservation.Time + 1
            roomId = reservation.Room
            dur = cc.Duration

            key = (periodId, roomId)
            if key in slot_table:
                room_duration = slot_table[key]
            else:
                room_duration = ROOM_COLUMN_NUMBER * [0]
                slot_table[key] = room_duration
            room_duration[dayId] = dur

            for m in range(1, dur):
                next_key = (periodId + m, roomId)
                if next_key not in slot_table:
                    slot_table[next_key] = ROOM_COLUMN_NUMBER * [0]
                if slot_table[next_key][dayId] < 1:
                    slot_table[next_key][dayId] = -1

            if key in time_table:
                room_schedule = time_table[key]
            else:
                room_schedule = ROOM_COLUMN_NUMBER * [None]
                time_table[key] = room_schedule

            room_schedule[dayId] = "".join(getCourseClass(cc, solution.criteria, ci))
            ci += 6

        return time_table

    @staticmethod
    def getHtmlCell(content, rowspan):
        # Генерирует HTML-ячейку с контентом и rowspan
        if rowspan == 0:
            return "<td></td>"

        if content is None:
            return ""

        sb = []
        if rowspan > 1:
            sb.append("<td style='border: .1em solid black; padding: .25em' rowspan='")
            sb.append(rowspan)
            sb.append("'>")
        else:
            sb.append("<td style='border: .1em solid black; padding: .25em'>")

        sb.append(content)
        sb.append("</td>")
        return "".join(str(v) for v in sb)

    @staticmethod
    def getResult(solution):
        # Генерирует финальный HTML-результат из решения
        HtmlOutput.init()
        configuration = solution.configuration
        nr = configuration.numberOfRooms
        getRoomById = configuration.getRoomById

        slot_table = defaultdict(list)
        time_table = HtmlOutput.generateTimeTable(
            solution, slot_table
        )  # Tuple[0] = время, Tuple[1] = ID аудитории
        if not slot_table or not time_table:
            return ""

        sb = []
        for roomId in range(nr):
            room = getRoomById(roomId)
            for periodId in range(HtmlOutput.ROOM_ROW_NUMBER):
                if periodId == 0:
                    sb.append("<div id='room_")
                    sb.append(room.Name)
                    sb.append("' style='padding: 0.5em'>\n")
                    sb.append("<table style='border-collapse: collapse; width: 95%'>\n")
                    sb.append(HtmlOutput.getTableHeader(room))
                else:
                    key = (periodId, roomId)
                    room_duration = (
                        slot_table[key] if key in slot_table.keys() else None
                    )
                    room_schedule = (
                        time_table[key] if key in time_table.keys() else None
                    )
                    sb.append("<tr>")
                    for dayId in range(HtmlOutput.ROOM_COLUMN_NUMBER):
                        if dayId == 0:
                            sb.append(
                                "<th style='border: .1em solid black; padding: .25em' scope='row' colspan='2'>"
                            )
                            sb.append(HtmlOutput.PERIODS[periodId])
                            sb.append("</th>\n")
                            continue

                        if room_schedule is None and room_duration is None:
                            continue

                        content = (
                            room_schedule[dayId] if room_schedule is not None else None
                        )
                        sb.append(HtmlOutput.getHtmlCell(content, room_duration[dayId]))
                    sb.append("</tr>\n")

                if periodId == HtmlOutput.ROOM_ROW_NUMBER - 1:
                    sb.append("</table>\n</div>\n")

        return "".join(str(v) for v in sb)

    @staticmethod
    def getTableHeader(room):
        # Генерирует заголовок таблицы HTML для аудитории
        sb = [
            "<tr><th style='border: .1em solid black' scope='col' colspan='2'>Аудитория: ",
            room.Name,
            "</th>\n",
        ]
        for weekDay in HtmlOutput.WEEK_DAYS:
            sb.append(
                "<th style='border: .1em solid black; padding: .25em; width: 15%' scope='col' rowspan='2'>"
            )
            sb.append(weekDay)
            sb.append("</th>\n")
        sb.append("</tr>\n")
        sb.append("<tr>\n")
        sb.append("<th style='border: .1em solid black; padding: .25em'>Лаборатория: ")
        sb.append("Да" if room.Lab else "Нет")
        sb.append("</th>\n")
        sb.append("<th style='border: .1em solid black; padding: .25em'>Места: ")
        sb.append(room.NumberOfSeats)
        sb.append("</th>\n")
        sb.append("</tr>\n")
        return "".join(str(v) for v in sb)
