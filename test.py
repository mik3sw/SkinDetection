'''from rich.panel import Panel

from textual.app import App
from textual.reactive import Reactive
from textual.widget import Widget


class Hover(Widget):

    mouse_over = Reactive(False)

    def render(self) -> Panel:
        return Panel("Hello [b]World[/b]", style=("on red" if self.mouse_over else ""))

    def on_enter(self) -> None:
        self.mouse_over = True

    def on_leave(self) -> None:
        self.mouse_over = False


class HoverApp(App):
    """Demonstrates custom widgets"""

    async def on_mount(self) -> None:
        hovers = (Hover() for _ in range(10))
        await self.view.dock(*hovers, edge="top")


HoverApp.run(log="textual.log")'''

from textual.app import App
from textual.reactive import Reactive
from textual.widgets import Footer, Placeholder
from rich.panel import Panel
from datetime import datetime
from textual.widget import Widget
from rich.align import Align
from rich.markdown import Markdown

MARKDOWN = """
# Progetto Elaborazione delle Immagini
__Partecipanti__
1. Mattia Napoli       [852239]
2. Eleonora Cicalla    [851649]
3. Michele Marcucci    [851905]
"""

class Clock(Widget):
    def on_mount(self):
        self.set_interval(1, self.refresh)

    def render(self):
        time = datetime.now().strftime("%c")
        return Align.center(time, vertical="middle")
    
class SideBar(Widget):
    def on_mount(self):
        self.set_interval(1, self.refresh)
    
    def render(self):
        return Align.right(Markdown(MARKDOWN), vertical="top")

class Cam(Widget):

    mouse_over = Reactive(False)

    def render(self) -> Panel:
        return Align.center(Panel("[b]Video from webcam[/b]", style=("on green" if self.mouse_over else "")), vertical="middle")

    def on_enter(self) -> None:
        self.mouse_over = True

    def on_leave(self) -> None:
        self.mouse_over = False

class File(Widget):

    mouse_over = Reactive(False)

    def render(self) -> Panel:
        return Align.center(Panel("[b]Video from file[/b]", style=("on green" if self.mouse_over else "")), vertical="middle")

    def on_enter(self) -> None:
        self.mouse_over = True

    def on_leave(self) -> None:
        self.mouse_over = False

class SmoothApp(App):
    """Demonstrates smooth animation. Press 'b' to see it in action."""

    async def on_load(self) -> None:
        """Bind keys here."""
        await self.bind("b", "toggle_sidebar", "Informazioni")
        await self.bind("q", "quit", "Quit")

    show_bar = Reactive(False)

    def watch_show_bar(self, show_bar: bool) -> None:
        """Called when show_bar changes."""
        self.bar.animate("layout_offset_x", 0 if show_bar else -40)

    def action_toggle_sidebar(self) -> None:
        """Called when user hits 'b' key."""
        self.show_bar = not self.show_bar

    async def on_mount(self) -> None:
        """Build layout here."""
        footer = Footer()
        self.bar = SideBar(name="Informazioni")

        await self.view.dock(footer, edge="bottom")
        await self.view.dock(Cam(name="Cam"), File(name="File"), edge="top")
        await self.view.dock(self.bar, edge="left", size=40, z=1)
        #Panel("Hello [b]World[/b]", style=("on red" if self.mouse_over else ""))

        self.bar.layout_offset_x = -40

        # self.set_timer(10, lambda: self.action("quit"))


SmoothApp.run(title="Progetto Elaborazione Immagini", log="textual.log")

'''
import os
import sys
from rich.console import RenderableType

from rich.syntax import Syntax
from rich.traceback import Traceback

from textual.app import App
from textual.widgets import Header, Footer, FileClick, ScrollView, DirectoryTree


class MyApp(App):
    """An example of a very simple Textual App"""

    async def on_load(self) -> None:
        """Sent before going in to application mode."""

        # Bind our basic keys
        await self.bind("b", "view.toggle('sidebar')", "Toggle sidebar")
        await self.bind("q", "quit", "Quit")

        # Get path to show
        try:
            self.path = sys.argv[1]
        except IndexError:
            self.path = os.path.abspath(
                os.path.join(os.path.basename(__file__), "../../")
            )

    async def on_mount(self) -> None:
        """Call after terminal goes in to application mode"""

        # Create our widgets
        # In this a scroll view for the code and a directory tree
        self.body = ScrollView()
        self.directory = DirectoryTree(self.path, "Code")

        # Dock our widgets
        await self.view.dock(Header(), edge="top")
        await self.view.dock(Footer(), edge="bottom")

        # Note the directory is also in a scroll view
        await self.view.dock(
            ScrollView(self.directory), edge="left", size=48, name="sidebar"
        )
        await self.view.dock(self.body, edge="top")

    async def handle_file_click(self, message: FileClick) -> None:
        """A message sent by the directory tree when a file is clicked."""

        syntax: RenderableType
        try:
            # Construct a Syntax object for the path in the message
            syntax = Syntax.from_path(
                message.path,
                line_numbers=True,
                word_wrap=True,
                indent_guides=True,
                theme="monokai",
            )
        except Exception:
            # Possibly a binary file
            # For demonstration purposes we will show the traceback
            syntax = Traceback(theme="monokai", width=None, show_locals=True)
        self.app.sub_title = os.path.basename(message.path)
        await self.body.update(syntax)


# Run our app class
MyApp.run(title="Code Viewer", log="textual.log")
'''