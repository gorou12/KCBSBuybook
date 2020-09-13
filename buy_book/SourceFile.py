import json
import datetime
import itertools

REPAIR_TIMES_MULTIPLIER: float = 0.8
BUY_PRICE_MULTIPLIER: float = 0.5


class SourceFile():
    created_date: datetime.datetime = None
    books: list = []
    price_meta: dict = {}
    total_sold_price: int = 0
    total_buy_price: int = 0

    def __init__(self, _dict: dict):
        super().__init__()
        self.books = []
        self.created_date = datetime.datetime.strptime(
            _dict.get('created_date', '1970-01-01 00:00:00'),
            '%Y-%m-%d %H:%M:%S'
        )
        if('books' in _dict):
            for _book in _dict['books']:
                if _book["item_type"] == "enchanted_book":
                    self.books.append(Book(_book))
                elif _book["item_type"] == "eco_egg":
                    self.books.append(EcoEgg(_book))

    def __repr__(self):
        return "buy_book.SourceFile(created_date: " +\
               repr(self.created_date) +\
               ", books: " +\
               str(len(self.books)) +\
               ")"

    def __eq__(self, other):
        if not isinstance(other, SourceFile):
            return NotImplemented
        return (self.created_date == other.created_date and
                self.books == other.books)

    def __hash__(self):
        return hash((self.created_date, self.books))

    def set_prices(self, prices: dict):
        self.books = [i.set_prices(prices['prices']) for i in self.books]
        self.price_meta = prices['metadata']
        return self

    def get_total_sold_price(self) -> int:
        if self.total_sold_price == 0:
            self.total_sold_price = sum(
                [i.get_sold_price() for i in self.books])
        return self.total_sold_price

    def get_total_buy_price(self) -> int:
        if self.total_buy_price == 0:
            self.total_buy_price = sum([i.get_buy_price() for i in self.books])
        return self.total_buy_price

    def get_dict(self) -> dict:
        self.get_total_sold_price()
        self.get_total_buy_price()
        return self.to_dict()

    def to_dict(self) -> dict:
        return {
            "created_date": self.created_date,
            "books": [b.to_dict() for b in self.books],
            "price_meta": self.price_meta,
            "total_sold_price": self.total_sold_price,
            "total_buy_price": self.total_buy_price
        }


class EcoEgg():
    item_type = "eco_egg"
    total_price: int = 0
    unit_price: int = 0
    japanese: str = ""
    count: int = 0

    def __init__(self, _dict: dict):
        super().__init__()
        self.count = _dict.get('count', -1)

    def __repr__(self):
        return "buy_book.EcoEgg(count: " +\
               str(self.count) +\
               ")"

    def __eq__(self, other):
        if not isinstance(other, EcoEgg):
            return NotImplemented
        return (self.count == other.count)

    def __hash__(self):
        return hash((self.count))

    def set_prices(self, price_list: list):
        for item in price_list:
            if "eco_egg" != item['id']:
                continue
            self.unit_price = item['price'][0]
            self.japanese = item.get('japanese', "")
        return self

    def get_total_price(self) -> int:
        if self.total_price != 0:
            return self.total_price
        self.total_price = self.unit_price * self.count
        return self.total_price

    def get_sold_price(self) -> int:
        if self.total_price == 0:
            self.get_total_price()
        multiply: float = 1
        return int(self.total_price * multiply)

    def get_buy_price(self) -> int:
        if self.total_price == 0:
            self.get_total_price()
        multiply: float = 1
        return int(self.total_price * multiply * BUY_PRICE_MULTIPLIER)

    def to_dict(self) -> dict:
        return {
            "item_type": self.item_type,
            "total_price": self.total_price,
            "unit_price": self.unit_price,
            "japanese": self.japanese,
            "count": self.count
        }


class Book():
    item_type = "enchanted_book"
    repair_times: int = -1
    enchantments: list = []
    total_price: int = 0

    def __init__(self, _dict: dict):
        super().__init__()
        self.enchantments = []
        self.repair_times = _dict.get('repair_times', -1)
        if('enchantments' in _dict):
            for _encha in _dict['enchantments']:
                e = Enchantment(_encha)
                self.enchantments.append(e)

    def __repr__(self):
        return "buy_book.Book(repair_times: " +\
               str(self.repair_times) +\
               ", enchantments: " +\
               str(len(self.enchantments)) +\
               ")"

    def __eq__(self, other):
        if not isinstance(other, Book):
            return NotImplemented
        return (self.repair_times == other.repair_times and
                self.enchantments == other.enchantments)

    def __hash__(self):
        return hash((self.repair_times, self.enchantments))

    def set_prices(self, price_list: list):
        self.enchantments = [i.set_price(price_list)
                             for i in self.enchantments]
        return self

    def get_total_price(self) -> int:
        if self.total_price != 0:
            return self.total_price
        tools = [i.fit_tool for i in self.enchantments]
        tools = set(itertools.chain.from_iterable(tools))
        max_price = 0
        for tool in tools:
            prices = [i.price for i in self.enchantments if tool in i.fit_tool]
            max_price = max_price if (sum(prices) < max_price) else sum(prices)
        self.total_price = max_price
        return max_price

    def get_sold_price(self) -> int:
        if self.total_price == 0:
            self.get_total_price()
        multiply: float = 1 if (
            self.repair_times == 0)\
            else self.repair_times * REPAIR_TIMES_MULTIPLIER
        return int(self.total_price * multiply)

    def get_buy_price(self) -> int:
        if self.total_price == 0:
            self.get_total_price()
        multiply: float = 1 if (
            self.repair_times == 0)\
            else self.repair_times * REPAIR_TIMES_MULTIPLIER
        return int(self.total_price * multiply * BUY_PRICE_MULTIPLIER)

    def to_dict(self) -> dict:
        return {
            "item_type": self.item_type,
            "repair_times": self.repair_times,
            "enchantments": [e.to_dict() for e in self.enchantments],
            "total_price": self.total_price
        }


class Enchantment:
    namespaced_id: str = ""
    level: int = -1
    price: int = 0
    fit_tool: list = []
    japanese: str = ""

    def __init__(self, _dict: dict):
        super().__init__()
        self.namespaced_id = _dict.get('enchantment', "")
        self.level = _dict.get('level', -1)

    def __repr__(self):
        return "buy_book.Enchantment(namespaced_id: " +\
               self.namespaced_id +\
               ", level: " +\
               str(self.level) +\
               ", price: " +\
               str(self.price) +\
               ", fit_tool: " +\
               str(self.fit_tool) +\
               ")"

    def __eq__(self, other):
        if not isinstance(other, Enchantment):
            return NotImplemented
        return (self.namespaced_id == other.namespaced_id and
                self.level == other.level)

    def __hash__(self):
        return hash(
            (self.namespaced_id,
             self.level,
             self.price,
             self.fit_tool))

    def set_price(self, price_list: list):
        this_id = self.namespaced_id.split(":")[1]
        for item in price_list:
            if this_id != item['id']:
                continue
            self.price = item['price'][self.level - 1]
            self.fit_tool = item.get('fit', [])
            self.japanese = item.get('japanese', "")
        return self

    def get_price(self):
        return self.price

    def to_dict(self) -> dict:
        return {
            "namespaced_id": self.namespaced_id,
            "level": self.level,
            "price": self.price,
            "fit_tool": self.fit_tool,
            "japanese": self.japanese,
        }


class SourceFileJsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, SourceFile):
            return o.to_dict()
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        return super(SourceFileJsonEncoder, self).default(o)
