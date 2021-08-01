from json import dumps, loads
import json

class SimpleQueue():
    """Simple queue."""
    def __init__(self):
        self.__queue = list()
        self.__tail = 0
        self.__head = 0
        return
    
    # Properties
    @property
    def is_empty(self) -> bool:
        return self.__head == self.__tail

    @property
    def head(self) -> int:
        return self.__head

    @property
    def tail(self) -> int:
        return self.__tail

    @property
    def active_indexes(self) -> list:
        return range(self.__head, self.__tail)

    @property
    def active_items(self) -> list:
        return [self.__queue[i] for i in self.active_indexes]

    @property
    def active_number(self) -> int:
        return self.__tail - self.__head

    @property
    def history(self) -> list:
        return self.__queue

    @property
    def last_one(self):
        return self.history[self.head - 1]
    
    @property
    def as_string(self) -> str:
        queue_dict = {
            "head": self.__head,
            "tail": self.__tail,
            "queue": self.__queue
        }
        return dumps(queue_dict, ensure_ascii = False, indent = 4)
    
    @property
    def as_dict(self) -> dict:
        queue_dict = {
            "head": self.__head,
            "tail": self.__tail,
            "queue": self.__queue
        }
        return queue_dict

    # Methods
    def add(self, item):
        """Add an item into queue."""
        self.__queue.append(item)
        self.__tail += 1
        return

    def pop(self):
        """Pop up an item and return it."""
        self.__head += 1
        return self.__queue[self.__head - 1]

    def add_items(self, items: list):
        """Add items into queue."""
        for item in items:
            self.add(item)
        return

    def compress(self):
        """Compress queue. This will drop all deactive items."""
        self.__queue = self.active_items
        self.__tail = self.active_number
        self.__head = 0
        return

    def pop_all(self):
        """Pop up all item."""
        pops = list()
        while not self.is_empty:
            pops.append(self.pop())
        return pops

    def clean(self):
        self.__head = self.__tail
        return

    def reinitialize(self):
        """Reinitialize queue. But why don't you create a new empty queue?"""
        self.__queue = list()
        self.__head = 0
        self.__tail = 0
        return
    
    @staticmethod
    def load_from_string(string: str):
        queue_dict = loads(string)
        queue = SimpleQueue()
        queue.__head = queue_dict["head"]
        queue.__tail = queue_dict["tail"]
        queue.__queue = queue_dict["queue"]
        return queue

    @staticmethod
    def load_from_dict(dic: dict):
        queue = SimpleQueue()
        queue.__head = dic["head"]
        queue.__tail = dic["tail"]
        queue.__queue = dic["queue"]
        return queue

    # Magic Methods
    def __repr__(self):
        """For directly typing in command line."""
        abstract = "Head: {}, Tail: {}\n".format(self.head, self.tail)
        abstract += "Active: {}\n".format(self.active_items)
        abstract += "History:{}\n".format(self.history)
        return abstract

    def __str__(self):
        """For print()."""
        return self.__repr__()

    def __len__(self):
        """For len()."""
        return self.active_number

    def __iter__(self):
        """For iterator"""
        for item in self.active_items:
            yield item

    def __contains__(self, item):
        """For operator 'in'."""
        return item in self.active_items

    def __bool__(self):
        """Convert to bool."""
        return not self.is_empty
