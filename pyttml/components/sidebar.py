from textual.widgets import Button
from textual.containers import Vertical


class Sidebar(Vertical):    
    def on_mount(self) -> None:
        for screen in self.app.SCREENS.keys():
            self.mount(Button(
            label=screen.capitalize(),
            id=f"nav_{screen}_button",
            tooltip=f"Switch to {screen.capitalize} Screen",
        ))
            
        current_mode = self.app.current_mode
        self.query_one(f"#nav_{current_mode}_button").disabled = True

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id.startswith("nav_"):
            self.app.switch_mode(event.button.id.split("_")[1])