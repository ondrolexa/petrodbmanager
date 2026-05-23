from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen, Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    TextArea,
)

if TYPE_CHECKING:
    from textual.app import ComposeResult

_BACK_BINDING = ("escape", "go_back", "Back")


# ── Login ─────────────────────────────────────────────────────────


class LoginScreen(Screen):
    CSS = """
    #login-container {
        align: center middle;
        width: 40;
        padding: 1 2;
    }
    #login-title {
        text-style: bold;
        content-align: center middle;
        height: 3;
    }
    #login-form {
        width: 100%;
    }
    #login-form Input {
        margin-bottom: 1;
    }
    #login-buttons {
        width: 100%;
        height: 3;
    }
    #error-msg {
        color: $error;
        text-style: bold;
        height: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Label("PetroDB Client", id="login-title"),
            Vertical(
                Input(placeholder="Username", id="username"),
                Input(placeholder="Password", id="password", password=True),
                Label("", id="error-msg"),
                Horizontal(
                    Button("Login", id="login-btn", variant="primary"),
                    id="login-buttons",
                ),
                id="login-form",
            ),
            id="login-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#username", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "login-btn":
            self.do_login()

    def on_input_submitted(self) -> None:
        self.do_login()

    def do_login(self) -> None:
        username = self.query_one("#username", Input).value
        password = self.query_one("#password", Input).value
        if not username or not password:
            self.query_one("#error-msg", Label).update("Username and password required")
            return

        api = self.app.api  # ty: ignore

        async def _login() -> None:
            try:
                await api.login(username, password)
            except Exception as e:
                self.query_one("#error-msg", Label).update(str(e))
            else:
                self.app.push_screen(ProjectListScreen())

        self.app.call_later(_login)


# ── Projects ──────────────────────────────────────────────────────


class ProjectListScreen(Screen):
    CSS = """
    Screen { align: center top; }
    #project-title { text-style: bold; height: 3; content-align: center middle; }
    #project-table { width: 80%; height: 1fr; margin: 1 0; }
    #project-actions { width: 80%; height: 3; align: center middle; }
    #refresh-btn { margin: 0 1; }
    #status-msg { height: 1; content-align: center middle; color: $secondary; }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Select a Project", id="project-title")
        yield DataTable(id="project-table", cursor_type="row")
        yield Horizontal(
            Button("Refresh", id="refresh-btn"),
            Button("Open Project", id="open-btn", variant="primary"),
            id="project-actions",
        )
        yield Label("", id="status-msg")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#project-table", DataTable).add_columns(
            "ID", "Name", "Description"
        )
        self._load()

    def _load(self) -> None:
        api = self.app.api  # ty: ignore

        async def _fetch() -> None:
            status = self.query_one("#status-msg", Label)
            try:
                projects = await api.get_projects()
            except Exception as e:
                status.update(f"Error: {e}")
                return
            table = self.query_one("#project-table", DataTable)
            table.clear()
            for p in projects:
                table.add_row(str(p["id"]), p["name"], p.get("description") or "")
            status.update(f"Loaded {len(projects)} project(s)")

        self.app.call_later(_fetch)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "refresh-btn":
            self._load()
        elif event.button.id == "open-btn":
            self._open()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self._open()

    def _open(self) -> None:
        table = self.query_one("#project-table", DataTable)
        row = table.cursor_row
        if row is None:
            self.query_one("#status-msg", Label).update("No project selected")
            return
        values = table.get_row_at(row)
        self.app.push_screen(SampleListScreen(int(values[0]), str(values[1])))


# ── Samples ───────────────────────────────────────────────────────


