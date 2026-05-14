# This is the book dataclass. Used to store the books in memory prior to saving them into whatever format one needs.

from dataclasses import dataclass

@dataclass
class Book:
    title: str
    price: float

    def getRowOfData(self):
        return [str(self.title), str(self.price)]
    