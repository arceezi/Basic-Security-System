import tkinter as tk
import tkinter.ttk as ttk

class LabeledEntry(ttk.Frame):
    def __init__(self, parent, label_text: str, show: str | None = None):
        super().__init__(parent)
        self.label = ttk.Label(self, text=label_text)
        self.entry = ttk.Entry(self, show=show)
        self.label.pack(side="left", padx=(0,8))
        self.entry.pack(side="left", fill="x", expand=True)

    def get(self) -> str:
        return self.entry.get()

class Banner(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.var = tk.StringVar()
        self.label = ttk.Label(self, textvariable=self.var)
        self.label.pack(fill="x")
        self.pack_forget()

    def show(self, message: str):
        self.var.set(message)
        self.pack(fill="x", pady=(0,8))

    def hide(self):
        self.pack_forget()