class SampleListScreen(Screen):
    BINDINGS = [_BACK_BINDING]

    CSS = """
    Screen { align: center top; }
    #sample-title { text-style: bold; height: 3; content-align: center middle; }
    #sample-table { width: 80%; height: 1fr; margin: 1 0; }
    #sample-actions { width: 80%; height: 3; align: center middle; }
    #sample-actions Button { margin: 0 1; }
    #status-msg { height: 1; content-align: center middle; color: $secondary; }
    """

    def __init__(self, project_id: int, project_name: str) -> None:
        super().__init__()
        self._pid = project_id
        self._pname = project_name

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label(f"Samples in {self._pname}", id="sample-title")
        yield DataTable(id="sample-table", cursor_type="row")
        yield Horizontal(
            Button("New", id="new-btn"),
            Button("Open", id="open-btn", variant="primary"),
            Button("Edit", id="edit-btn"),
            Button("Delete", id="delete-btn", variant="error"),
            Button("Back", id="back-btn"),
            id="sample-actions",
        )
        yield Label("", id="status-msg")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#sample-table", DataTable).add_columns(
            "ID", "Name", "Description"
        )
        self._load()

    def _load(self) -> None:
        api = self.app.api  # ty: ignore

        async def _fetch() -> None:
            status = self.query_one("#status-msg", Label)
            try:
                items = await api.get_samples(self._pid)
            except Exception as e:
                status.update(f"Error: {e}")
                return
            table = self.query_one("#sample-table", DataTable)
            table.clear()
            for s in items:
                table.add_row(str(s["id"]), s["name"], s.get("description") or "")
            status.update(f"Loaded {len(items)} sample(s)")

        self.app.call_later(_fetch)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self._open()

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn = event.button.id
        if btn == "new-btn":
            self._new()
        elif btn == "open-btn":
            self._open()
        elif btn == "edit-btn":
            self._edit()
        elif btn == "delete-btn":
            self._delete()
        elif btn == "back-btn":
            self.app.pop_screen()

    def _selected(self) -> tuple[int, str, str] | None:
        table = self.query_one("#sample-table", DataTable)
        row = table.cursor_row
        if row is None:
            self.query_one("#status-msg", Label).update("No sample selected")
            return None
        values = table.get_row_at(row)
        return int(values[0]), str(values[1]), str(values[2])

    def _refresh(self) -> None:
        self._load()

    def _new(self) -> None:
        def on_result(result: tuple[str, str] | None) -> None:
            if result is None:
                return
            name, description = result
            api = self.app.api  # ty: ignore

            async def _create() -> None:
                try:
                    await api.create_sample(self._pid, name, description or None)
                except Exception as e:
                    self.query_one("#status-msg", Label).update(f"Error: {e}")
                    return
                self._refresh()

            self.app.call_later(_create)

        self.app.push_screen(SampleFormScreen(), on_result)

    def _open(self) -> None:
        sel = self._selected()
        if sel is None:
            return
        sid, sname, sdesc = sel
        self.app.push_screen(SampleScreen(self._pid, self._pname, sid, sname, sdesc))

    def _edit(self) -> None:
        sel = self._selected()
        if sel is None:
            return
        sid, sname, sdesc = sel

        def on_result(result: tuple[str, str] | None) -> None:
            if result is None:
                return
            name, description = result
            api = self.app.api  # ty: ignore

            async def _update() -> None:
                try:
                    await api.update_sample(self._pid, sid, name, description or None)
                except Exception as e:
                    self.query_one("#status-msg", Label).update(f"Error: {e}")
                    return
                self._refresh()

            self.app.call_later(_update)

        self.app.push_screen(SampleFormScreen(name=sname, description=sdesc), on_result)

    def _delete(self) -> None:
        sel = self._selected()
        if sel is None:
            return
        sid, sname, _ = sel

        def on_confirm(confirmed: bool) -> None:
            if not confirmed:
                return
            api = self.app.api  # ty: ignore

            async def _delete() -> None:
                try:
                    await api.delete_sample(self._pid, sid)
                except Exception as e:
                    self.query_one("#status-msg", Label).update(f"Error: {e}")
                    return
                self._refresh()

            self.app.call_later(_delete)

        self.app.push_screen(  # ty: ignore
            ConfirmScreen(f"Delete sample '{sname}'?"), on_confirm
        )


