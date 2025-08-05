# nt10x.py
# NT 1.0X - Retro Win95-like desktop using Tkinter
# Run: python nt10x.py

import sys
import time
import tkinter as tk
from tkinter import ttk

APP_TITLE = "NT 1.0X"
WIN_W, WIN_H = 600, 400
START_BG = "#c0c0c0"  # Win95 gray
FACE_BG = "#d4d0c8"
BTN_LIGHT = "#ffffff"
BTN_DARK = "#404040"
BTN_SHADOW = "#808080"
TEXT_DARK = "#000000"
TEXT_LIGHT = "#ffffff"
ACTIVE_BLUE = "#000080"
ACTIVE_BLUE_LIGHT = "#0000a8"

# Global maximize flag, default False (per request)
MAXIMIZE_ENABLED = False


def bevel_frame(parent, bg=FACE_BG, relief="raised"):
    """
    Create a classic Win95-style beveled frame using nested frames.
    relief="raised" or "sunken"
    """
    outer = tk.Frame(parent, bg=BTN_DARK)
    inner_light = tk.Frame(outer, bg=BTN_LIGHT)
    inner_shadow = tk.Frame(inner_light, bg=BTN_SHADOW)
    face = tk.Frame(inner_shadow, bg=bg)

    pad = 1
    inner_light.pack(padx=pad, pady=pad, fill="both", expand=True)
    inner_shadow.pack(padx=pad, pady=pad, fill="both", expand=True)

    if relief == "raised":
        # Outer dark, inner light/shadow gives raised look
        face.pack(padx=(1, 0), pady=(1, 0), fill="both", expand=True)
    else:
        # Invert to appear sunken
        face.configure(bg=bg)
        face.pack(padx=(0, 1), pady=(0, 1), fill="both", expand=True)

    return outer, face


def win95_button(
    parent, text="", command=None, width=None, state="normal", tooltip=None
):
    # A flat button with Win95 bevel using relief changes on press
    frm_outer = tk.Frame(parent, bg=BTN_DARK)
    frm_light = tk.Frame(frm_outer, bg=BTN_LIGHT)
    frm_shadow = tk.Frame(frm_light, bg=BTN_SHADOW)
    face = tk.Frame(frm_shadow, bg=FACE_BG)
    lbl = tk.Label(
        face,
        text=text,
        bg=FACE_BG,
        fg=TEXT_DARK,
        padx=8,
        pady=2,
        font=("MS Sans Serif", 9),
    )
    frm_light.pack(padx=1, pady=1)
    frm_shadow.pack(padx=1, pady=1)
    face.pack(padx=(1, 0), pady=(1, 0))
    lbl.pack()

    def press(_=None):
        frm_outer.configure(bg=BTN_LIGHT)
        frm_light.configure(bg=BTN_DARK)
        frm_shadow.configure(bg=BTN_SHADOW)
        face.configure(bg=BTN_SHADOW)
        lbl.configure(bg=BTN_SHADOW)
        if state != "disabled" and command:
            parent.after(80, command)

    def release(_=None):
        frm_outer.configure(bg=BTN_DARK)
        frm_light.configure(bg=BTN_LIGHT)
        frm_shadow.configure(bg=BTN_SHADOW)
        face.configure(bg=FACE_BG)
        lbl.configure(bg=FACE_BG)

    if state == "disabled":
        lbl.configure(fg=BTN_SHADOW)

    for w in (frm_outer, face, lbl):
        w.bind("<ButtonPress-1>", press)
        w.bind("<ButtonRelease-1>", release)

    if width is not None:
        lbl.configure(width=width)

    # Optional tooltip
    if tooltip:
        tip = tk.Toplevel(parent)
        tip.withdraw()
        tip.overrideredirect(True)
        tip.attributes("-topmost", True)
        tip_lbl = tk.Label(
            tip,
            text=tooltip,
            bg="#ffffe1",
            fg="#000000",
            bd=1,
            relief="solid",
            font=("MS Sans Serif", 8),
            padx=4,
            pady=1,
        )

        tip_lbl.pack()

        def enter(e):
            tip.geometry(f"+{e.x_root+12}+{e.y_root+12}")
            tip.deiconify()

        def leave(_):
            tip.withdraw()

        lbl.bind("<Enter>", enter)
        lbl.bind("<Leave>", leave)

    return frm_outer


