# Хранит данные об аудитории
class Room:
    # Счетчик ID для автоматического назначения идентификаторов
    _next_room_id = 0

    # Инициализирует данные аудитории и присваивает ID
    def __init__(self, name, lab, number_of_seats):
        # Возвращает идентификатор аудитории, назначаемый автоматически
        self.Id = Room._next_room_id
        Room._next_room_id += 1
        # Возвращает название аудитории
        self.Name = name
        # Возвращает TRUE, если в аудитории есть компьютеры, иначе FALSE
        self.Lab = lab
        # Возвращает количество мест в аудитории
        self.NumberOfSeats = number_of_seats

    # Перезапускает назначение ID
    @staticmethod
    def restartIDs() -> None:
        Room._next_room_id = 0
