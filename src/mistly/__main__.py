import os

from string import digits, ascii_lowercase, ascii_uppercase, punctuation
from typing import List

from .genius import Genius
from .song import Song

from rich import box
from rich.align import Align
from rich.panel import Panel
from rich.table import Table
from rich.console import RenderableType
from rich.progress import Progress, SpinnerColumn

from textual import events
from textual.geometry import Offset
from textual.app import App
from textual.widget import Widget, Reactive
from textual.widgets import Placeholder, ScrollView


class Body(Placeholder):
    def __init__(self, contents: List[str] | str,
                 name: str | None = None) -> None:
        super().__init__()
        self.name = name
        self.content = Table.grid(padding=1)
        self.content.add_column()
        if isinstance(contents, list):
            for row in contents:
                self.content.add_row(row)
        elif isinstance(contents, str):
            self.content.add_row(contents)

    def render(self):
        return Panel(
            Align.center(
                self.content, vertical="middle"
            ),
            title=self.name,
            border_style="green" if self.mouse_over else "blue",
            box=box.HEAVY if self.has_focus else box.ROUNDED,
            padding=(1, 2)
        )


class Sidebar(Placeholder):
    def __init__(self, songs: List[Song], name: str | None = None) -> None:
        super().__init__()
        self.name = name
        self.content = Table.grid(padding=1)
        self.content.add_column()
        if songs:
            for song in songs:
                self.content.add_row(
                    f"[bold]{song.title}[/bold]\n{song.artist}"
                )
        self.hrid = 0  # highlighted row id
        self.content.rows[self.hrid].style = "green"

    def render(self):
        return Panel(
            Align.center(
                self.content, vertical="middle"
            ),
            title=self.name,
            border_style="green" if self.mouse_over else "blue",
            box=box.HEAVY if self.has_focus else box.ROUNDED,
            padding=(1, 2),
        )

    async def highlight_next(self):
        self.content.rows[self.hrid].style = "white"
        self.hrid += 1
        if self.hrid == len(self.content.rows):
            self.hrid = 0
        self.content.rows[self.hrid].style = "green"
        self.refresh()

    async def highlight_prev(self):
        self.content.rows[self.hrid].style = "white"
        self.hrid -= 1
        if self.hrid == -1:
            self.hrid = len(self.content.rows) - 1
        self.content.rows[self.hrid].style = "green"
        self.refresh()


class Search(Widget):
    def __init__(self, query: str | None = '', name: str | None = None) -> None:
        super().__init__(name)
        self.query = query
        self.layout_size = 3

    def render(self) -> RenderableType:
        return Panel(
            f"Search: {self.query}",
            border_style="blue",
            box=box.HEAVY
        )

    async def append(self, query: str) -> None:
        self.query += query
        self.refresh()

    async def pop_last(self) -> None:
        self.query = self.query[:-1]
        self.refresh()


