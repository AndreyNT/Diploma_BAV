from Model.Constant import Constant


class CourseClass:
    # Счетчик ID для автоматического назначения идентификаторов
    _next_class_id = 0

    # Инициализирует объект занятия
    def __init__(self, professors, course, requires_lab, duration, groups, section):
        self.Id = CourseClass._next_class_id
        CourseClass._next_class_id += 1
        # Возвращает указатель на профессоров, которые преподают
        self.Professors = professors
        # Возвращает указатель на словарь пересечения времён профессоров
        self.availableTime = self.Intersection(professors)
        # Возвращает указатель на курс, к которому относится занятие
        self.Course = course
        # Возвращает количество мест (студентов), необходимое в аудитории
        self.NumberOfSeats = 0
        # Возвращает секцию занятия
        self.Section = section
        # Возвращает TRUE, если для занятия требуется компьютер в аудитории
        self.LabRequired = requires_lab
        # Возвращает длительность занятия в часах
        self.Duration = duration
        # Возвращает ссылку на список студенческих групп, посещающих занятие
        self.Groups = groups

        # Привязывает профессоров к занятию
        for professor in self.Professors:
            professor.addCourseClass(self)

        # Привязывает студенческие группы к занятию
        for grp in self.Groups:
            grp.addClass(self)
            self.NumberOfSeats += grp.NumberOfStudents

    # Возвращает TRUE, если у другого занятия есть одна или пересекающиеся студенческие группы
    def groupsOverlap(self, c):
        return any(True for grp in self.Groups if grp in c.Groups)

    # Возвращает TRUE, если у другого занятия есть тот же профессор
    def professorOverlaps(self, c):
        return any(True for prof in self.Professors if prof in c.Professors)

    def Intersection(self, profs):
        intersection = {}

        if len(profs) == 1:
            return profs[0].availableTime

        for day in profs[0].availableTime:
            b = True
            times = []  # список списков из двух элементов (начало, конец) или []
            for d in profs:
                if not day in d.availableTime:
                    b = False
                    break
                times.append(d.availableTime[day])
            if b:
                x = self.timeInter(times)
                if x[1] != False:
                    intersection[day] = x[0]

        return intersection

    def timeInter(self, times):  # times = [["чч:мм", "чч:мм"], [], ...]
        starttime = Constant.TEMP_LIST_HOURS[0]
        endtime = Constant.TEMP_LIST_HOURS[-1]

        for time in times:
            if len(time) == 0:
                continue
            if time[0] > starttime:
                starttime = time[0]
            if time[1] < endtime:
                if time[1] <= starttime:
                    return [], False

                endtime = time[1]

        return (
            ([starttime, endtime], True)
            if starttime != Constant.TEMP_LIST_HOURS[0]
            or endtime != Constant.TEMP_LIST_HOURS[-1]
            else ([], True)
        )

    def randDayTime(self):
        from random import choice, randrange

        dur = self.Duration
        iterat = 0
        while True:

            day, t = choice(list(self.availableTime.items()))
            # Пример диапазона времени: 09:30 -> 13:00
            if len(t) == 0:
                x = (Constant.indexDay(day), randrange(0, Constant.DAY_HOURS - dur + 1))
                # if dur == 3 and x[1] == 6:
                #     print(
                #         f"randDay Time :\n\ttime from 0 -> {Constant.DAY_HOURS - dur + 1} time = {x[1]}"
                #     )
                #     input("press .....")
                return x
            else:  # 09:30 -> 13:00
                index_t1 = Constant.TEMP_LIST_HOURS.index(t[0])
                index_t2 = Constant.TEMP_LIST_HOURS.index(t[1])
                try:
                    x = (
                        Constant.indexDay(day),
                        randrange(index_t1, index_t2 - dur + 1),
                    )
                    # if dur == 3 and x[1] == 6:
                    #     print(
                    #         f"randDay Time :\n\ttime from {index_t1} -> {index_t2 - dur + 1} time = {x[1]}"
                    #     )
                    #     input("press .....")
                    return x
                except:
                    iterat += 1
                    if iterat == 10:
                        x = (
                            Constant.indexDay(day),
                            randrange(0, Constant.DAY_HOURS - dur + 1),
                        )
                        # if dur == 3 and x[1] == 6:
                        #     print(
                        #         f"randDay Time after while:\n\ttime from 0 -> {Constant.DAY_HOURS - dur + 1} time = {x[1]}"
                        #     )
                        #     input("press .....")
                        return x

    def __hash__(self):
        return hash(self.Id)

    def __eq__(self, other):
        return self.Id == other.Id

    def __ne__(self, other):
        # Не обязательно, но для избежания ситуации, когда одновременно x==y и x!=y
        return not (self == other)

    # Перезапускает назначение ID
    @staticmethod
    def restartIDs() -> None:
        CourseClass._next_class_id = 0