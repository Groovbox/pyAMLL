from textual.app import ComposeResult
from textual.widgets import Label, ListItem, ListView
from textual.containers import Horizontal, Vertical
from parser import VocalElement, Lyrics
from parser.modify import ModificationType
from enum import Enum
from utils import convert_seconds_to_format as fsec


class ScrollDirection(Enum):
    forward = 1
    backward = -1

class CarouselItem(Vertical):
    def __init__(self, element:VocalElement=None, active=False):
        self.element = element
        self.active = active
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Label(fsec(self.element.start_time), id="start_time")
        yield Label(self.element.text, classes="element_text")
        yield Label(fsec(self.element.end_time), id="end_time")
    
    def update(self) -> None:
        self.query_one("#start_time", Label).update(fsec(self.element.start_time))
        self.query_one("#end_time", Label).update(fsec(self.element.end_time))
    
    def set_state(self, active):
        start_time_label:Label = self.query_one("#start_time")
        end_time_label:Label = self.query_one("#end_time")

        if active:
            self.active = True
            self.classes = "active"
            start_time_label.visible = True
            end_time_label.visible = True
        else:        
            self.active = False
            self.classes = ""
            start_time_label.visible = False
            end_time_label.visible = False
    
    def on_mount(self):
        self.set_state(self.active)
    
    def __str__(self):
        return self.element.text


class Carousel(Horizontal):
    active_item:CarouselItem = None

    def on_mount(self) -> None:
        # TODO: Set variable number of elements displayed in the carousel.
        for i in range(5):
            try:
                self.push(self.app.CURR_LYRICS.element_map[i][0], active=(i==0))
            except IndexError:
                break

    def shift_cursor(self,scroll_direction:ScrollDirection) -> None:
        """
        Sets the next or the previous CarouselItem as active and current Item as Inactive
        """

        active_item_index = self._nodes.index(self.active_item)
        new_index = active_item_index+scroll_direction.value

        if new_index not in range(0, len(self._nodes)):
            return
        self.active_item.set_state(False)

        new_active_item:CarouselItem = self._nodes[new_index]
        new_active_item.set_state(True)
        self.active_item = new_active_item
    
    def move(self, scroll_direction:ScrollDirection) -> None:
        """
        Moves the carousel left or right by one item
        """
        lyrics:Lyrics = self.app.CURR_LYRICS

        self.shift_cursor(scroll_direction)

        active_item_map_index = lyrics.get_element_map_index(self.active_item.element)
        last_item_map_index = lyrics.get_element_map_index(self._nodes[-1].element)
        first_item_map_index = lyrics.get_element_map_index(self._nodes[0].element)

        # Prevent carousel movement
        if scroll_direction == ScrollDirection.forward:
            if last_item_map_index >= len(lyrics.element_map)-1:
                return
            if active_item_map_index in range(0,3):
                return
            
            self.remove_children("CarouselItem:first-of-type")
            self.push(lyrics.element_map[last_item_map_index+1][0])

        elif scroll_direction == ScrollDirection.backward:
            total_elements = len(lyrics.element_map)
            if first_item_map_index == 0:
                return
            if active_item_map_index in range(total_elements-3,total_elements-1):
                return
            
            self.remove_children("CarouselItem:last-of-type")
            self.push(lyrics.element_map[first_item_map_index-1][0], first=True)

    def move_to_element_map_index(self, scroll_direction:ScrollDirection, element_map_index:int) -> None:
        new_fist_index = (element_map_index*scroll_direction.value)

        self.remove_children()
        
        for i in range(5):
            _active = False
            if i==2:
                _active = True
            self.push(self.app.CURR_LYRICS.element_map[new_fist_index+i][0], active=_active)
        
        self.active_item = self.app.CURR_LYRICS.element_map[new_fist_index+2]
        
    def push(self, vocal_element:VocalElement, active:bool=False, first=False) -> None:
        """
        Adds a new CarouselItem to the carousel.
        Args:
            vocal_element (VocalElement): The vocal element to be added to the carousel.
            active (bool, optional): If True, sets the new item as the active item. Defaults to False.
            first (bool, optional): If True, inserts the new item at the beginning of the carousel. Defaults to False.
        Returns:
            None
        """

        new_item = CarouselItem(element=vocal_element, active=active)        
        self.mount(new_item)

        if first:
            _old_first = self._nodes[0]
            self.move_child(new_item, before=_old_first)
        
        if active:
            self.active_item = new_item
    
    def rebuild(self) -> None:
        operation = self.app.CURR_LYRICS.modification_stack[-1]
        if operation._type == ModificationType.DELETE:
            self.remove_children(".active") # Remove the current active element
            # If first element then go to next element
            if self.active_item.element.line_index == 0 and self.active_item.element.word_index == 0:
                self.move(ScrollDirection.forward)
            else:
                self.move(ScrollDirection.backward)
            # Else go back
            


class VerticalScroller(ListView):
    active_line_index:int = 0

    def on_mount(self) -> None:
        for line in self.app.CURR_LYRICS.init_list:
            self.mount(ListItem(Label(str(line))))
        
        self._nodes[self.active_line_index].add_class("lyric-line-active")

    def scroll(self, scroll_direction:ScrollDirection):
        self._nodes[self.active_line_index].remove_class("lyric-line-active")
        self.active_line_index = self.active_line_index+scroll_direction.value
        self._nodes[self.active_line_index].add_class("lyric-line-active")
