import tkinter as tk
import tkinter.ttk as ttk
from gui.widgets import LabeledEntry, Banner
from auth_manager import authenticate, is_system_frozen

class LoginFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        ttk.Label(self, text="Login", style="Header.TLabel").pack(anchor="w", pady=(8,12))

        self.banner = Banner(self)
        if is_system_frozen():
            self.banner.show("System is frozen. Try again later or contact admin.")

        form = ttk.Frame(self)
        form.pack(fill="x", pady=8)
        self.username = LabeledEntry(form, "Username:")
        self.password = LabeledEntry(form, "Password:", show="*")
        self.username.pack(fill="x", pady=4)
        self.password.pack(fill="x", pady=4)

        btns = ttk.Frame(self)
        btns.pack(fill="x", pady=8)
        ttk.Button(btns, text="Login", command=self.on_login).pack(side="left")
        ttk.Button(btns, text="Register", command=self.app.show_register).pack(side="left", padx=8)

        self.msg = tk.StringVar()
        ttk.Label(self, textvariable=self.msg, foreground="#444").pack(anchor="w", pady=(6,0))

    def on_login(self):
        u = self.username.get().strip()
        p = self.password.get().strip()
        ok, message = authenticate(u, p)
        self.msg.set(message)
        self.app.set_status(message)
        if ok:
            self.app.show_files()