class SplashScreen(tk.Toplevel):
    def __init__(self, master, on_done):
        super().__init__(master)
        self.on_done = on_done
        self.overrideredirect(True)
        self.configure(bg=BTN_DARK)
        self.attributes("-topmost", True)

        w, h = 420, 240
        self.update_idletasks()
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        outer, face = bevel_frame(self, bg=FACE_BG, relief="raised")
        outer.pack(fill="both", expand=True, padx=6, pady=6)

        title = tk.Label(
            face,
            text="NT 1.0X",
            font=("MS Sans Serif", 16, "bold"),
            fg=TEXT_LIGHT,
            bg=ACTIVE_BLUE,
            anchor="w",
            padx=8,
        )
        title.pack(fill="x", pady=(8, 6), padx=8)

        info = tk.Label(
            face,
            text="Starting NT 1.0X...\nCopyright (C) 1995-1998",
            font=("MS Sans Serif", 9),
            bg=FACE_BG,
            fg=TEXT_DARK,
            justify="left",
        )
        info.pack(anchor="w", padx=12)

        # Faux progress bar (sunken)
        bar_outer, bar_face = bevel_frame(face, bg="#c8c8c8", relief="sunken")
        bar_outer.pack(fill="x", padx=12, pady=16)
        self.bar = tk.Frame(bar_face, bg=ACTIVE_BLUE_LIGHT, height=16, width=0)
        self.bar.pack(side="left")

        self.progress = 0
        self.after(80, self._tick)

    def _tick(self):
        self.progress = min(100, self.progress + 5)
        w = int((self.progress / 100.0) * 360)
        self.bar.configure(width=w)
        if self.progress >= 100:
            self.after(300, self._finish)
        else:
            self.after(80, self._tick)

    def _finish(self):
        try:
            self.destroy()
        except Exception:
            pass
        self.on_done()


class RetroWindow(tk.Frame):
    def __init__(self, parent, title="NT 1.0X - Main", width=WIN_W, height=WIN_H):
        super().__init__(parent, bg=FACE_BG)
        self.parent = parent
        self.width = width
        self.height = height
        self.is_maximized = False

        # Container: simulated window with beveled border
        self.outer, self.face = bevel_frame(parent, bg=FACE_BG, relief="raised")
        self.outer.place(x=60, y=60, width=self.width, height=self.height)

        self._build_title_bar(title)
        self._build_content()

        # Dragging via title bar
        self._drag_data = {"x": 0, "y": 0}
        for w in (self.title_bar, self.title_lbl):
            w.bind("<ButtonPress-1>", self._start_move)
            w.bind("<B1-Motion>", self._do_move)

    def _build_title_bar(self, title):
        self.title_bar = tk.Frame(self.face, bg=ACTIVE_BLUE, height=24)
        self.title_bar.pack(fill="x")

        self.title_lbl = tk.Label(
            self.title_bar,
            text=title,
            bg=ACTIVE_BLUE,
            fg=TEXT_LIGHT,
            anchor="w",
            padx=8,
            font=("MS Sans Serif", 9, "bold"),
        )
        self.title_lbl.pack(side="left", fill="x", expand=True)

        # System buttons container (right side)
        sys_btns = tk.Frame(self.title_bar, bg=ACTIVE_BLUE)
        sys_btns.pack(side="right")

        # Minimize button
        btn_min = win95_button(
            sys_btns,
            text="_",
            command=self._minimize,
            width=3,
            tooltip="Minimize",
        )
        btn_min.pack(side="left", padx=2, pady=2)

        # Maximize button (disabled by default per spec)
        btn_max = win95_button(
            sys_btns,
            text="▢",
            command=self._toggle_maximize if MAXIMIZE_ENABLED else None,
            width=3,
            tooltip="Maximize (disabled)" if not MAXIMIZE_ENABLED else "Maximize",
            state="disabled" if not MAXIMIZE_ENABLED else "normal",
        )
        btn_max.pack(side="left", padx=2, pady=2)

        # Close button
        btn_close = win95_button(
            sys_btns, text="X", command=self._close, width=3, tooltip="Close"
        )
        btn_close.pack(side="left", padx=2, pady=2)

    def _build_content(self):
        # Client area with sunken look
        self.client_outer, self.client = bevel_frame(
            self.face, bg=FACE_BG, relief="sunken"
        )
        self.client_outer.pack(fill="both", expand=True, padx=6, pady=6)

        lbl = tk.Label(
            self.client,
            text="Welcome to NT 1.0X\nWindows 95 vibes = ON",
            bg=FACE_BG,
            fg=TEXT_DARK,
            font=("MS Sans Serif", 10),
            padx=12,
            pady=12,
            justify="left",
        )
        lbl.pack(anchor="nw")

        # Some Win95-style controls
        controls = tk.Frame(self.client, bg=FACE_BG)
        controls.pack(anchor="nw", padx=12, pady=6)

        cb_var = tk.BooleanVar(value=True)
        chk = tk.Checkbutton(
            controls,
            text="Enable vibes",
            variable=cb_var,
            bg=FACE_BG,
            fg=TEXT_DARK,
            activebackground=FACE_BG,
            activeforeground=TEXT_DARK,
            selectcolor=FACE_BG,
            highlightthickness=0,
            font=("MS Sans Serif", 9),
        )
        chk.grid(row=0, column=0, sticky="w", padx=(0, 12))

        rbv = tk.StringVar(value="s11")
        rb1 = tk.Radiobutton(
            controls,
            text="Mode s11 (600x400)",
            variable=rbv,
            value="s11",
            bg=FACE_BG,
            fg=TEXT_DARK,
            activebackground=FACE_BG,
            selectcolor=FACE_BG,
            highlightthickness=0,
            font=("MS Sans Serif", 9),
        )
        rb1.grid(row=0, column=1, sticky="w")

        btn_panel = tk.Frame(self.client, bg=FACE_BG)
        btn_panel.pack(anchor="nw", padx=12, pady=8)

        win95_button(
            btn_panel, text="About...", command=self._about, width=10
        ).pack(side="left", padx=4)
        win95_button(
            btn_panel, text="Notepad", command=self._notepad, width=10
        ).pack(side="left", padx=4)

    def _start_move(self, event):
        self._drag_data["x"] = event.x_root - self.outer.winfo_rootx()
        self._drag_data["y"] = event.y_root - self.outer.winfo_rooty()

    def _do_move(self, event):
        if self.is_maximized:
            return
        nx = event.x_root - self._drag_data["x"]
        ny = event.y_root - self._drag_data["y"]
        self.outer.place_configure(x=nx, y=ny)

    def _toggle_maximize(self):
        if not MAXIMIZE_ENABLED:
            return
        if not self.is_maximized:
            self.prev_geom = self.outer.place_info()
            self.outer.place_configure(x=0, y=0, relwidth=1.0, relheight=1.0)
            self.is_maximized = True
        else:
            self.outer.place_configure(
                x=self.prev_geom.get("x", 60),
                y=self.prev_geom.get("y", 60),
                relwidth="",
                relheight="",
                width=WIN_W,
                height=WIN_H,
            )
            self.is_maximized = False

    def _minimize(self):
        self.outer.place_forget()

    def _close(self):
        self.outer.destroy()

    def _about(self):
        AboutDialog(self.parent, "NT 1.0X", "A retro desktop environment (Win95 vibe)")

    def _notepad(self):
        Notepad(self.parent)


