class Constant:
    DAYS_NUM = 0
    WEEK_DAYS = ()
    DAY_HOURS = 0
    FIRST_HOUR = 0
    # каждый час в формате hh:mm с начала  до конца рабочего дня
    # для определения индекса периода в зависимости от времени преподавателя
    TEMP_LIST_HOURS = ()
    YEAR_NUM = 0
    SPECIALIZATIONs = ()
    SPECIALIZATION_NUM = 0
    SECTION_NUM = {}

    @staticmethod
    def init(dictConfig):
        from datetime import time

        for key in dictConfig:
            if key == "weekdays":
                Constant.WEEK_DAYS = tuple(dictConfig[key])
                Constant.DAYS_NUM = len(Constant.WEEK_DAYS)
            elif key == "dayHours":
                Constant.DAY_HOURS = dictConfig[key]
            elif key == "startHour":
                Constant.FIRST_HOUR = dictConfig[key]
            elif key == "yearNum":
                Constant.YEAR_NUM = dictConfig[key]
            elif key == "specializations":
                Constant.SPECIALIZATIONS = tuple(dictConfig[key])
                Constant.SPECIALIZATION_NUM = len(dictConfig[key])
            elif key == "sectionNum":
                Constant.SECTION_NUM = dictConfig[key]

        Constant.TEMP_LIST_HOURS, Constant.PERIODS = Constant.generateHOURS_Periods()

    @staticmethod
    def generateHOURS_Periods():
        from datetime import time

        t = time.fromisoformat(Constant.FIRST_HOUR)
        temp = []
        for i in range(Constant.DAY_HOURS + 1):
            temp.append(str(time(t.hour + i, t.minute))[:5])

        PERIODS = [""]
        for i in range(Constant.DAY_HOURS):
            PERIODS.append(temp[i] + " - " + temp[i + 1])

        return tuple(temp), tuple(PERIODS)

    @staticmethod
    # Возвращает индекс дня в списке WEEK_DAYS
    def indexDay(day):
        return Constant.WEEK_DAYS.index(day)
