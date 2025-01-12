from enum import Enum
from parser import Lyrics, VocalElement

class ModificationType(Enum):
    EDIT = "edit"
    DELETE = "delete"
    APPEND = "append"

class OperationStatus(Enum):
    PENDING = "pending"
    ONGOING = "ongoing"
    EXEUTED = "executed"
    FAILED = "failed"

class LyricModifyOperation():
    def __init__(self,_type:ModificationType, modified_element:VocalElement ,lyrics:Lyrics|None=None) -> None:
        self._type = _type
        self.lyrics = lyrics
        self.status:OperationStatus = OperationStatus.PENDING
        self.context:str = ""
        self.modified_element = modified_element
    
    def execute(self) -> Lyrics:

        if self._type == ModificationType.DELETE:
            for mapping in self.lyrics.element_map:
                i_element:VocalElement = mapping[0]
                line = mapping[1]
                word = mapping[2]
                if (i_element.line_index, i_element.word_index) == (self.modified_element.line_index, self.modified_element.word_index):
                    break
            
            self.lyrics.init_list[line].elements[word] = None
        
        self.lyrics.rebuild()
        self.status = OperationStatus.EXEUTED
        return self.lyrics