class Taskbar(tk.Frame):
    def __init__(self, parent, on_start):
        super().__init__(parent, bg=FACE_BG)
        # Raised taskbar
        self.outer, self.face = bevel_frame(parent, bg=FACE_BG, relief="raised")
        self.outer.pack(side="bottom", fill="x")

        bar = tk.Frame(self.face, bg=FACE_BG, height=32)
        bar.pack(fill="x")

        # Start button
        start = win95_button(bar, text="Start", command=on_start, width=8)
        start.pack(side="left", padx=4, pady=2)

        # Spacer/app area
        app_area = tk.Frame(bar, bg=FACE_BG)
        app_area.pack(side="left", fill="x", expand=True)

        # Clock (right)
        clock_outer, clock_face = bevel_frame(bar, bg=FACE_BG, relief="sunken")
        clock_outer.pack(side="right", padx=6, pady=4)
        self.clock_lbl = tk.Label(
            clock_face, text="", bg=FACE_BG, fg=TEXT_DARK, font=("MS Sans Serif", 9)
        )
        self.clock_lbl.pack(padx=8, pady=2)
        self._tick()

    def _tick(self):
        self.clock_lbl.configure(text=time.strftime("%I:%M %p").lstrip("0"))
        self.after(1000, self._tick)


class StartMenu(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(bg=BTN_DARK)

        outer, face = bevel_frame(self, bg=FACE_BG, relief="raised")
        outer.pack(fill="both", expand=True)
        self.face = face

        items = [
            ("Programs", None),
            ("Accessories", None),
            ("Notepad", self._notepad),
            ("About NT 1.0X", self._about),
            ("Shut Down...", self._shutdown),
        ]

        for text, cmd in items:
            b = tk.Button(
                face,
                text=text,
                bg=FACE_BG,
                fg=TEXT_DARK,
                relief="flat",
                anchor="w",
                padx=10,
                font=("MS Sans Serif", 9),
                command=cmd if cmd else self._noop,
            )
            b.pack(fill="x", padx=6, pady=2)

        self.bind("<FocusOut>", lambda e: self.destroy())

    def popup(self, x, y):
        self.geometry(f"+{x}+{y}")
        self.deiconify()
        self.focus_set()

    def _noop(self):
        self.destroy()

    def _about(self):
        self.destroy()
        AboutDialog(self.master, "About NT 1.0X", "NT 1.0X\nWindows 95 vibes = ON")

    def _shutdown(self):
        self.destroy()
        if tk.messagebox.askyesno("Shut Down", "Shut down NT 1.0X?"):
            self.master.quit()

    def _notepad(self):
        self.destroy()
        Notepad(self.master)


class AboutDialog(tk.Toplevel):
    def __init__(self, master, title, message):
        super().__init__(master)
        self.title(title)
        self.configure(bg=BTN_DARK)
        self.resizable(False, False)

        outer, face = bevel_frame(self, bg=FACE_BG, relief="raised")
        outer.pack(fill="both", expand=True, padx=6, pady=6)

        lbl = tk.Label(
            face,
            text=message,
            bg=FACE_BG,
            fg=TEXT_DARK,
            font=("MS Sans Serif", 10),
            padx=12,
            pady=12,
            justify="left",
        )
        lbl.pack()

        btns = tk.Frame(face, bg=FACE_BG)
        btns.pack(pady=6)
        win95_button(btns, text="OK", command=self.destroy, width=8).pack()

        self.update_idletasks()
        w, h = 320, 160
        x = self.master.winfo_rootx() + 80
        y = self.master.winfo_rooty() + 80
        self.geometry(f"{w}x{h}+{x}+{y}")


class Notepad(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Notepad - NT 1.0X")
        self.configure(bg=BTN_DARK)

        outer, face = bevel_frame(self, bg=FACE_BG, relief="raised")
        outer.pack(fill="both", expand=True, padx=6, pady=6)

        # Menu bar (simple)
        menu_outer, menu_face = bevel_frame(face, bg=FACE_BG, relief="raised")
        menu_outer.pack(fill="x", padx=6, pady=(6, 0))
        menubar = tk.Frame(menu_face, bg=FACE_BG)
        menubar.pack(fill="x")
        for name in ["File", "Edit", "Help"]:
            tk.Label(
                menubar,
                text=name,
                bg=FACE_BG,
                fg=TEXT_DARK,
                font=("MS Sans Serif", 9),
                padx=6,
            ).pack(side="left")

        # Text area (sunken)
        txt_outer, txt_face = bevel_frame(face, bg="#ffffff", relief="sunken")
        txt_outer.pack(fill="both", expand=True, padx=6, pady=6)
        self.text = tk.Text(
            txt_face, bg="#ffffff", fg="#000000", insertbackground="#000000"
        )
        self.text.pack(fill="both", expand=True)

        # Status bar
        status_outer, status_face = bevel_frame(face, bg=FACE_BG, relief="sunken")
        status_outer.pack(fill="x", padx=6, pady=(0, 6))
        self.status = tk.Label(
            status_face,
            text="Ln 1, Col 1",
            bg=FACE_BG,
            fg=TEXT_DARK,
            font=("MS Sans Serif", 9),
        )
        self.status.pack(anchor="w", padx=6)

        self.text.bind("<KeyRelease>", self._update_status)

        self.geometry("520x360+120+120")

    def _update_status(self, _=None):
        idx = self.text.index(tk.INSERT)
        ln, col = map(int, idx.split("."))
        self.status.configure(text=f"Ln {ln}, Col {col+1}")


class Desktop(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.configure(bg=START_BG)
        self.geometry("800x600+120+80")
        self.minsize(640, 480)

        # Disable default themed ttk to keep classic look
        style = ttk.Style(self)
        try:
            style.theme_use("classic")
        except Exception:
            pass

        # Desktop background (pattern)
        self.canvas = tk.Canvas(self, bg=START_BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self._paint_pattern)

        self.taskbar = Taskbar(self, self._open_start_menu)

        # Main window mock
        self.main_window = RetroWindow(self, title="NT 1.0X - Main", width=WIN_W, height=WIN_H)

        # Splash screen first
        self.withdraw()
        self.after(100, lambda: SplashScreen(self, self._after_splash))

    def _after_splash(self):
        self.deiconify()
        self.lift()

    def _paint_pattern(self, event):
        # Simple checker pattern like old desktops
        self.canvas.delete("pat")
        step = 16
        w, h = event.width, event.height
        c1, c2 = "#008080", "#007070"
        for y in range(0, h, step):
            for x in range(0, w, step):
                c = c1 if (x // step + y // step) % 2 == 0 else c2
                self.canvas.create_rectangle(
                    x, y, x + step, y + step, fill=c, outline=c, tags="pat"
                )

    def _open_start_menu(self):
        menu = StartMenu(self)
        # Place above the Start button
        x = self.winfo_rootx() + 8
        y = self.winfo_rooty() + self.winfo_height() - 220
        menu.popup(x, y)


def main():
    app = Desktop()
    app.mainloop()


if __name__ == "__main__":
    main()
