class Car:
    def __init__(self, make, model, year):
        self.make = make
        self.model = model
        self.year = year

    def describe(self):
        print(f"{self.year} {self.make} {self.model}")

    def is_old(self):
        if self.year < 2016:
            return True
        else:
            return False

car1 = Car("Honda", "Civic", 2015)
car2 = Car("Hyundai", "Tuscon", 2019)

car1.describe()
car2.describe()

print(car1.is_old())
print(car2.is_old())