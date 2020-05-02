import datetime


class SourceFile:
    created_date: datetime.datetime = None
    books: list = []

    def __init__(self, _dict: dict):
        super().__init__()
        self.created_date = datetime.datetime.strptime(
            _dict.get('created_date', '1970-01-01 00:00:00'),
            '%Y-%m-%d %H:%M:%S'
        )
        if('books' in _dict):
            for _book in _dict['books']:
                self.books.append(Book(_book))

    def __eq__(self, other):
        return (self.created_date == other.created_date
                and self.books == other.books)

    def __hash__(self):
        return hash((self.created_date, self.books))


class Book:
    repair_times: int = -1
    enchantments: list = []

    def __init__(self, _dict: dict):
        super().__init__()
        self.repair_times = _dict.get('repair_times', -1)
        if('enchantments' in _dict):
            for _encha in _dict['enchantments']:
                self.enchantments.append(Enchantment(_encha))

    def __eq__(self, other):
        return (self.repair_times == other.repair_times
                and self.enchantments == other.enchantments)

    def __hash__(self):
        return hash((self.repair_times, self.enchantments))


class Enchantment:
    namespaced_id: str = ""
    level: int = -1

    def __init__(self, _dict: dict):
        super().__init__()
        self.namespaced_id = _dict.get('enchantment', "")
        self.level = _dict.get('level', -1)

    def __eq__(self, other):
        return (self.namespaced_id == other.namespaced_id
                and self.level == other.level)

    def __hash__(self):
        return hash((self.namespaced_id, self.level))
