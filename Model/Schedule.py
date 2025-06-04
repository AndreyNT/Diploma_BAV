from Model.Constant import Constant
from Model.Reservation import Reservation
from collections import defaultdict
from random import randrange


# Хромосома расписания
class Schedule:
    # Инициализирует хромосомы с конфигурационным блоком (настройка хромосомы)
    def __init__(self, configuration):
        self._configuration = configuration
        # Значение приспособленности хромосомы
        self._fitness = 0

        # Временные слоты, одна запись представляет один час в одной аудитории
        slots_length = (
            Constant.DAYS_NUM * Constant.DAY_HOURS * self._configuration.numberOfRooms
        )
        self._slots = [[] for _ in range(slots_length)]

        # Таблица занятий для хромосомы
        # Используется для определения первого временного слота, занятого занятием
        self._classes = defaultdict(Reservation)

        # Флаги соблюдения требований занятия
        self._criteria = (self._configuration.numberOfCourseClasses * 6) * [False]

        self._diversity = 0.0
        self._rank = 0

    def copy(self, c, setup_only):
        if not setup_only:
            self._configuration = c.configuration
            # копирует временные слоты и таблицу занятий
            self._slots, self._classes = c.slots, c.classes

            # копирует флаги соблюдения требований
            self._criteria = c.criteria

            # копирует значение приспособленности
            self._fitness = c.fitness
            return self

        return Schedule(c.configuration)

    # Создаёт новую хромосому с тем же набором параметров, но случайно сгенерированным расписанием
    def makeNewFromPrototype(self):
        # Создаёт новую хромосому, копируя настройки текущей (без данных)
        new_chromosome = self.copy(self, True)
        # Получает доступ к слотам и таблице занятий новой хромосомы
        new_chromosome_slots, new_chromosome_classes = (
            new_chromosome._slots,
            new_chromosome._classes,
        )

        # Размещает занятия в случайных позициях
        # Получает список всех занятий из конфигурации
        classes = self._configuration.courseClasses
        # Количество аудиторий
        nr = self._configuration.numberOfRooms
        DAYS_NUM, DAY_HOURS = Constant.DAYS_NUM, Constant.DAY_HOURS

        # Для каждого занятия из конфигурации
        for c in classes:
            # Определяет случайное время и аудиторию для занятия
            dur = c.Duration  # Длительность занятия
            day, time = c.randDayTime()  # Случайный день и время

            # Случайно выбирает аудиторию
            room = randrange(32768) % nr
            # Создаёт объект бронирования
            reservation = Reservation(nr, day, time, room)
            # Получает индекс временного слота через хэш-функцию
            reservation_index = hash(reservation)

            # Заполняет временные слоты для каждого часа занятия
            for i in range(reservation_index, reservation_index + dur):
                new_chromosome_slots[i].append(c)  # Добавляет занятие в соответствующий слот

            # Добавляет занятие в таблицу занятий хромосомы
            new_chromosome_classes[c] = reservation  # Сохраняет связь занятия с бронированием

        # Вычисляет приспособленность нового расписания
        new_chromosome.calculateFitness("makeNewFromPrototype")
        return new_chromosome

    # Выполняет операцию кроссовера с использованием
    # двух хромосом и возвращает потомка
    def crossover(self, parent, numberOfCrossoverPoints, crossoverProbability):
        # Проверяет вероятность операции кроссовера
        if randrange(32768) % 100 > crossoverProbability:
            # Нет кроссовера, просто копирует первую родительскую хромосому
            return self.copy(self, False)

        # Создаёт новую хромосому, копируя настройки текущей (без данных)
        n = self.copy(self, True)
        n_classes, n_slots = n._classes, n._slots

        classes = self._classes
        # Количество занятий
        size = len(classes)

        cp = size * [False]

        # Определяет точки кроссовера (случайно)
        for i in range(numberOfCrossoverPoints, 0, -1):
            check_point = False
            while not check_point:
                p = randrange(32768) % size
                if not cp[p]:
                    cp[p] = check_point = True

        # Создаёт новую хромосому, объединяя данные родителей
        first = randrange(2) == 0

        for i in range(size):
            if first:
                course_class = self._configuration.courseClasses[i]
                dur = course_class.Duration
                reservation = classes[course_class]
                reservation_index = hash(reservation)
                # Вставляет занятие из первой
                # родительской хромосомы в таблицу потомка
                n_classes[course_class] = reservation
                # Все временные слоты занятия копируются

                try:
                    for j in range(reservation_index, reservation_index + dur):
                        n_slots[j].append(course_class)
                except:
                    print("length slot = ", len(n_slots))
                    print(
                        "reservation_index, reservation_index + dur ",
                        reservation_index,
                        reservation_index + dur,
                    )
                    exit()
            else:
                course_class = self._configuration.courseClasses[i]
                dur = course_class.Duration
                reservation = parent._classes[course_class]
                reservation_index = hash(reservation)
                # Вставляет занятие из второй
                # родительской хромосомы в таблицу потомка
                n_classes[course_class] = reservation

                # Все временные слоты занятия копируются
                try:
                    for j in range(reservation_index, reservation_index + dur):
                        n_slots[j].append(course_class)
                except:
                    print("length slot = ", len(n_slots))
                    print(
                        "reservation_index, reservation_index + dur ",
                        reservation_index,
                        reservation_index + dur,
                    )
                    exit()
            # Точка кроссовера
            if cp[i]:
                # Меняет источник хромосомы
                first = not first

        n.calculateFitness("crossover")

        # Возвращает указатель на потомка
        return n

    # Выполняет мутацию хромосомы
    def mutation(self, mutationSize, mutationProbability):
        # Проверяет вероятность операции мутации
        if randrange(32768) % 100 > mutationProbability:
            return

        classes = self._classes
        # Общее количество занятий
        numberOfClasses = len(classes)
        course_classes = tuple(classes.keys())
        configuration = self._configuration
        slots = self._slots
        nr = configuration.numberOfRooms

        DAY_HOURS = Constant.DAY_HOURS
        DAYS_NUM = Constant.DAYS_NUM
        # Перемещает указанное количество занятий в случайные позиции
        for i in range(mutationSize, 0, -1):
            # Выбирает случайное занятие для перемещения
            mpos = randrange(32768) % numberOfClasses

            # Текущий временной слот, занятый занятием
            cc1 = course_classes[mpos]
            reservation1 = classes[cc1]
            reservation1_index = hash(reservation1)

            # Определяет новую случайную позицию для занятия
            dur = cc1.Duration
            day, time = cc1.randDayTime()

            room = randrange(32768) % nr
            reservation2 = Reservation(nr, day, time, room)
            reservation2_index = hash(reservation2)

            # Перемещает все временные слоты занятия
            for j in range(dur):
                # Удаляет занятие из текущего временного слота
                cl = slots[reservation1_index + j]
                clTuple = tuple(cl)
                for cc in clTuple:
                    cl.remove(cc)

                # Перемещает занятие в новый временной слот
                slots[reservation2_index + j].append(cc1)

            # Обновляет запись в таблице занятий, указывающую на новые временные слоты
            classes[cc1] = reservation2
        self.calculateFitness("mutation")

    # Вычисляет значение приспособленности хромосомы
    def calculateFitness(self, Form):
        # Общий балл хромосомы
        sumScore = 0
        score = 0
        softScore = 0

        criteria, configuration = self._criteria, self._configuration
        items, slots = self._classes.items(), self._slots
        numberOfRooms = configuration.numberOfRooms
        DAY_HOURS, DAYS_NUM = Constant.DAY_HOURS, Constant.DAYS_NUM
        daySize = DAY_HOURS * numberOfRooms

        #######################################################
        # Словари для подсчёта количества занятий в день
        group_day_count = defaultdict(int)
        professor_day_count = defaultdict(int)

        for cc, reservation in items:
            day = reservation.Day
            for group in cc.Groups:
                group_day_count[(group.Id, day)] += 1
            for prof in cc.Professors:
                professor_day_count[(prof.Id, day)] += 1

        for key, count in group_day_count.items():
            if count > 4:
                self._fitness = 0
                return


        for key, count in professor_day_count.items():
            if count > 4:
                self._fitness = 0
                return
        #######################################################

        ci = 0
        getRoomById = configuration.getRoomById

        # Проверяет критерии и рассчитывает оценки для каждого занятия в расписании
        for cc, reservation in items:
            score = 0
            softScore = 0
            # Координаты временного слота
            day, time, room = reservation.Day, reservation.Time, reservation.Room
            dur = cc.Duration

            # Проверяет пересечение занятий в аудитории
            reservation_index = hash(reservation)
            cls = slots[reservation_index: reservation_index + dur]
            ro = any(True for slot in cls if len(slot) > 1)

            # При пересечении занятий в аудитории
            score = score if ro else score + 1
            criteria[ci + 0] = not ro

            r = getRoomById(room)
            # Проверяет, достаточно ли мест в аудитории
            criteria[ci + 1] = r.NumberOfSeats >= cc.NumberOfSeats
            score = score + 1 if criteria[ci + 1] else score

            # Проверяет наличие компьютеров в аудитории
            criteria[ci + 2] = ((not cc.LabRequired) or r.Lab) and (
                    cc.LabRequired or not (r.Lab)
            )
            score = score + 1 if criteria[ci + 2] else score
            po = go = False

            # Проверяет пересечение занятий для преподавателей и студенческих групп
            t = day * daySize + time
            professorOverlaps, groupsOverlap = cc.professorOverlaps, cc.groupsOverlap
            try:
                for k in range(numberOfRooms, 0, -1):
                    # Для каждого часа занятия
                    for i in range(t, t + dur):
                        cl = slots[i]
                        for cc1 in cl:
                            if cc != cc1:
                                # Пересечение преподавателей?
                                if not po and professorOverlaps(cc1):
                                    po = True
                                # Пересечение студенческих групп?
                                if not go and groupsOverlap(cc1):
                                    go = True
                                # Оба типа пересечения? Достаточно проверить
                                if po and go:
                                    raise Exception("нет необходимости проверять дальше")
                    t += DAY_HOURS
            except Exception:
                pass

            # Преподаватели не имеют пересекающихся занятий?
            score = score if po else score + 1
            criteria[ci + 3] = not po

            # Студенческие группы не имеют пересекающихся занятий?
            score = score if go else score + 1
            criteria[ci + 4] = not go

            # Доступен ли преподаватель в выбранное время?

            # Альфа для мягких правил
            alpha = [
                1.0,  # альфа для занятий в удобное время преподавателя
                0.5,  # альфа для отмены пауз между занятиями
                0.8,  # альфа для более раннего расписания занятий
                1.7,  # альфа для сведения занятий преподавателя к минимуму дней
            ]

            profScore = 0
            to = False
            lenProfTheoretical = 0
            for prof in cc.Professors:
                if prof.isProf:
                    lenProfTheoretical += 1
                    if prof.inAvailable(
                            Constant.WEEK_DAYS[day],
                            Constant.TEMP_LIST_HOURS[time],
                            Constant.TEMP_LIST_HOURS[time + dur],
                    ):
                        profScore += 1
                    else:
                        to = True
                else:
                    try:
                        if prof.inAvailable(
                                Constant.WEEK_DAYS[day],
                                Constant.TEMP_LIST_HOURS[time],
                                Constant.TEMP_LIST_HOURS[time + dur],
                        ):
                            softScore += alpha[0]
                    except:
                        from time import sleep

                        sleep(1)
                        print(
                            "второй ID курса = ",
                            cc.Id,
                            "день = ",
                            day,
                            "время курса = ",
                            time,
                            ", длительность = ",
                            cc.Duration,
                            " ,длина PERIODS = ",
                            len(Constant.PERIODS),
                        )
                        for index, period in enumerate(Constant.TEMP_LIST_HOURS):
                            print(f"TEMP_LIST_HOURS {period} его индекс {index}")
                        print("доступное время для курса: ", cc.availableTime)
                        print("доступное время для преподавателя: ", prof.availableTime)
                        exit()

            if cc.LabRequired:
                score += 1
            else:
                if lenProfTheoretical > 0:
                    profScore /= lenProfTheoretical
                    score += profScore

            criteria[ci + 5] = not to

            # Второе мягкое правило
            try:
                if reservation_index % DAY_HOURS == 0:
                    softScore += alpha[1]
                else:
                    if len(slots[reservation_index - 1]) != 0:
                        softScore += alpha[1]
            except:
                pass

            # Третье мягкое правило
            try:
                if reservation_index % DAY_HOURS == 0:
                    softScore += alpha[2]
                    raise

                totalSlot = 0  # количество слотов с начала дня до времени занятия
                nonEmptySLot = 0  # количество непустых слотов с начала дня до времени занятия

                for index in range(
                        day * numberOfRooms * DAY_HOURS + room * DAY_HOURS,
                        reservation_index,
                ):
                    totalSlot += 1
                    if len(slots[index]) != 0:
                        nonEmptySLot += 1
                softScore += alpha[2] * nonEmptySLot / totalSlot
            except:
                pass

            # Четвертое мягкое правило
            minFewerDayScore = 10
            for prof in cc.Professors:
                lenProfCourse = len(prof.CourseClasses)
                sumDistance = 0
                for profCourse in prof.CourseClasses:
                    profReservation = self._classes[profCourse]
                    if cc == profCourse:
                        sumDistance += 1
                    elif day != profReservation.Day:
                        sumDistance += 0
                    else:
                        sumDistance += (
                                1 - (abs(time - profReservation.Time) - 1) / DAY_HOURS
                        )
                minFewerDayScore = min(minFewerDayScore, sumDistance / lenProfCourse)

            softScore += alpha[3] * minFewerDayScore

            softScore /= 4.1 * configuration.numberOfCourseClasses
            score += softScore

            sumScore += score
            ci += 6

        ###################################################################################
        # Дополнительные мягкие ограничения для студентов: отсутствие окон
        alpha_gap = 1.0
        for group in configuration._studentGroups.values():
            for day_idx in range(DAYS_NUM):
                # Собираем все занятия группы в этот день
                times = []
                for cc in group.CourseClasses:
                    reservation = self._classes.get(cc)
                    if reservation and reservation.Day == day_idx:
                        times.append((reservation.Time, cc.Duration))
                if times:
                    # Проверяем утреннюю паузу
                    min_time = min(t[0] for t in times)
                    if min_time > 0:
                        sumScore -= alpha_gap
                    # Проверяем промежуточные паузы между занятиями
                    times_sorted = sorted(times, key=lambda x: x[0])
                    for i in range(len(times_sorted) - 1):
                        current_end = times_sorted[i][0] +  times_sorted[i][1]
                        next_start = times_sorted[i + 1][0]
                        if next_start > current_end:
                            sumScore -= alpha_gap
        ###################################################################################

         # Рассчитывает значение приспособленности на основе баллов
        if configuration.numberOfCourseClasses > 0:
            self._fitness = sumScore / (configuration.numberOfCourseClasses * 7)
        else:
            self._fitness = 0


    # Вычисляет значение приспособленности хромосомы (версия 2)
    def calculateFitness2(self, From):
        # Общий балл хромосомы
        sumScore = 0
        score = 0
        softScore = 0

        criteria, configuration = self._criteria, self._configuration
        items, slots = self._classes.items(), self._slots
        numberOfRooms = configuration.numberOfRooms
        DAY_HOURS, DAYS_NUM = Constant.DAY_HOURS, Constant.DAYS_NUM
        daySize = DAY_HOURS * numberOfRooms

        ci = 0
        getRoomById = configuration.getRoomById

        # Проверяет критерии и рассчитывает оценки для каждого занятия в расписании
        for cc, reservation in items:
            score = 0
            softScore = 0.7

            # Координаты временного слота
            day, time, room = reservation.Day, reservation.Time, reservation.Room
            dur = cc.Duration

            """if dur == 3 and time == 6:
                print(
                    "fittness first ",
                    "From ",
                    From,
                    "id course = ",
                    cc.Id,
                    "day = ",
                    day,
                    "time of course = ",
                    reservation.Time,
                    ", duration = ",
                    cc.Duration,
                    " ,length of PERIODS = ",
                    len(Constant.PERIODS),
                )"""

            # Проверяет пересечение занятий в аудитории
            reservation_index = hash(reservation)
            cls = slots[reservation_index: reservation_index + dur]
            ro = any(True for slot in cls if len(slot) > 1)

            # При пересечении занятий в аудитории
            score = score if ro else score + 1
            criteria[ci + 0] = not ro

            r = getRoomById(room)
            # Проверяет, достаточно ли мест в аудитории
            criteria[ci + 1] = r.NumberOfSeats >= cc.NumberOfSeats
            score = score + 1 if criteria[ci + 1] else score

            # Проверяет наличие компьютеров в аудитории при необходимости
            criteria[ci + 2] = (not cc.LabRequired) or (cc.LabRequired and r.Lab)
            score = score + 1 if criteria[ci + 2] else score
            po = go = False

            # Проверяет пересечение занятий для преподавателей и студенческих групп
            t = day * daySize + time
            professorOverlaps, groupsOverlap = cc.professorOverlaps, cc.groupsOverlap
            try:
                for k in range(numberOfRooms, 0, -1):
                    # Для каждого часа занятия
                    for i in range(t, t + dur):
                        cl = slots[i]
                        for cc1 in cl:
                            if cc != cc1:
                                # Пересечение преподавателей?
                                if not po and professorOverlaps(cc1):
                                    po = True
                                # Пересечение студенческих групп?
                                if not go and groupsOverlap(cc1):
                                    go = True
                                # Оба типа пересечения? Достаточно проверить
                                if po and go:
                                    raise Exception("нет необходимости проверять дальше")
                    t += DAY_HOURS
            except Exception:
                pass

            # Преподаватели не имеют пересекающихся занятий?
            score = score if po else score + 1
            criteria[ci + 3] = not po

            # Студенческие группы не имеют пересекающихся занятий?
            score = score if go else score + 1
            criteria[ci + 4] = not go

            # Доступен ли преподаватель в выбранное время?
            profScore = 0
            to = False
            lenProfTheoretical = 0
            for prof in cc.Professors:
                if prof.isProf:
                    lenProfTheoretical += 1
                    if prof.inAvailable(
                            Constant.WEEK_DAYS[day],
                            Constant.TEMP_LIST_HOURS[time],
                            Constant.TEMP_LIST_HOURS[time + dur],
                    ):
                        profScore += 1
                    else:
                        to = True
                else:
                    try:
                        if prof.inAvailable(
                                Constant.WEEK_DAYS[day],
                                Constant.TEMP_LIST_HOURS[time],
                                Constant.TEMP_LIST_HOURS[time + dur],
                        ):
                            softScore += 1.3
                    except:
                        from time import sleep
                        sleep(1)
                        print(
                            "второй ID курса = ",
                            cc.Id,
                            "день = ",
                            day,
                            "время курса = ",
                            time,
                            ", длительность = ",
                            cc.Duration,
                            " ,длина PERIODS = ",
                            len(Constant.PERIODS),
                        )
                        for index, period in enumerate(Constant.TEMP_LIST_HOURS):
                            print(f"TEMP_LIST_HOURS {period} его индекс {index}")
                        print("доступное время для курса: ", cc.availableTime)
                        print("доступное время для преподавателя: ", prof.availableTime)
                        exit()

            if cc.LabRequired:
                score += 1
            else:
                if lenProfTheoretical > 0:
                    profScore /= lenProfTheoretical
                    score += profScore

            criteria[ci + 5] = not to

            # Масштабирует мягкий балл
            softScore /= 2.1 * configuration.numberOfCourseClasses
            score += softScore

            sumScore += score
            ci += 6

        # Рассчитывает значение приспособленности на основе баллов
        if configuration.numberOfCourseClasses > 0:
            self._fitness = sumScore / (configuration.numberOfCourseClasses * 7)
        else:
            self._fitness = 0

    # Возвращает значение приспособленности хромосомы
    @property
    def fitness(self):
        return self._fitness

    @property
    # Возвращает конфигурационный блок, использованный для создания хромосомы
    def configuration(self):
        return self._configuration

    @property
    # Возвращает ссылку на таблицу занятий
    def classes(self):
        return self._classes

    @property
    # Возвращает массив флагов удовлетворения требований занятий
    def criteria(self):
        return self._criteria

    @property
    # Возвращает ссылку на массив временных слотов
    def slots(self):
        return self._slots

    @property
    def diversity(self):
        return self._diversity

    @diversity.setter
    def diversity(self, new_diversity):
        self._diversity = new_diversity

    @property
    def rank(self):
        return self._rank

    @rank.setter
    def rank(self, new_rank):
        self._rank = new_rank

    # Генерирует хэш-код для хромосомы на основе её таблицы занятий
    def __hash__(self) -> int:
        prime = 31
        result = 1
        classes = self._classes
        for cc in classes.keys():
            reservation = classes[cc]
            result = prime * result + (0 if reservation is None else hash(reservation))
        return result

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        classes, otherClasses = self._classes, other.classes
        for cc in classes.keys():
            if classes[cc] != otherClasses[cc]:
                return False

    def __ne__(self, other):
        return not self.__eq__(other)
