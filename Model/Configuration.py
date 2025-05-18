import codecs
import json
from Model.Constant import Constant
from Model.Professor import Professor
from Model.StudentsGroup import StudentsGroup
from Model.Course import Course
from Model.Room import Room
from Model.CourseClass import CourseClass


# Читает файл конфигурации и хранит разобранные объекты
class Configuration:

    # Инициализирует данные
    def __init__(self):
        # Указывает, что конфигурация ещё не разобрана
        self._isEmpty = True
        # Разобранные преподавателя
        self._professors = {}
        # Разобранные группы студентов
        self._studentGroups = {}
        # Разобранные курсы
        self._courses = {}
        # Разобранные аудитории
        self._rooms = {}
        # Разобранные занятия
        self._courseClasses = []

    # Возвращает преподавателя по указанному ID
    # Если преподвателя с таким ID нет, возвращает NULL
    def getProfessorById(self, id) -> Professor:
        if id in self._professors:
            return self._professors[id]
        return None

    @property
    # Возвращает количество разобранных преподавателей
    def numberOfProfessors(self) -> int:
        return len(self._professors)

    # Возвращает группу студентов по указанному ID
    # Если группы с таким ID нет, возвращает NULL
    def getStudentsGroupById(self, id) -> StudentsGroup:
        if id in self._studentGroups:
            return self._studentGroups[id]
        return None

    @property
    # Возвращает количество разобранных групп студентов
    def numberOfStudentGroups(self) -> int:
        return len(self._studentGroups)

    # Возвращает курс по указанному ID
    # Если курса с таким ID нет, возвращает NULL
    def getCourseById(self, id) -> Course:
        if id in self._courses:
            return self._courses[id]
        return None

    @property
    def numberOfCourses(self) -> int:
        return len(self._courses)

    # Возвращает аудиторию по указанному ID
    # Если аудитории с таким ID нет, возвращает NULL
    def getRoomById(self, id) -> Room:
        if id in self._rooms:
            return self._rooms[id]
        return None

    @property
    # Возвращает количество разобранных аудиторий
    def numberOfRooms(self) -> int:
        return len(self._rooms)

    @property
    # Возвращает ссылку на список разобранных занятий
    def courseClasses(self) -> list:
        return self._courseClasses

    @property
    # Возвращает количество разобранных занятий
    def numberOfCourseClasses(self) -> int:
        return len(self._courseClasses)

    @property
    # Возвращает TRUE, если конфигурация ещё не разобрана
    def isEmpty(self) -> bool:
        return self._isEmpty

    # Считывает данные профессора из файла конфигурации, создает объект и возвращает
    # Возвращает NULL, если не удалось разобрать данные
    @staticmethod
    def __parseProfessor(dictConfig):
        id = 0
        name = ''
        isProf = False
        availableTime = {}

        for key in dictConfig:
            if key == 'id':
                id = dictConfig[key]
            elif key == 'name':
                name = dictConfig[key]
            elif key == 'isProf':
                isProf = dictConfig[key]
            elif key == 'availableTime':
                availableTime = dictConfig[key]

        if id == 0 or name == '':
            return None
        return Professor(id, name, availableTime, isProf)

    # Считывает данные группы студентов из файла конфигурации, создает объект и возвращает
    # Возвращает None, если не удалось разобрать данные
    @staticmethod
    def __parseStudentsGroup(dictConfig):
        id = 0
        name = ''
        size = 0

        for key in dictConfig:
            if key == 'id':
                id = dictConfig[key]
            elif key == 'name':
                name = dictConfig[key]
            elif key == 'size':
                size = dictConfig[key]

        if id == 0:
            return None
        return StudentsGroup(id, name, size)

    # Считывает данные курса из файла конфигурации, создает объект и возвращает
    # Возвращает None, если не удалось разобрать данные
    @staticmethod
    def __parseCourse(dictConfig):
        id = 0
        name = ''
        year = 0
        specialization = ''

        for key in dictConfig:
            if key == 'id':
                id = dictConfig[key]
            elif key == 'name':
                name = dictConfig[key]
            elif key == 'year':
                year = dictConfig[key]
            elif key == 'specialization':
                specialization = dictConfig[key]

        if id == 0:
            return None
        return Course(id, name, year,specialization)

    # Считывает данные аудитории из файла конфигурации, создает объект и возвращает
    # Возвращает None, если не удалось разобрать данные
    @staticmethod
    def __parseRoom(dictConfig):
        lab = False
        name = ''
        size = 0

        for key in dictConfig:
            if key == 'lab':
                lab = dictConfig[key]
            elif key == 'name':
                name = dictConfig[key]
            elif key == 'size':
                size = dictConfig[key]

        if size == 0 or name == '':
            return None
        return Room(name, lab, size)

    # Считывает данные занятия из файла конфигурации, создает объект и возвращает ссылку
    # Возвращает None, если не удалось разобрать данные
    def __parseCourseClass(self, dictConfig):
        cid = 0
        dur = 1
        lab = False
        section = 0
        group_list = []
        prof_list = []

        for key in dictConfig:
            if key == 'professors':
                professors = dictConfig[key]
                if isinstance(professors, list):
                    for prof in professors:
                        p = self.getProfessorById(prof)
                        if p:
                            prof_list.append(p)
                else:
                    p = self.getProfessorById(professors)
                    if p:
                        prof_list.append(p)
            elif key == 'course':
                cid = dictConfig[key]
            elif key == 'lab':
                lab = dictConfig[key]
            elif key == 'duration':
                dur = dictConfig[key]
            elif key == 'section':
                section = dictConfig[key]
            elif key == 'group' or key == 'groups':
                groups = dictConfig[key]
                if isinstance(groups, list):
                    for grp in groups:
                        g = self.getStudentsGroupById(grp)
                        if g:
                            group_list.append(g)
                else:
                    g = self.getStudentsGroupById(groups)
                    if g:
                        group_list.append(g)

        # Получает курс, к которому относится это занятие
        c = self.getCourseById(cid)

        # Проверяет, существует ли курс
        if not c:
            return None

        # Создает объект и возвращает
        return CourseClass(prof_list, c, lab, dur, group_list, section)

    # Разбирает файл и сохраняет объекты
    def parseFile(self, fileName):
        # Очистка ранее разобранных объектов
        self._professors = {}
        self._studentGroups = {}
        self._courses = {}
        self._rooms = {}
        self._courseClasses = []

        Room.restartIDs()
        CourseClass.restartIDs()

        with codecs.open(fileName, "r", "utf-8") as f:
            # Читает файл в строку и десериализует JSON
            data = json.load(f)

        for dictConfig in data:
            for key in dictConfig:
                if key == 'prof':
                    prof = self.__parseProfessor(dictConfig[key])
                    self._professors[prof.Id] = prof
                elif key == 'course':
                    course = self.__parseCourse(dictConfig[key])
                    self._courses[course.Id] = course
                elif key == 'room':
                    room = self.__parseRoom(dictConfig[key])
                    self._rooms[room.Id] = room
                elif key == 'group':
                    group = self.__parseStudentsGroup(dictConfig[key])
                    self._studentGroups[group.Id] = group
                elif key == 'class':
                    courseClass = self.__parseCourseClass(dictConfig[key])
                    self._courseClasses.append(courseClass)
                elif key == 'const':
                    Constant.init(dictConfig[key])

        self._isEmpty = False
