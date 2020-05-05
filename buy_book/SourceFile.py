import datetime
import itertools

REPAIR_TIMES_MULTIPLIER: float = 0.8
BUY_PRICE_MULTIPLIER: float = 0.5


class SourceFile():
    created_date: datetime.datetime = None
    books: list = []
    total_sold_price: int = 0

    def __init__(self, _dict: dict):
        super().__init__()
        self.books = []
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

    def set_prices(self, prices: dict):
        self.books = [i.set_prices(prices['prices']) for i in self.books]
        return self

    def get_total_sold_price(self) -> int:
        if self.total_sold_price == 0:
            self.total_sold_price = sum([i.get_sold_price() for i in self.books])
        return self.total_sold_price

    def get_total_buy_price(self) -> int:
        if self.total_sold_price == 0:
            self.get_total_sold_price()
        return int(self.total_sold_price * BUY_PRICE_MULTIPLIER)


class Book():
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
        return (self.repair_times == other.repair_times
                and self.enchantments == other.enchantments)

    def __hash__(self):
        return hash((self.repair_times, self.enchantments))

    def set_prices(self, price_list: list):
        self.enchantments = [i.set_price(price_list) for i in self.enchantments]
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
        multiply: float = 1 if (self.repair_times == 0) else self.repair_times * REPAIR_TIMES_MULTIPLIER
        return int(self.total_price * multiply)


class Enchantment:
    namespaced_id: str = ""
    level: int = -1
    price: int = 0
    fit_tool: list = []

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
        return (self.namespaced_id == other.namespaced_id
                and self.level == other.level)

    def __hash__(self):
        return hash((self.namespaced_id, self.level, self.price, self.fit_tool))

    def set_price(self, price_list: list):
        this_id = self.namespaced_id.split(":")[1]
        for item in price_list:
            if this_id != item['id']:
                continue
            self.price = item['price'][self.level - 1]
            self.fit_tool = item.get('fit', [])
        return self

    def get_price(self):
        return self.price
