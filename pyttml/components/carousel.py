from textual.app import ComposeResult
from textual.widgets import Label
from textual.containers import Horizontal, Vertical
from ttml import Element, Line


class CarouselElement(Vertical):
    def __init__(self, *children, name = None, id = None, classes = None, disabled = False,
                 element:Element=None, is_active=False):
    
        self.element = element
        self.is_active = is_active

        super().__init__(*children, name=name, id=id, classes=classes, disabled=disabled)

    def compose(self) -> ComposeResult:
        yield Label(str(self.element.start_time), id="start_time")
        yield Label(self.element.text, classes="element_text")
        yield Label(str(self.element.end_time), id="end_time")
    
    def toggle_timestamps(self, hide=None):
        start_time_label = self.query_one("#start_time")
        end_time_label = self.query_one("#end_time")

        if hide is not None and isinstance(hide, bool):
            start_time_label.visible = not(hide)
            end_time_label.visible = not(hide)
            return
        
        start_time_label.visible = not(start_time_label.visible)
        start_time_label.visible = not(start_time_label.visible)
    
    def set_state(self, active):
        if active:
            self.is_active = True
            self.classes = "active"
            self.toggle_timestamps(False)
            return
        
        self.is_active = False
        self.classes = ""
        self.toggle_timestamps(True)
    
    def on_mount(self):
        self.set_state(self.is_active)
    
    def __str__(self):
        return self.element.text


class WordCarousel(Vertical):
    last_word_line_index = 0
    first_item_line_index = 0
    last_word_index = 0
    first_word_index = 0
    lyrics:str = None

    def __init__(self, *children, name = None, id = None, classes = None, disabled = False, lyrics:str):
        self.lyrics = lyrics
        super().__init__(*children, name=name, id=id, classes=classes, disabled=disabled)

    def compose(self) -> ComposeResult:
        yield(Horizontal(id="root"))
        
    def push(self, element:Element, active:bool=False, first=False):
        root = self.query_one("#root")
        _new_element = CarouselElement(element=element, is_active=active)        
        root.mount(_new_element)

        if first:
            _old_first = root._nodes[0]
            root.move_child(_new_element, before=_old_first)


        for line in self.lyrics:
            line:Line = line
            if element in line.elements:
                if first:
                    self.first_item_line_index = self.lyrics.index(line)
                    self.first_word_index = line.elements.index(element)
                    break
                self.last_word_line_index = self.lyrics.index(line)
                self.last_word_index = line.elements.index(element)
                break
