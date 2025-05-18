# Хранит данные о курсе
class Course:
    # Инициализирует курс
    def __init__(self, id, name, year, specialization):
        # Возвращает идентификатор курса
        self.Id = id
        # Возвращает название курса
        self.Name = name
        # Возвращает год курса
        self.Year = year
        # Возвращает специализацию курса
        self.Specialization = specialization
