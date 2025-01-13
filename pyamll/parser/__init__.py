from dataclasses import dataclass
from typing import List
from enum import Enum

class Vocal(Enum):
    STANDARD = 0
    PRIMARY = 1
    SECONDARY = 2


@dataclass
class VocalElement:
    text: str
    line_index:int
    is_part_of_word:bool = False
    is_explicit: bool = False
    start_time: float = 0
    end_time: float = 0
    
    def __str__(self):
        return self.text

@dataclass
class Line:
    index: int
    elements: List[VocalElement]
    vocal: Vocal = Vocal.STANDARD
    is_backing: bool = False

    @property
    def start_time(self) -> float:
        return self.elements[0].get_start_time()

    @property
    def end_time(self) -> float:
        return self.elements[-1].get_end_time()

    def is_last_element(self, element:VocalElement|int) -> bool:
        if isinstance(element, int):
            if element == len(self.elements)-1:
                return True
            return False
        if self.elements[-1] == element:
            return True
        return False

    def __str__(self):
        _str = ""

        part_of_word = False
        for i in range(len(self.elements)):
            _str += str(self.elements[i])
            part_of_word = self.elements[i].is_part_of_word
            if not part_of_word:
                _str+=" "

        return _str.strip()
    
class Lyrics(list):
    element_map = []
    init_list:list[Line]
    
    def __init__(self, init_list:list[Line], *args):
        self.init_list = init_list
        for i,line in enumerate(init_list):
            line:Line = line
            for j, element in enumerate(line.elements):
                self.element_map.append([element, i, j])
        super().__init__(*args)
    
    def get_offset_element(self, element:VocalElement, offset:int) -> VocalElement:
        for i,map_item in enumerate(self.element_map):
            if element == map_item[0]:
                return self.element_map[i+offset][0]
    
    def get_element_map_index(self, element:VocalElement) -> int:
        for i,map_item in enumerate(self.element_map):
            if element == map_item[0]:
                return i
        return 0


def process_lyrics(lyrics_str:str) -> Lyrics:
    if lyrics_str == "":
        return

    text_lines:list[str] = lyrics_str.split("\n")
    line_objects:list[Line] = []

    for line_counter in range(len(text_lines)):
        if text_lines[line_counter] == "":
            continue

        text_line = text_lines[line_counter]

        if text_line.startswith("(") and text_line.endswith(")"):
            text_line = text_line.strip("()")
            is_backing = True
        else:
            is_backing = False

        line = Line(index=line_counter, elements=[], vocal=Vocal.STANDARD, is_backing=is_backing)

        for word_counter in range(len(text_line.split(" "))):
            word = text_line.split(" ")[word_counter]
            if word.strip() == "":
                continue

            # if / in word like heart/beat then the first word will have the bool but not last
            if '/' in word:
                syllables = word.split('/')
                for syllable_counter in range(len(syllables)):
                    line.elements.append(
                        VocalElement(text=syllables[syllable_counter], is_part_of_word=(syllable_counter != len(syllables)-1) ,line_index=len(line_objects)))
                continue
            
            line.elements.append(VocalElement(text=word, line_index=len(line_objects)))

        line_objects.append(line)
    return Lyrics(line_objects)
