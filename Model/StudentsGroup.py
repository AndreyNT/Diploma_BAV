# Хранит данные о студенческой группе
class StudentsGroup:
    # Инициализирует данные студенческой группы
    def __init__(self, id, name, numberOfStudents):
        self.Id = id
        self.Name = name
        self.NumberOfStudents = numberOfStudents
        self.CourseClasses = []

    # Привязывает группу к занятию
    def addClass(self, course_class):
        self.CourseClasses.append(course_class)

    def __hash__(self):
        return hash(self.Id)

    # Сравнивает идентификаторы двух объектов, представляющих студенческие группы
    def __eq__(self, rhs):
        return self.Id == rhs.Id

    def __ne__(self, other):
        # Не обязательно, но чтобы избежать ситуации, когда одновременно x==y и x!=y
        return not self.__eq__(other)