class SampleFormScreen(ModalScreen[tuple[str, str] | None]):
    CSS = """
    #dialog { width: 50; height: auto; padding: 1 2;
              border: thick $border; background: $surface; align: center middle; }
    #form-title { text-style: bold; height: 3; content-align: center middle; }
    #form-fields Input { margin-bottom: 1; }
    #form-buttons { height: 3; align: center middle; }
    #form-buttons Button { margin: 0 1; }
    #form-error { height: 1; color: $error; }
    """

    def __init__(self, name: str = "", description: str = "") -> None:
        super().__init__()
        self._name = name
        self._description = description
        self._editing = bool(name)

    def compose(self) -> ComposeResult:
        title = "Edit Sample" if self._editing else "New Sample"
        yield Vertical(
            Label(title, id="form-title"),
            Vertical(
                Input(value=self._name, placeholder="Sample name", id="fname"),
                Input(
                    value=self._description,
                    placeholder="Description (optional)",
                    id="fdesc",
                ),
                Label("", id="form-error"),
                id="form-fields",
            ),
            Horizontal(
                Button("Cancel", id="cancel-btn"),
                Button("Save", id="save-btn", variant="primary"),
                id="form-buttons",
            ),
            id="dialog",
        )

    def on_mount(self) -> None:
        self.query_one("#fname", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel-btn":
            self.dismiss(None)
        elif event.button.id == "save-btn":
            name = self.query_one("#fname", Input).value.strip()
            desc = self.query_one("#fdesc", Input).value.strip()
            if not name:
                self.query_one("#form-error", Label).update("Name is required")
                return
            self.dismiss((name, desc))


# ── Sample detail / component navigation ─────────────────────────


class SampleScreen(Screen):
    BINDINGS = [_BACK_BINDING]

    CSS = """
    Screen { align: center middle; }
    #sample-title { text-style: bold; content-align: center middle; height: 3; }
    #sample-detail { width: 60; height: auto; margin-bottom: 1; }
    #sample-detail Label { padding: 0 1; }
    #value-label { color: $text-muted; }
    #nav-main, #nav-secondary { width: 60; height: auto; align: center middle; }
    #nav-main Button, #nav-secondary Button { margin: 0 1; }
    #status-msg { height: 1; content-align: center middle; color: $secondary; }
    """

    def __init__(
        self,
        project_id: int,
        project_name: str,
        sample_id: int,
        sample_name: str,
        sample_description: str,
    ) -> None:
        super().__init__()
        self._pid = project_id
        self._pname = project_name
        self._sid = sample_id
        self._sname = sample_name
        self._sdesc = sample_description

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label(f"Sample: {self._sname}", id="sample-title")
        yield Vertical(
            Label(f"ID: {self._sid}"),
            Label(f"Project: {self._pname}"),
            Label("Description:") if self._sdesc else Label(),
            Label(f" {self._sdesc}") if self._sdesc else Label(),
            id="sample-detail",
        )
        yield Horizontal(
            Button("Spots", id="spots-btn", variant="primary"),
            Button("Areas", id="areas-btn", variant="primary"),
            Button("Profiles", id="profiles-btn", variant="primary"),
            id="nav-main",
        )
        yield Horizontal(
            Button("Edit Sample", id="edit-btn"),
            Button("Delete Sample", id="delete-btn", variant="error"),
            Button("Back", id="back-btn"),
            id="nav-secondary",
        )
        yield Label("", id="status-msg")
        yield Footer()

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn = event.button.id
        if btn == "spots-btn":
            self.app.push_screen(SpotListScreen(self._pid, self._sid, self._sname))
        elif btn == "areas-btn":
            self.app.push_screen(AreaListScreen(self._pid, self._sid, self._sname))
        elif btn == "profiles-btn":
            self.app.push_screen(ProfileListScreen(self._pid, self._sid, self._sname))
        elif btn == "edit-btn":
            self._edit()
        elif btn == "delete-btn":
            self._delete()
        elif btn == "back-btn":
            self.app.pop_screen()

    def _edit(self) -> None:
        def on_result(result: tuple[str, str] | None) -> None:
            if result is None:
                return
            name, description = result
            api = self.app.api  # ty: ignore

            async def _update() -> None:
                try:
                    await api.update_sample(
                        self._pid, self._sid, name, description or None
                    )
                except Exception as e:
                    self.query_one("#status-msg", Label).update(f"Error: {e}")
                    return
                self._sname = name
                self._sdesc = description
                self.query_one("#sample-title", Label).update(f"Sample: {name}")
                detail = self.query_one("#sample-detail", Vertical)
                await detail.remove_children()
                await detail.mount(Label(f"ID: {self._sid}"))
                await detail.mount(Label(f"Project: {self._pname}"))
                if description:
                    await detail.mount(Label("Description:"))
                    await detail.mount(Label(f" {description}"))

            self.app.call_later(_update)

        self.app.push_screen(
            SampleFormScreen(name=self._sname, description=self._sdesc), on_result
        )

    def _delete(self) -> None:
        def on_confirm(confirmed: bool) -> None:
            if not confirmed:
                return
            api = self.app.api  # ty: ignore

            async def _delete() -> None:
                try:
                    await api.delete_sample(self._pid, self._sid)
                except Exception as e:
                    self.query_one("#status-msg", Label).update(f"Error: {e}")
                    return
                self.app.pop_screen()

            self.app.call_later(_delete)

        self.app.push_screen(  # ty: ignore
            ConfirmScreen(f"Delete sample '{self._sname}'?"), on_confirm
        )


# ── Generic entity list screen ────────────────────────────────────


class _EntityListScreen(Screen):
    BINDINGS = [_BACK_BINDING]
    ENTITY_TITLE = ""
    ENTITY_COLUMNS: list[tuple[str, str, str]] = []
    HAS_OPEN = False
    FORM_SCREEN = None

    def __init__(
        self,
        project_id: int,
        sample_id: int,
        sample_name: str,
        profile_id: int | None = None,
    ) -> None:
        super().__init__()
        self._pid = project_id
        self._sid = sample_id
        self._sname = sample_name
        self._profile_id = profile_id

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label(f"{self.ENTITY_TITLE} in {self._sname}", id="entity-title")
        yield DataTable(id="entity-table", cursor_type="row")
        actions = [("New", "new-btn")]
        if self.HAS_OPEN:
            actions.append(("Open", "open-btn", "primary"))  # ty: ignore
        actions.append(("Edit", "edit-btn"))
        actions.append(("Delete", "delete-btn", "error"))  # ty: ignore
        actions.append(("Back", "back-btn"))
        yield Horizontal(
            *(
                Button(label=label, id=btn_id, variant=variant)
                for label, btn_id, *rest in actions
                for variant in (rest[0] if rest else "default",)
            ),
            id="entity-actions",
        )
        yield Label("", id="status-msg")
        yield Footer()

    CSS = """
    #entity-title { text-style: bold; height: 3; content-align: center middle; }
    #entity-table { width: 80%; height: 1fr; margin: 1 0; }
    #entity-actions { width: 80%; height: 3; align: center middle; }
    #entity-actions Button { margin: 0 1; }
    #status-msg { height: 1; content-align: center middle; color: $secondary; }
    """

    def on_mount(self) -> None:
        self.query_one("#entity-table", DataTable).add_columns(
            *[c[0] for c in self.ENTITY_COLUMNS]
        )
        self._load()  # ty: ignore

    def _selected(self) -> list[str] | None:
        table = self.query_one("#entity-table", DataTable)
        row = table.cursor_row
        if row is None:
            self.query_one("#status-msg", Label).update("No item selected")
            return None
        return [str(v) for v in table.get_row_at(row)]

    def _refresh(self) -> None:
        self._load()  # ty: ignore

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn = event.button.id
        if btn == "new-btn":
            self._new()
        elif btn == "edit-btn":
            self._edit()
        elif btn == "delete-btn":
            self._delete()
        elif btn == "back-btn":
            self.app.pop_screen()

    def _new(self) -> None:
        raise NotImplementedError

    def _edit(self) -> None:
        raise NotImplementedError

    def _delete(self) -> None:
        raise NotImplementedError


# ── Spots ─────────────────────────────────────────────────────────


def _parse_values(text: str) -> dict:
    d: dict = {}
    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if "=" in line:
            k, _, v = line.partition("=")
            k = k.strip()
            v = v.strip()
        else:
            parts = line.split(None, 1)
            if len(parts) != 2:
                continue
            k, v = parts
        try:
            d[k] = float(v)
        except ValueError:
            d[k] = v
    return d


def _format_values(d: dict) -> str:
    return "\n".join(f"{k} = {v}" for k, v in d.items())


class SpotListScreen(_EntityListScreen):
    ENTITY_TITLE = "Spots"
    ENTITY_COLUMNS = [
        ("ID", "id", "4"),
        ("Label", "label", "20"),
        ("Mineral", "mineral", "14"),
        ("Values", "values", "10"),
    ]

    def _load(self) -> None:
        api = self.app.api  # ty: ignore

        async def _fetch() -> None:
            status = self.query_one("#status-msg", Label)
            try:
                items = await api.get_spots(self._pid, self._sid)
            except Exception as e:
                status.update(f"Error: {e}")
                return
            table = self.query_one("#entity-table", DataTable)
            table.clear()
            for s in items:
                table.add_row(
                    str(s["id"]),
                    s["label"],
                    s.get("mineral") or "",
                    str(len(s.get("values", {}))),
                )
            status.update(f"Loaded {len(items)} spot(s)")

        self.app.call_later(_fetch)

    def _new(self) -> None:
        def on_result(result: dict | None) -> None:
            if result is None:
                return
            api = self.app.api  # ty: ignore

            async def _create() -> None:
                try:
                    await api.create_spot(
                        self._pid,
                        self._sid,
                        result["label"],
                        result.get("mineral"),
                        result.get("__values__"),
                    )
                except Exception as e:
                    self.query_one("#status-msg", Label).update(f"Error: {e}")
                    return
                self._refresh()

            self.app.call_later(_create)

        self.app.push_screen(
            EntityFormScreen(
                "New Spot",
                [("label", "Label", "str", True), ("mineral", "Mineral", "str", False)],
                has_values=True,
            ),
            on_result,
        )

    def _edit(self) -> None:
        sel = self._selected()
        if sel is None:
            return
        spot_id = int(sel[0])
        api = self.app.api  # ty: ignore

        async def _fetch() -> None:
            try:
                spot = await api.get_spot(self._pid, self._sid, spot_id)
            except Exception as e:
                self.query_one("#status-msg", Label).update(f"Error: {e}")
                return

            def on_result(result: dict | None) -> None:
                if result is None:
                    return

                async def _update() -> None:
                    try:
                        await api.update_spot(
                            self._pid,
                            self._sid,
                            spot_id,
                            result["label"],
                            result.get("mineral"),
                            result.get("__values__"),
                        )
                    except Exception as e:
                        self.query_one("#status-msg", Label).update(f"Error: {e}")
                        return
                    self._refresh()

                self.app.call_later(_update)

            self.app.push_screen(
                EntityFormScreen(
                    "Edit Spot",
                    [
                        ("label", "Label", "str", True),
                        ("mineral", "Mineral", "str", False),
                    ],
                    has_values=True,
                    initial={
                        "label": spot["label"],
                        "mineral": spot.get("mineral") or "",
                        "__values__": spot.get("values", {}),
                    },
                ),
                on_result,
            )

        self.app.call_later(_fetch)

    def _delete(self) -> None:
        sel = self._selected()
        if sel is None:
            return
        spot_id = int(sel[0])
        label = sel[1]

        def on_confirm(confirmed: bool) -> None:
            if not confirmed:
                return
            api = self.app.api  # ty: ignore

            async def _delete() -> None:
                try:
                    await api.delete_spot(self._pid, self._sid, spot_id)
                except Exception as e:
                    self.query_one("#status-msg", Label).update(f"Error: {e}")
                    return
                self._refresh()

            self.app.call_later(_delete)

        self.app.push_screen(  # ty: ignore
            ConfirmScreen(f"Delete spot '{label}'?"), on_confirm
        )


# ── Areas ─────────────────────────────────────────────────────────


class AreaListScreen(_EntityListScreen):
    ENTITY_TITLE = "Areas"
    ENTITY_COLUMNS = [
        ("ID", "id", "4"),
        ("Label", "label", "20"),
        ("Values", "values", "10"),
    ]

    def _load(self) -> None:
        api = self.app.api  # ty: ignore

        async def _fetch() -> None:
            status = self.query_one("#status-msg", Label)
            try:
                items = await api.get_areas(self._pid, self._sid)
            except Exception as e:
                status.update(f"Error: {e}")
                return
            table = self.query_one("#entity-table", DataTable)
            table.clear()
            for a in items:
                table.add_row(str(a["id"]), a["label"], str(len(a.get("values", {}))))
            status.update(f"Loaded {len(items)} area(s)")

        self.app.call_later(_fetch)

    def _new(self) -> None:
        def on_result(result: dict | None) -> None:
            if result is None:
                return
            api = self.app.api  # ty: ignore

            async def _create() -> None:
                try:
                    await api.create_area(
                        self._pid, self._sid, result["label"], result.get("__values__")
                    )
                except Exception as e:
                    self.query_one("#status-msg", Label).update(f"Error: {e}")
                    return
                self._refresh()

            self.app.call_later(_create)

        self.app.push_screen(
            EntityFormScreen(
                "New Area", [("label", "Label", "str", True)], has_values=True
            ),
            on_result,
        )

    def _edit(self) -> None:
        sel = self._selected()
        if sel is None:
            return
        area_id = int(sel[0])
        api = self.app.api  # ty: ignore

        async def _fetch() -> None:
            try:
                area = await api.get_area(self._pid, self._sid, area_id)
            except Exception as e:
                self.query_one("#status-msg", Label).update(f"Error: {e}")
                return

            def on_result(result: dict | None) -> None:
                if result is None:
                    return

                async def _update() -> None:
                    try:
                        await api.update_area(
                            self._pid,
                            self._sid,
                            area_id,
                            result["label"],
                            result.get("__values__"),
                        )
                    except Exception as e:
                        self.query_one("#status-msg", Label).update(f"Error: {e}")
                        return
                    self._refresh()

                self.app.call_later(_update)

            self.app.push_screen(
                EntityFormScreen(
                    "Edit Area",
                    [("label", "Label", "str", True)],
                    has_values=True,
                    initial={
                        "label": area["label"],
                        "__values__": area.get("values", {}),
                    },
                ),
                on_result,
            )

        self.app.call_later(_fetch)

    def _delete(self) -> None:
        sel = self._selected()
        if sel is None:
            return
        area_id = int(sel[0])
        label = sel[1]

        def on_confirm(confirmed: bool) -> None:
            if not confirmed:
                return
            api = self.app.api  # ty: ignore

            async def _delete() -> None:
                try:
                    await api.delete_area(self._pid, self._sid, area_id)
                except Exception as e:
                    self.query_one("#status-msg", Label).update(f"Error: {e}")
                    return
                self._refresh()

            self.app.call_later(_delete)

        self.app.push_screen(  # ty: ignore
            ConfirmScreen(f"Delete area '{label}'?"), on_confirm
        )


# ── Profiles ──────────────────────────────────────────────────────


class ProfileListScreen(_EntityListScreen):
    ENTITY_TITLE = "Profiles"
    ENTITY_COLUMNS = [
        ("ID", "id", "4"),
        ("Label", "label", "20"),
        ("Mineral", "mineral", "14"),
    ]
    HAS_OPEN = True

    def _load(self) -> None:
        api = self.app.api  # ty: ignore

        async def _fetch() -> None:
            status = self.query_one("#status-msg", Label)
            try:
                items = await api.get_profiles(self._pid, self._sid)
            except Exception as e:
                status.update(f"Error: {e}")
                return
            table = self.query_one("#entity-table", DataTable)
            table.clear()
            for p in items:
                table.add_row(str(p["id"]), p["label"], p.get("mineral") or "")
            status.update(f"Loaded {len(items)} profile(s)")

        self.app.call_later(_fetch)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self._open()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "open-btn":
            self._open()
        else:
            super().on_button_pressed(event)

    def _open(self) -> None:
        sel = self._selected()
        if sel is None:
            return
        profile_id = int(sel[0])
        self.app.push_screen(
            ProfileSpotListScreen(self._pid, self._sid, self._sname, profile_id)
        )

    def _new(self) -> None:
        def on_result(result: dict | None) -> None:
            if result is None:
                return
            api = self.app.api  # ty: ignore

            async def _create() -> None:
                try:
                    await api.create_profile(
                        self._pid, self._sid, result["label"], result.get("mineral")
                    )
                except Exception as e:
                    self.query_one("#status-msg", Label).update(f"Error: {e}")
                    return
                self._refresh()

            self.app.call_later(_create)

        self.app.push_screen(
            EntityFormScreen(
                "New Profile",
                [("label", "Label", "str", True), ("mineral", "Mineral", "str", False)],
            ),
            on_result,
        )

    def _edit(self) -> None:
        sel = self._selected()
        if sel is None:
            return
        profile_id = int(sel[0])
        api = self.app.api  # ty: ignore

        async def _fetch() -> None:
            try:
                profile = await api.get_profile(self._pid, self._sid, profile_id)
            except Exception as e:
                self.query_one("#status-msg", Label).update(f"Error: {e}")
                return

            def on_result(result: dict | None) -> None:
                if result is None:
                    return

                async def _update() -> None:
                    try:
                        await api.update_profile(
                            self._pid,
                            self._sid,
                            profile_id,
                            result["label"],
                            result.get("mineral"),
                        )
                    except Exception as e:
                        self.query_one("#status-msg", Label).update(f"Error: {e}")
                        return
                    self._refresh()

                self.app.call_later(_update)

            self.app.push_screen(
                EntityFormScreen(
                    "Edit Profile",
                    [
                        ("label", "Label", "str", True),
                        ("mineral", "Mineral", "str", False),
                    ],
                    initial={
                        "label": profile["label"],
                        "mineral": profile.get("mineral") or "",
                    },
                ),
                on_result,
            )

        self.app.call_later(_fetch)

    def _delete(self) -> None:
        sel = self._selected()
        if sel is None:
            return
        profile_id = int(sel[0])
        label = sel[1]

        def on_confirm(confirmed: bool) -> None:
            if not confirmed:
                return
            api = self.app.api  # ty: ignore

            async def _delete() -> None:
                try:
                    await api.delete_profile(self._pid, self._sid, profile_id)
                except Exception as e:
                    self.query_one("#status-msg", Label).update(f"Error: {e}")
                    return
                self._refresh()

            self.app.call_later(_delete)

        self.app.push_screen(  # ty: ignore
            ConfirmScreen(f"Delete profile '{label}'?"), on_confirm
        )


# ── Profile Spots ─────────────────────────────────────────────────


class ProfileSpotListScreen(_EntityListScreen):
    ENTITY_TITLE = "Profile Spots"
    ENTITY_COLUMNS = [
        ("ID", "id", "4"),
        ("Index", "index", "10"),
        ("Values", "values", "10"),
    ]

    def __init__(
        self, project_id: int, sample_id: int, sample_name: str, profile_id: int
    ) -> None:
        super().__init__(project_id, sample_id, sample_name, profile_id)

    def _load(self) -> None:
        api = self.app.api  # ty: ignore

        async def _fetch() -> None:
            status = self.query_one("#status-msg", Label)
            try:
                items = await api.get_profile_spots(
                    self._pid, self._sid, self._profile_id
                )
            except Exception as e:
                status.update(f"Error: {e}")
                return
            table = self.query_one("#entity-table", DataTable)
            table.clear()
            for ps in items:
                table.add_row(
                    str(ps["id"]), str(ps["index"]), str(len(ps.get("values", {})))
                )
            status.update(f"Loaded {len(items)} profile spot(s)")

        self.app.call_later(_fetch)

    def _new(self) -> None:
        def on_result(result: dict | None) -> None:
            if result is None:
                return
            api = self.app.api  # ty: ignore

            async def _create() -> None:
                try:
                    await api.create_profile_spot(
                        self._pid,
                        self._sid,
                        self._profile_id,
                        int(result["index"]),
                        result.get("__values__"),
                    )
                except Exception as e:
                    self.query_one("#status-msg", Label).update(f"Error: {e}")
                    return
                self._refresh()

            self.app.call_later(_create)

        self.app.push_screen(
            EntityFormScreen(
                "New Profile Spot", [("index", "Index", "int", True)], has_values=True
            ),
            on_result,
        )

    def _edit(self) -> None:
        sel = self._selected()
        if sel is None:
            return
        spot_id = int(sel[0])
        api = self.app.api  # ty: ignore

        async def _fetch() -> None:
            try:
                ps = await api.get_profile_spot(
                    self._pid, self._sid, self._profile_id, spot_id
                )
            except Exception as e:
                self.query_one("#status-msg", Label).update(f"Error: {e}")
                return

            def on_result(result: dict | None) -> None:
                if result is None:
                    return

                async def _update() -> None:
                    try:
                        await api.update_profile_spot(
                            self._pid,
                            self._sid,
                            self._profile_id,
                            spot_id,
                            int(result["index"]),
                            result.get("__values__"),
                        )
                    except Exception as e:
                        self.query_one("#status-msg", Label).update(f"Error: {e}")
                        return
                    self._refresh()

                self.app.call_later(_update)

            self.app.push_screen(
                EntityFormScreen(
                    "Edit Profile Spot",
                    [("index", "Index", "int", True)],
                    has_values=True,
                    initial={
                        "index": str(ps["index"]),
                        "__values__": ps.get("values", {}),
                    },
                ),
                on_result,
            )

        self.app.call_later(_fetch)

    def _delete(self) -> None:
        sel = self._selected()
        if sel is None:
            return
        spot_id = int(sel[0])
        idx = sel[1]

        def on_confirm(confirmed: bool) -> None:
            if not confirmed:
                return
            api = self.app.api  # ty: ignore

            async def _delete() -> None:
                try:
                    await api.delete_profile_spot(
                        self._pid, self._sid, self._profile_id, spot_id
                    )
                except Exception as e:
                    self.query_one("#status-msg", Label).update(f"Error: {e}")
                    return
                self._refresh()

            self.app.call_later(_delete)

        self.app.push_screen(  # ty: ignore
            ConfirmScreen(f"Delete profile spot #{idx}?"), on_confirm
        )


# ── Generic entity form (with optional values dict) ───────────────


class EntityFormScreen(ModalScreen[dict | None]):
    BINDINGS = [("escape", "cancel", "Cancel")]

    CSS = """
    Screen { align: center top; padding: 1 0; }
    #dialog { width: 60; padding: 0 2;
              border: thick $border; background: $surface; }
    #form-title { text-style: bold; height: 1; content-align: center middle; }
    #form-scroll { width: 100%; height: auto; max-height: 22; overflow-y: auto; }
    #form-scroll Input { margin-bottom: 1; }
    #form-buttons { height: 3; align: center middle; }
    #form-buttons Button { margin: 0 1; }
    #form-error { height: 1; color: $error; }
    #values-label { text-style: bold; margin-top: 1; margin-bottom: 0; }
    #ef-__values__ { width: 100%; height: 12; margin-bottom: 1; }
    """

    def __init__(
        self,
        title: str,
        fields: list[tuple[str, str, str, bool]],
        has_values: bool = False,
        initial: dict | None = None,
    ) -> None:
        super().__init__()
        self._title = title
        self._fields = fields
        self._has_values = has_values
        self._initial = initial or {}

    def compose(self) -> ComposeResult:
        children: list = []
        for fid, flabel, ftype, freq in self._fields:
            val = str(self._initial.get(fid, ""))
            placeholder = f"{flabel}" + (" (required)" if freq else " (optional)")
            children.append(Input(value=val, placeholder=placeholder, id=f"ef-{fid}"))

        if self._has_values:
            children.append(
                Label("Values (key = value, one per line)", id="values-label")
            )
            vals = self._initial.get("__values__", {})
            val_text = _format_values(vals) if isinstance(vals, dict) else ""
            children.append(TextArea(val_text, id="ef-__values__"))

        yield Vertical(
            Label(self._title, id="form-title"),
            Vertical(*children, id="form-scroll"),
            Label("", id="form-error"),
            Horizontal(
                Button("Cancel", id="cancel-btn"),
                Button("Save", id="save-btn", variant="primary"),
                id="form-buttons",
            ),
            id="dialog",
        )

    def on_mount(self) -> None:
        if self._fields:
            self.query_one(f"#ef-{self._fields[0][0]}", Input).focus()

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel-btn":
            self.dismiss(None)
        elif event.button.id == "save-btn":
            self._save()

    def _save(self) -> None:
        result: dict = {}
        for fid, flabel, ftype, freq in self._fields:
            val = self.query_one(f"#ef-{fid}", Input).value.strip()
            if freq and not val:
                self.query_one("#form-error", Label).update(f"{flabel} is required")
                return
            if ftype == "int":
                if val:
                    try:
                        result[fid] = int(val)
                    except ValueError:
                        self.query_one("#form-error", Label).update(
                            f"{flabel} must be an integer"
                        )
                        return
                else:
                    result[fid] = 0
            else:
                result[fid] = val

        if self._has_values:
            text = self.query_one("#ef-__values__", TextArea).text
            result["__values__"] = _parse_values(text) if text.strip() else {}

        self.dismiss(result)


# ── Confirm dialog ────────────────────────────────────────────────


class ConfirmScreen(ModalScreen[bool]):
    BINDINGS = [("escape", "cancel", "Cancel")]

    CSS = """
    Screen { align: center top; padding: 1 0; }
    #confirm-dialog { width: 50; height: auto; padding: 0 2;
                      border: thick $error; background: $surface; }
    #confirm-msg { height: 1; content-align: center middle; text-style: bold; }
    #confirm-buttons { height: 3; align: center middle; }
    #confirm-buttons Button { margin: 0 1; }
    """

    def __init__(self, message: str) -> None:
        super().__init__()
        self._message = message

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label(self._message, id="confirm-msg"),
            Horizontal(
                Button("Cancel", id="no-btn"),
                Button("Confirm", id="yes-btn", variant="error"),
                id="confirm-buttons",
            ),
            id="confirm-dialog",
        )

    def action_cancel(self) -> None:
        self.dismiss(False)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "yes-btn")
