import datetime
from typing import Protocol


class SourceFile():
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

    def __repr__(self):
        return "buy_book.SourceFile(created_date: " +\
               repr(self.created_date) +\
               ", books: " +\
               str(len(self.books)) +\
               ")"

    def __eq__(self, other):
        if not isinstance(other, SourceFile):
            return NotImplemented
        return (self.created_date == other.created_date
                and self.books == other.books)

    def __hash__(self):
        return hash((self.created_date, self.books))


class Book():
    repair_times: int = -1
    enchantments: list = []

    def __init__(self, _dict: dict):
        super().__init__()
        self.repair_times = _dict.get('repair_times', -1)
        if('enchantments' in _dict):
            for _encha in _dict['enchantments']:
                self.enchantments.append(Enchantment(_encha))

    def __repr__(self):
        return "buy_book.Book(repair_times: " +\
               str(self.repair_times) +\
               ", enchantments: " +\
               str(len(self.enchantments)) +\
               ")"

    def __eq__(self, other):
        if not isinstance(other, Book):
            return NotImplemented
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

    def __repr__(self):
        return "buy_book.Enchantment(namespaced_id: " +\
               self.namespaced_id +\
               ", level: " +\
               str(self.level) +\
               ")"

    def __eq__(self, other):
        if not isinstance(other, Enchantment):
            return NotImplemented
        return (self.namespaced_id == other.namespaced_id
                and self.level == other.level)

    def __hash__(self):
        return hash((self.namespaced_id, self.level))