class Mistly(App):

    async def on_load(self):
        await self.bind("b", "toggle_sidebar", "Toggle Side Bar")
        await self.bind("/", "toggle_search", "Toggle Search Bar")
        await self.bind("q", "quit", "Quit")

    show_sidebar: Reactive[bool] = Reactive(False)

    async def on_mount(self) -> None:
        token = os.environ["GENIUS_TOKEN"]
        self.genius = Genius(token)

        self.search = Search()
        self.sidebar_renderable = Body(["/ to search"], name="Search Results")
        self.body_renderable = Body("...", name="Lyrics")
        self.sidebar = ScrollView(self.sidebar_renderable)
        self.body = ScrollView(self.body_renderable)

        self.loading_progress = Progress(SpinnerColumn(), "{task.description}")
        self.loading_progress.add_task("[green]Loading")
        
        await self.view.dock(self.search, edge="bottom", name="search")
        await self.view.dock(self.sidebar, edge="left", size=48, name="sidebar")
        await self.view.dock(self.body, edge="left", name="body")
        await self.set_focus(self.search)

    async def update_sidebar(self, query: str) -> None:
        if not query:
            return

        self.songs = self.genius.search(query)
        if self.songs:
            content = "\n\n".join([f"{song.title}\n{song.artist}" for song in self.songs])
        else:
            content = "Nothing found..."
        self.sidebar_renderable = Sidebar(self.songs, name=f"Search Results")
        await self.sidebar.update(self.sidebar_renderable)
        await self.set_focus(self.sidebar_renderable)

    async def update_body(self, song_id: int) -> None:
        if not self.songs:
            return
        if song_id < 0 or song_id >= len(self.songs):
            return

        content = self.songs[song_id].fetch_lyrics()
        self.body_renderable = Body(name=f"{self.songs[song_id].title} Lyrics", contents=content)
        await self.body.update(self.body_renderable)

    async def action_toggle_search(self) -> None:
        await self.view.action_toggle("search")
        if self.focused == self.search:
            self.focused = None
        else:
            await self.search.focus()
            
    async def action_toggle_sidebar(self) -> None:
        await self.view.action_toggle("sidebar")
        self.show_sidebar = not self.show_sidebar
        if self.focused == self.sidebar_renderable:
            await self.set_focus(self.body_renderable)
        else:
            if not self.show_sidebar:
                await self.set_focus(self.sidebar_renderable)

    async def on_event(self, event: events.Event) -> None:
        # Handle input events that haven't been forwarded
        # If the event has been forwarded it may have bubbled up back to the App
        if isinstance(event, events.InputEvent) and not event.is_forwarded:
            if isinstance(event, events.MouseEvent):
                # Record current mouse position on App
                self.mouse_position = Offset(event.x, event.y)
            if isinstance(event, events.Key) and self.focused:
                if self.focused == self.search:
                    if event.key in f" {digits}{ascii_lowercase}{ascii_uppercase}{punctuation}":
                        await self.search.append(f"{event.key}")
                    elif event.key in ["backspace", "ctrl+h"]:
                        await self.search.pop_last()
                    elif event.key == "escape":
                        await self.action_toggle_search()
                        await self.set_focus(self.sidebar_renderable)
                    elif event.key == "enter":
                        with self.loading_progress:
                            await self.action_toggle_search()
                            await self.set_focus(self.sidebar_renderable)
                            await self.update_sidebar(self.search.query)
                            await self.update_body(0)
                elif event.key == "b":
                    await self.action_toggle_sidebar()
                elif event.key in ["q", "ctrl+c"]:
                    await self.shutdown()
                elif event.key == "/":
                    await self.action_toggle_search()
                elif event.key in ["l", "ctrl+f", "right"]:
                    await self.set_focus(self.body_renderable)
                elif event.key in ["h", "ctrl+b", "left"]:
                    if not self.show_sidebar:
                        await self.set_focus(self.sidebar_renderable)
                elif self.focused == self.sidebar_renderable and \
                     isinstance(self.sidebar_renderable, Sidebar):
                    if event.key in ["j", "ctrl+n", "down"]:
                        await self.sidebar_renderable.highlight_next()
                        self.sidebar.scroll_up()
                    elif event.key in ["k", "ctrl+p", "up"]:
                        await self.sidebar_renderable.highlight_prev()
                        self.sidebar.scroll_down()
                    elif event.key in ["enter", "l", "ctrl+f", "right"]:
                        with self.loading_progress:
                            await self.update_body(self.sidebar_renderable.hrid)
                            self.sidebar.refresh()
                elif self.focused == self.body_renderable:
                    if event.key in ["j", "ctrl+n", "down"]:
                        self.body.scroll_up()
                    elif event.key in ["k", "ctrl+p", "up"]:
                        self.body.scroll_down()
                # Key events are sent direct to focused widget
                elif self.bindings.allow_forward(event.key):
                    await self.focused.forward_event(event)
                else:
                    # Key has allow_forward=False which disallows forward to focused widget
                    await super().on_event(event)
            else:
                # Forward the event to the view
                await self.view.forward_event(event)
        else:
            await super().on_event(event)


if __name__ == "__main__":
    Mistly.run()
