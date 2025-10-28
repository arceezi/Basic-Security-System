import tkinter.ttk as ttk
from gui.widgets import LabeledEntry
from auth_manager import register_user

class RegisterFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        ttk.Label(self, text="Register", style="Header.TLabel").pack(anchor="w", pady=(8,12))

        form = ttk.Frame(self)
        form.pack(fill="x", pady=8)
        self.username = LabeledEntry(form, "Username:")
        self.password = LabeledEntry(form, "Password:", show="*")
        self.username.pack(fill="x", pady=4)
        self.password.pack(fill="x", pady=4)

        btns = ttk.Frame(self)
        btns.pack(fill="x", pady=8)
        ttk.Button(btns, text="Create", command=self.on_create).pack(side="left")
        ttk.Button(btns, text="Back to Login", command=self.app.show_login).pack(side="left", padx=8)

        self.msg = ttk.Label(self, text="")
        self.msg.pack(anchor="w")

    def on_create(self):
        u = self.username.get().strip()
        p = self.password.get().strip()
        ok, message = register_user(u, p)
        self.msg.config(text=message)
        self.app.set_status(message)
        if ok:
            self.app.show_login()
