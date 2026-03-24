#!/usr/bin/env python3
"""
Hyprland Keybindings Overlay — daemon

Show with: kill -SIGUSR1 $(pgrep -f keybinds-viewer.py)
Hide with: kill -SIGUSR2 $(pgrep -f keybinds-viewer.py)
"""

import fcntl
import os
import re
import signal
import sys

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
from gi.repository import GLib, Gdk, Gio, Gtk, Pango

BINDS_FILE   = os.path.expanduser('~/.config/hypr/config/binds.conf')
HYPRLAND_CONF = os.path.expanduser('~/.config/hypr/hyprland.conf')
LOCK_FILE    = '/tmp/hypr-keybinds-viewer.lock'

# ── single-instance lock ──────────────────────────────────────────────────────

_lock_fh = open(LOCK_FILE, 'w')
try:
    fcntl.flock(_lock_fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
except IOError:
    sys.exit(0)   # already running

# ── parsing ───────────────────────────────────────────────────────────────────

def _load_variables(*paths):
    """Collect $VAR = value lines from config files."""
    variables: dict[str, str] = {}
    for path in paths:
        try:
            with open(path) as f:
                for line in f:
                    m = re.match(r'^\s*\$(\w+)\s*=\s*(.+)', line)
                    if m:
                        variables[m.group(1)] = m.group(2).strip()
        except OSError:
            pass
    return variables


def _resolve_vars(text: str, variables: dict[str, str]) -> str:
    """Replace $VAR references; longest names first to avoid partial matches."""
    for name in sorted(variables, key=len, reverse=True):
        text = text.replace(f'${name}', variables[name])
    return text


def _normalize_mods(mods: str) -> str:
    """
    Normalise modifier strings for display:
      'SUPER_SHIFT'  → 'SUPER + SHIFT'
      'SUPER SHIFT'  → 'SUPER + SHIFT'
      ''             → '(none)'
    """
    mods = mods.strip()
    if not mods:
        return '(none)'
    parts = [p for p in re.split(r'[_\s]+', mods) if p]
    return ' + '.join(parts)


def parse_binds(variables: dict[str, str]) -> list[tuple]:
    """
    Returns list of (category, bind_type, mods, key, action, args).
    Categories are inferred from box-drawing comment headers.
    """
    results = []
    current_category = 'General'

    # ╔══ Section ══╗  (top-level section headers)
    re_section = re.compile(r'#\s*[║╔╚]\s*(.+?)\s*[║╗╝]')
    # ╭── Category ──╮  (subcategory headers)
    re_category = re.compile(r'#\s*[│╰╭]\s*(.+?)\s*[│╯╮]')
    # bind / binde / bindr / bindm / bindl / bindle / bindlr
    re_bind = re.compile(
        r'^\s*(bind[emrldl]*)\s*=\s*([^,#]*),\s*([^,#]*),\s*([^,#]*),?\s*(.*)'
    )

    try:
        with open(BINDS_FILE) as f:
            for raw_line in f:
                line = raw_line.rstrip()

                m = re_section.search(line)
                if m:
                    current_category = m.group(1).strip()
                    continue

                m = re_category.search(line)
                if m:
                    current_category = m.group(1).strip()
                    continue

                m = re_bind.match(line)
                if m:
                    bind_type, mods, key, action, args = m.groups()
                    mods   = _normalize_mods(_resolve_vars(mods.strip(), variables))
                    key    = key.strip()
                    action = action.strip()
                    args   = re.sub(r'\s*#.*$', '', args).strip()  # drop inline comments
                    results.append((current_category, bind_type, mods, key, action, args))
    except OSError:
        pass

    return results

# ── CSS ───────────────────────────────────────────────────────────────────────

_CSS = b"""
window {
    background-color: rgba(12, 13, 22, 0.96);
}
.titlebar {
    padding: 10px 16px 8px;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    background-color: rgba(255,255,255,0.03);
}
.titlebar label {
    font-size: 14px;
    font-weight: bold;
    color: #c8d0f0;
}
.col-header {
    padding: 4px 8px;
    border-bottom: 1px solid rgba(255,255,255,0.12);
    background-color: rgba(255,255,255,0.04);
}
.col-header label {
    font-size: 10px;
    font-weight: bold;
    color: #556677;
    letter-spacing: 0.5px;
}
.cat-row {
    padding: 5px 16px 3px;
    background-color: rgba(80,100,180,0.12);
    border-top: 1px solid rgba(80,100,180,0.2);
    margin-top: 2px;
}
.cat-row label {
    font-size: 10px;
    font-weight: bold;
    color: #7788bb;
    letter-spacing: 0.8px;
}
.bind-row {
    padding: 3px 8px;
    border-bottom: 1px solid rgba(255,255,255,0.03);
}
.bind-row:hover {
    background-color: rgba(255,255,255,0.04);
}
.t-type {
    font-size: 10px;
    color: #445566;
    font-family: monospace;
}
.t-mods {
    font-size: 11px;
    font-weight: bold;
    color: #99aacc;
    font-family: monospace;
}
.t-key {
    font-size: 11px;
    color: #ddbb88;
    font-family: monospace;
    background-color: rgba(255,255,255,0.07);
    border-radius: 3px;
    padding: 0px 5px;
}
.t-action {
    font-size: 11px;
    color: #88bb88;
    font-family: monospace;
}
.t-args {
    font-size: 10px;
    color: #667788;
    font-family: monospace;
}
"""

# ── window ────────────────────────────────────────────────────────────────────

class KeybindsWindow(Gtk.ApplicationWindow):
    # column widths  (type, mods, key, action)
    _WIDTHS = (48, 170, 110, 130)

    def __init__(self, app: Gtk.Application):
        super().__init__(application=app)
        self.set_title("Hyprland Keybindings")
        self.set_default_size(1100, 660)
        self.set_decorated(False)
        self.set_resizable(False)

        self._rebuild_timer: int | None = None

        self._apply_css()
        self._build_layout()
        self._setup_file_monitor()
        self.rebuild()

        self.set_visible(False)

    # ── CSS ──

    def _apply_css(self):
        provider = Gtk.CssProvider()
        provider.load_from_data(_CSS)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    # ── layout skeleton ──

    def _build_layout(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_child(root)

        # title bar
        titlebar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        titlebar.add_css_class("titlebar")
        lbl = Gtk.Label(label="  Hyprland Keybindings")
        lbl.set_halign(Gtk.Align.START)
        titlebar.append(lbl)
        root.append(titlebar)

        # column header
        root.append(self._make_header_row())

        # scrollable content area
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        root.append(scroll)

        self._content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        scroll.set_child(self._content)

    def _make_header_row(self) -> Gtk.Box:
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        row.add_css_class("col-header")
        for text, width in zip(
            ("TYPE", "MODIFIERS", "KEY", "ACTION", "ARGUMENTS"),
            (*self._WIDTHS, -1),
        ):
            lbl = Gtk.Label(label=text)
            lbl.set_halign(Gtk.Align.START)
            lbl.set_xalign(0.0)
            if width > 0:
                lbl.set_size_request(width, -1)
            else:
                lbl.set_hexpand(True)
            row.append(lbl)
        return row

    # ── content builder ──

    def rebuild(self):
        # clear
        child = self._content.get_first_child()
        while child:
            nxt = child.get_next_sibling()
            self._content.remove(child)
            child = nxt

        variables = _load_variables(HYPRLAND_CONF, BINDS_FILE)
        binds     = parse_binds(variables)

        last_cat: str | None = None
        for category, bind_type, mods, key, action, args in binds:
            if category != last_cat:
                self._content.append(self._make_cat_row(category))
                last_cat = category
            self._content.append(self._make_bind_row(bind_type, mods, key, action, args))

    def _make_cat_row(self, category: str) -> Gtk.Box:
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        row.add_css_class("cat-row")
        lbl = Gtk.Label(label=category.upper())
        lbl.set_halign(Gtk.Align.START)
        lbl.set_hexpand(True)
        row.append(lbl)
        return row

    def _make_bind_row(self, bind_type, mods, key, action, args) -> Gtk.Box:
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        row.add_css_class("bind-row")

        specs = [
            (bind_type, "t-type",   self._WIDTHS[0], False),
            (mods,      "t-mods",   self._WIDTHS[1], False),
            (key,       "t-key",    self._WIDTHS[2], False),
            (action,    "t-action", self._WIDTHS[3], False),
            (args,      "t-args",   -1,              True),
        ]
        for text, css_class, width, expand in specs:
            lbl = Gtk.Label(label=text)
            lbl.add_css_class(css_class)
            lbl.set_halign(Gtk.Align.START)
            lbl.set_xalign(0.0)
            if width > 0:
                lbl.set_size_request(width, -1)
            if expand:
                lbl.set_hexpand(True)
                lbl.set_ellipsize(Pango.EllipsizeMode.END)
                lbl.set_max_width_chars(60)
            row.append(lbl)

        return row

    # ── file monitoring ──

    def _setup_file_monitor(self):
        """Monitor the parent directory to survive atomic saves (neovim, vscode)."""
        dirpath  = os.path.dirname(BINDS_FILE)
        gdir     = Gio.File.new_for_path(dirpath)
        self._monitor = gdir.monitor_directory(
            Gio.FileMonitorFlags.WATCH_MOVES, None
        )
        self._monitor.connect("changed", self._on_dir_changed)

    def _on_dir_changed(
        self,
        _monitor,
        gfile: Gio.File,
        other_file: Gio.File | None,
        event_type: Gio.FileMonitorEvent,
    ):
        # Check whether the event concerns our target file
        paths = {gfile.get_path() if gfile else None}
        if other_file:
            paths.add(other_file.get_path())
        if BINDS_FILE not in paths:
            return

        relevant = {
            Gio.FileMonitorEvent.CHANGES_DONE_HINT,
            Gio.FileMonitorEvent.RENAMED,
            Gio.FileMonitorEvent.MOVED_IN,
            Gio.FileMonitorEvent.CREATED,
        }
        if event_type not in relevant:
            return

        # Debounce: coalesce rapid events into a single rebuild
        if self._rebuild_timer is not None:
            GLib.source_remove(self._rebuild_timer)
        self._rebuild_timer = GLib.timeout_add(120, self._debounced_rebuild)

    def _debounced_rebuild(self) -> bool:
        self._rebuild_timer = None
        self.rebuild()
        return GLib.SOURCE_REMOVE

# ── application ───────────────────────────────────────────────────────────────

class KeybindsApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.hypr.keybindsviewer")
        self._win: KeybindsWindow | None = None
        self._hide_timer: int | None = None

    def do_activate(self):
        if self._win is None:
            self._win = KeybindsWindow(self)

        # Prevent GTK from quitting when the window is hidden (no visible windows → auto-quit)
        self.hold()

        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGUSR1, self._show)
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGUSR2, self._hide)

    # signal handlers must return SOURCE_CONTINUE so GLib keeps them registered
    def _show(self) -> bool:
        if self._hide_timer is not None:
            GLib.source_remove(self._hide_timer)
            self._hide_timer = None
        self._win.set_visible(True)
        self._win.present()
        return GLib.SOURCE_CONTINUE

    def _hide(self) -> bool:
        if self._hide_timer is not None:
            GLib.source_remove(self._hide_timer)
        self._hide_timer = GLib.timeout_add(50, self._do_hide)
        return GLib.SOURCE_CONTINUE

    def _do_hide(self) -> bool:
        self._hide_timer = None
        if self._win:
            self._win.set_visible(False)
        return GLib.SOURCE_REMOVE


if __name__ == '__main__':
    app = KeybindsApp()
    sys.exit(app.run(None))
