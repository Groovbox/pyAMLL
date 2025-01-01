from textual.app import ComposeResult
from textual.widgets import Label
from textual.containers import Horizontal, Vertical
from ttml import VocalElement, Line, Lyrics
from enum import Enum


class CarouselItem(Vertical):
    def __init__(self, *children, name = None, id = None, classes = None, disabled = False,
                 element:VocalElement=None, is_active=False):
    
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


class ScrollDirection(Enum):
    forward = 1
    backward = -1


class Carousel(Vertical):
    active_item:CarouselItem = None

    substitue_last:CarouselItem = None
    substitue_first:CarouselItem = None

    lyrics:Lyrics = None

    def __init__(self, *children, name = None, id = None, classes = None, disabled = False, lyrics:Lyrics):
        self.lyrics = lyrics
        super().__init__(*children, name=name, id=id, classes=classes, disabled=disabled)

    def compose(self) -> ComposeResult:
        yield(Horizontal(id="root"))

    
    def on_mount(self) -> None:
        self.substitue_last = CarouselItem(element=self.lyrics.element_map[5][0])
        for i in range(5):
            self.push(self.lyrics.element_map[i][0], active=(i==0))


    def shift_cursor(self,scroll_direction:ScrollDirection) -> None:
        """
        Sets the next or the previous CarouselItem as active and current Item as Inactive
        """

        active_item_index = self.query_one("#root")._nodes.index(self.active_item)
        self.active_item.set_state(False)

        new_active_item:CarouselItem = self.query_one("#root")._nodes[active_item_index+scroll_direction.value]
        new_active_item.set_state(True)
        self.active_item = new_active_item

    
    def move(self, scroll_direction:ScrollDirection) -> None:
        """
        Moves the carousel left or right by one item
        """
        _forward = ScrollDirection.forward
        _backward = ScrollDirection.backward

        active_item_map_index = self.lyrics.get_element_map_index(self.active_item.element)

        if active_item_map_index == 0 and scroll_direction==_backward:
            return
        
        if active_item_map_index == len(self.lyrics.element_map)-1 and scroll_direction==_forward:
            return

        self.shift_cursor(scroll_direction)

        active_item_map_index = self.lyrics.get_element_map_index(self.active_item.element)

        if active_item_map_index <= 1 and scroll_direction==_backward:
            return
        
        if active_item_map_index >= len(self.lyrics.element_map)-3 and scroll_direction == _backward:
            return

        elif active_item_map_index <= 2 and scroll_direction==_forward:
            return
        
        if active_item_map_index >= len(self.lyrics.element_map)-2 and scroll_direction==_forward:
            return
        
        end_item:CarouselItem = self.query_one("#root")._nodes[0 if scroll_direction==_backward else -1]

        if scroll_direction==_forward and self.lyrics.element_map[-1][0] == self.substitue_last.element:
            self.push(self.substitue_last)
            self.substitue_last = None
            self.substitue_first = self.query_one("#root")._nodes[0]
            self.query_one("#root").remove_children("CarouselItem:first-of-type")
            return
    
        sub_element = self.lyrics.get_offset_element(end_item.element, scroll_direction.value*2)

        if scroll_direction == _forward:        
            self.push(self.substitue_last)
            self.substitue_last = CarouselItem(element=sub_element)
            self.substitue_first = self.query_one("#root")._nodes[0]
            self.query_one("#root").remove_children("CarouselItem:first-of-type")
        else:            
            self.push(self.substitue_first, first=True)
            self.substitue_first = CarouselItem(element=sub_element)
            self.substitue_last = self.query_one("#root")._nodes[-1]
            self.query_one("#root").remove_children("CarouselItem:last-of-type")

    
    def move_to_element_map_index(self, scroll_direction:ScrollDirection, element_map_index:int) -> None:
        new_fist_index = (element_map_index*scroll_direction.value)

        self.query_one("#root").remove_children()
        
        for i in range(5):
            _active = False
            if i==2:
                _active = True
            self.push(self.lyrics.element_map[new_fist_index+i][0], active=_active)
        
        self.substitue_first = self.lyrics.element_map[new_fist_index-1][0]
        self.substitue_last = self.lyrics.element_map[new_fist_index+5][0]
        self.active_item = self.lyrics.element_map[new_fist_index+2]
        
    def push(self, element_or_item:VocalElement|CarouselItem, active:bool=False, first=False) -> None:

        root = self.query_one("#root")

        if isinstance(element_or_item,CarouselItem):
            _new_element = element_or_item
        else:
            _new_element = CarouselItem(element=element_or_item, is_active=active)        
        root.mount(_new_element)

        if first:
            _old_first = root._nodes[0]
            root.move_child(_new_element, before=_old_first)
        
        if active:
            self.active_item = _new_element

