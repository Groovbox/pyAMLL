from dataclasses import dataclass
from typing import List
from enum import Enum
from pathlib import Path
import json

class Vocal(Enum):
    STANDARD = 0
    PRIMARY = 1
    SECONDARY = 2

class ExportFormat(Enum):
    APPLE_SWLRC = "swlrc.json"
    TTML = "ttml"


@dataclass
class VocalElement:
    word_index: int
    text: str
    line_index:int
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

        index = 0
        for i in range(len(self.elements)):
            if self.elements[i].word_index > index:
                _str += " "
                index = self.elements[i].word_index
            _str += str(self.elements[i])
        return _str
    
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
    
    def export(self, file:Path, format:ExportFormat) -> None:
        if format == ExportFormat.APPLE_SWLRC:
            content = parse_lyrics_to_swlrc(self)
            with open(file, "w") as f:
                f.write(json.dumps(content, indent=2))

            
def parse_lyrics_to_swlrc(lyrics:Lyrics) -> dict:
    swl = {
        "StartTime": lyrics.element_map[0][0].start_time,
        "EndTime": lyrics.element_map[-1][0].end_time,
        "Type": "Syllable",
        "VocalGroups": []
    }

    for line in lyrics.init_list:
        line:Line = line

        _lead_list = []

        for i,element in enumerate(line.elements):
            element:VocalElement = element
            _is_part_of_word = False
            try:
                if line.elements[i+1].word_index == element.word_index:
                    _is_part_of_word = True
            except IndexError:
                pass            

            _lead_list.append({
                "Text": element.text,
                    "IsPartOfWord": _is_part_of_word,
                    "StartTime": element.start_time,
                    "EndTime": element.end_time
            })
        
        swl["VocalGroups"].append({
            "Type":"Vocal",
            "OppositeAligned": (line.vocal == Vocal.SECONDARY),
            "StartTime": line.start_time,
            "EndTime": line.end_time,
            "Lead": _lead_list
        })
    
    return swl

def dump_lyrics(line_objects) -> None:
    with open("dump.txt", "w") as f:
        for lines in line_objects:
            for elements in lines.elements:
                f.write(f"Text: {elements.text}\n")
                f.write(f"Word Index: {elements.word_index}\n")
                f.write(f"Line Index: {elements.line_index}\n")
            f.write("\n\n")

def process_lyrics(lyrics_str:str) -> Lyrics:

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
                    line.elements.append(VocalElement(word_index=word_counter, text=syllables[syllable_counter], line_index=len(line_objects)))
                continue
            
            line.elements.append(VocalElement(word_index=word_counter, text=word, line_index=len(line_objects)))

        line_objects.append(line)
    dump_lyrics(line_objects)

    return Lyrics(line_objects)
