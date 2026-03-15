from dataclasses import dataclass

@dataclass
class Book:
    title: str
    price: float

    def getRowOfData(self):
        return [str(self.title), str(self.price)]
    