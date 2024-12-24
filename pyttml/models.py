from dataclasses import dataclass
from typing import List
from enum import Enum

class Vocal(Enum):
    STANDARD = 0
    PRIMARY = 1
    SECONDARY = 2

@dataclass
class Element:
    index: int
    start_time: float
    end_time: float
    text: str
    is_part_of_word: bool = False
    is_explicit: bool = False

    def get_start_time(self) -> float:
        return self.start_time
    
    def get_end_time(self) -> float:
        return self.end_time
    
    def __str__(self):
        return self.text

@dataclass
class Line:
    index: int
    elements: List[Element]
    vocal: Vocal = Vocal.STANDARD
    is_backing: bool = False

    def get_start_time(self) -> float:
        return self.elements[0].get_start_time()

    def get_end_time(self) -> float:
        return self.elements[-1].get_end_time()

    def __str__(self):
        _str = ""

        index = 0
        for i in range(len(self.elements)):
            if self.elements[i].index > index:
                _str += " "
                index = self.elements[i].index
            _str += str(self.elements[i])
        return _str