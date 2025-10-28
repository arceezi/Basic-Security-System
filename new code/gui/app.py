import tkinter as tk
import tkinter.ttk as ttk
from config import GUI_TITLE
from .theme import apply_theme
from .frames.login import LoginFrame
from .frames.register import RegisterFrame
from .frames.files import FilesFrame
from .frames.admin import AdminFrame
from .frames.dashboard import DashboardFrame

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(GUI_TITLE)
        self.geometry("720x480")
        apply_theme(self)
        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self.frames = {}

        self.status_var = tk.StringVar(value="Ready")
        status = ttk.Label(self, textvariable=self.status_var, anchor="w")
        status.pack(fill="x")

        self.navigate(LoginFrame)

    def set_status(self, msg: str) -> None:
        self.status_var.set(msg)

    def navigate(self, frame_cls, **kwargs) -> None:
        # Destroy current frame, create new
        for child in self.container.winfo_children():
            child.destroy()
        frame = frame_cls(self.container, app=self, **kwargs)
        frame.pack(fill="both", expand=True)

    # Convenience helpers for frames
    def show_login(self):
        self.navigate(LoginFrame)

    def show_register(self):
        self.navigate(RegisterFrame)

    def show_files(self):
        self.navigate(FilesFrame)

    def show_admin(self):
        self.navigate(AdminFrame)

    def show_dashboard(self):
        self.navigate(DashboardFrame)
