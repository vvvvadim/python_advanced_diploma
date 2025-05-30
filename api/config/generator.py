import random
from random import sample
from string import digits

first_name_list = ["Vasya", "John", "Petya", "Maxim", "Anton"]


class TestUser:
    name: str
    api_key: str = "test"

    def __init__(self) -> None:
        self.name = random.choice(first_name_list)
        self.api_key = "".join(sample(digits, 10))

    def __str__(self) -> str:
        return f"name : {self.name}, api-key : {self.api_key}, "
