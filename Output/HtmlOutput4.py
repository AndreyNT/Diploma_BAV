from Model.Constant import Constant
from collections import defaultdict


class HtmlOutput:
    @staticmethod
    def init():
        HtmlOutput.ROOM_COLUMN_NUMBER = Constant.DAYS_NUM + 1
        HtmlOutput.ROOM_ROW_NUMBER = Constant.DAY_HOURS + 1
        HtmlOutput.COLOR1 = "#319378"
        HtmlOutput.COLOR2 = "#CE0000"
        HtmlOutput.CRITERIAS = ("R", "S", "L", "P", "G", "T")
        HtmlOutput.CRITERIAS_DESCR = (
            "Current room has {any}overlapping",
            "Current room has {any}enough seats",
            "Current room with {any}enough computers if they are required",
            "Professors have {any}overlapping classes",
            "Student groups has {any}overlapping classes",
            "Time Professor has {any}overlapping classes",
        )
        HtmlOutput.PERIODS = Constant.PERIODS
        HtmlOutput.WEEK_DAYS = Constant.WEEK_DAYS

    @staticmethod
    def getCourseClass(cc, RoomName, criterias, ci):
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
            RoomName,
            "<br />",
            "/".join(map(lambda grp: grp.Name, cc.Groups)),
            "<br />",
        ]
        if cc.LabRequired:
            sb.append("Lab<br />")

        for i in range(length_CRITERIAS):
            sb.append("<span style='color:")
            if criterias[ci + i]:
                sb.append(COLOR1)
                sb.append("' title='")
                sb.append(
                    CRITERIAS_DESCR[i].format(any="" if (i == 1 or i == 2) else "no ")
                )
            else:
                sb.append(COLOR2)
                sb.append("' title='")
                sb.append(
                    CRITERIAS_DESCR[i].format(any="not " if (i == 1 or i == 2) else "")
                )
            sb.append("'> ")
            sb.append(CRITERIAS[i])
            sb.append(" </span>")

        return sb

    @staticmethod
    def generateTimeTable(solution, slot_table):
        ci = 0

        time_table = defaultdict(list)
        items = solution.classes.items
        ROOM_COLUMN_NUMBER = HtmlOutput.ROOM_COLUMN_NUMBER
        getCourseClass = HtmlOutput.getCourseClass

        for cc, reservation in items():
            dayId = reservation.Day + 1
            periodId = reservation.Time + 1
            roomId = reservation.Room
            dur = cc.Duration
            groups = "/".join(map(lambda grp: grp.Name, cc.Groups))

            indexId = dayId  # В данном случае индекс - это день недели

            key = (periodId, groups)
            if key not in slot_table:
                slot_table[key] = [0] * (ROOM_COLUMN_NUMBER + 1)

            year_duration = slot_table[key]
            year_duration[indexId] = dur

            for m in range(1, dur):
                next_key = (periodId + m, groups)
                if next_key not in slot_table:
                    slot_table[next_key] = [0] * (ROOM_COLUMN_NUMBER + 1)
                if slot_table[next_key][indexId] < 1:
                    slot_table[next_key][indexId] = -1

            if key not in time_table:
                year_schedule = [None] * (ROOM_COLUMN_NUMBER + 1)
                time_table[key] = year_schedule

            year_schedule = time_table[key]
            year_schedule[indexId] = "".join(
                getCourseClass(
                    cc,
                    solution._configuration.getRoomById(roomId).Name,
                    solution.criteria,
                    ci,
                )
            )

            ci += 6

        return time_table

    @staticmethod
    def getHtmlCell(content, rowspan):
        if rowspan == 0:
            return "<td></td>"

        if content is None:
            return "<td></td>"

        sb = []
        if rowspan > 1:
            sb.append("<td style='border: .1em solid black; padding: .25em' rowspan='")
            sb.append(str(rowspan))
            sb.append("'>")
        else:
            sb.append("<td style='border: .1em solid black; padding: .25em'>")

        sb.append(content)
        sb.append("</td>")
        return "".join(sb)

    @staticmethod
    def getResult(solution):
        HtmlOutput.init()
        slot_table = defaultdict(list)
        time_table = HtmlOutput.generateTimeTable(solution, slot_table)
        if not slot_table or not time_table:
            return ""

        sb = []
        for group, schedule in time_table.items():
            group_name = group[1]
            sb.append("<div id='group_")
            sb.append(group_name)
            sb.append("' style='padding: 0.5em'>\n")
            sb.append("<table style='border-collapse: collapse; width: 95%'>\n")
            sb.append(HtmlOutput.getTableHeader(group_name))
            for periodId in range(HtmlOutput.ROOM_ROW_NUMBER):
                if periodId == 0:
                    continue  # Первый период не нужен для заголовка

                key = (periodId, group_name)
                if key not in slot_table or key not in time_table:
                    continue

                year_duration = slot_table[key]
                year_schedule = time_table[key]
                sb.append("<tr>")

                for indexId in range(HtmlOutput.ROOM_COLUMN_NUMBER + 1):
                    if indexId == 0:
                        sb.append("<th style='border: .1em solid black; padding: .25em' scope='row'>")
                        sb.append(HtmlOutput.PERIODS[periodId])
                        sb.append("</th>\n")
                        continue

                    content = year_schedule[indexId] if year_schedule else None
                    sb.append(HtmlOutput.getHtmlCell(content, year_duration[indexId]))

                sb.append("</tr>\n")
            sb.append("</table>\n</div>\n")

        return "".join(sb)

    @staticmethod
    def getTableHeader(group_name):
        sb = [
            "<tr><th style='border: .1em solid black' scope='col' rowspan='2'>Group: ",
            group_name,
            "</th>\n",
        ]
        for weekDay in HtmlOutput.WEEK_DAYS:
            sb.append("<th style='border: .1em solid black; padding: .25em; width: 15%'>")
            sb.append(weekDay)
            sb.append("</th>\n")
        sb.append("</tr>\n")
        return "".join(sb)
