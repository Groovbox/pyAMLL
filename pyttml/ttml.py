from dataclasses import dataclass
from typing import List
from enum import Enum

class Vocal(Enum):
    STANDARD = 0
    PRIMARY = 1
    SECONDARY = 2

@dataclass
class Element:
    word_index: int
    text: str
    line_index:int
    is_explicit: bool = False
    start_time: float = 0
    end_time: float = 0
    
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

    def is_last_element(self, element:Element|int) -> bool:
        if isinstance(element, int):
            if element == len(self.elements)-1:
                return True
            return False
        if self.elements[-1] == element:
            return True
        return False

    def __str__(self):
        _str = ""

        index = 0
        for i in range(len(self.elements)):
            if self.elements[i].word_index > index:
                _str += " "
                index = self.elements[i].word_index
            _str += str(self.elements[i])
        return _str

def dump_lyrics(line_objects) -> None:
    with open("dump.txt", "w") as f:
        for lines in line_objects:
            for elements in lines.elements:
                f.write(f"Text: {elements.text}\n")
                f.write(f"Word Index: {elements.word_index}\n")
                f.write(f"Line Index: {elements.line_index}\n")
            f.write("\n\n")

def process_lyrics(lyrics_str:str) -> list[Line]:

    text_lines:list[str] = lyrics_str.split("\n")
    line_objects:list[Line] = []

    for line_counter in range(len(text_lines)):
        if text_lines[line_counter] == "":
            continue

        text_line = text_lines[line_counter]

        if text_line.startswith("(") and text_line.endswith(")"):
            is_backing = True
        else:
            is_backing = False

        line = Line(index=line_counter, elements=[], vocal=Vocal.STANDARD, is_backing=is_backing)

        for word_counter in range(len(text_line.split(" "))):
            word = text_line.split(" ")[word_counter]

            if '/' in word:
                syllables = word.split('/')
                for syllable_counter in range(len(syllables)):
                    line.elements.append(Element(word_index=word_counter, text=syllables[syllable_counter], line_index=len(line_objects)))
                continue
            
            line.elements.append(Element(word_index=word_counter, text=word, line_index=len(line_objects)))

        line_objects.append(line)
    dump_lyrics(line_objects)
    return line_objects
