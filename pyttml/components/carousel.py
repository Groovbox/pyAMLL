from textual.app import ComposeResult
from textual.widgets import Label, ListItem, ListView
from textual.containers import Horizontal, Vertical
from ttml import VocalElement, Lyrics
from enum import Enum
from utils import convert_seconds_to_format as fsec


class CarouselItem(Vertical):
    def __init__(self, *children, name = None, id = None, classes = None, disabled = False,
                 element:VocalElement=None, is_active=False):
    
        self.element = element
        self.is_active = is_active

        super().__init__(*children, name=name, id=id, classes=classes, disabled=disabled)

    def compose(self) -> ComposeResult:
        yield Label(fsec(self.element.start_time), id="start_time")
        yield Label(self.element.text, classes="element_text")
        yield Label(fsec(self.element.end_time), id="end_time")
    
    def update(self) -> None:
        self.query_one("#start_time", Label).update(fsec(self.element.start_time))
        self.query_one("#end_time", Label).update(fsec(self.element.end_time))


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

    def compose(self) -> ComposeResult:
        yield(Horizontal(id="root"))

    
    def on_mount(self) -> None:
        self.substitue_last = CarouselItem(element=self.app.CURR_LYRICS.element_map[5][0])
        for i in range(5):
            self.push(self.app.CURR_LYRICS.element_map[i][0], active=(i==0))

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

        active_item_map_index = self.app.CURR_LYRICS.get_element_map_index(self.active_item.element)

        # Prevent cursor movement if at the first index or last index
        if active_item_map_index == 0 and scroll_direction == _backward:
            return
        if active_item_map_index == len(self.app.CURR_LYRICS.element_map) - 1 and scroll_direction == _forward:
            return

        self.shift_cursor(scroll_direction)

        active_item_map_index = self.app.CURR_LYRICS.get_element_map_index(self.active_item.element)

        # Prevent carousel movement towards the end
        if scroll_direction == _backward:
            if active_item_map_index <= 1 or active_item_map_index >= len(self.app.CURR_LYRICS.element_map) - 3:
                return

        # Prevent carousel movement up till the third item
        elif scroll_direction == _forward:
            if active_item_map_index <= 2 or active_item_map_index >= len(self.app.CURR_LYRICS.element_map) - 2:
                return
        
        end_item:CarouselItem = self.query_one("#root")._nodes[0 if scroll_direction==_backward else -1]

        if scroll_direction==_forward and self.app.CURR_LYRICS.element_map[-1][0] == self.substitue_last.element:
            self.push(self.substitue_last)
            self.substitue_last = None
            self.substitue_first = self.query_one("#root")._nodes[0]
            self.query_one("#root").remove_children("CarouselItem:first-of-type")
            return
    
        sub_element = self.app.CURR_LYRICS.get_offset_element(end_item.element, scroll_direction.value*2)

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
            self.push(self.app.CURR_LYRICS.element_map[new_fist_index+i][0], active=_active)
        
        self.substitue_first = self.app.CURR_LYRICS.element_map[new_fist_index-1][0]
        self.substitue_last = self.app.CURR_LYRICS.element_map[new_fist_index+5][0]
        self.active_item = self.app.CURR_LYRICS.element_map[new_fist_index+2]
        
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


class VerticalScroller(ListView):
    lyrics:Lyrics = None
    active_line_index:int = 0

    def __init__(self, *children, initial_index = 0, name = None, id = None, classes = None, disabled = False, lyrics:Lyrics=lyrics):
        self.app.CURR_LYRICS = lyrics
        super().__init__(*children, initial_index=initial_index, name=name, id=id, classes=classes, disabled=disabled)

    def on_mount(self) -> None:
        for line in self.app.CURR_LYRICS.init_list:
            self.mount(ListItem(Label(str(line))))
        
        self._nodes[self.active_line_index].add_class("lyric-line-active")

    def scroll(self, scroll_direction:ScrollDirection):
        self._nodes[self.active_line_index].remove_class("lyric-line-active")
        self.active_line_index = self.active_line_index+scroll_direction.value
        self._nodes[self.active_line_index].add_class("lyric-line-active")

