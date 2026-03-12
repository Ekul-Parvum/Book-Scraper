class Book:
    def __init__(self, title, price):
        self.title = title
        self.price = price
    
    def getRowOfData(self):
        return [str(self.title), str(self.price)]