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

class Toast(tk.Toplevel):
    def __init__(self, parent, message, duration=2000):
        super().__init__(parent)
        self.wm_overrideredirect(True)
        self.configure(bg="#333")
        label = tk.Label(self, text=message, bg="#333", fg="#fff", font=("Segoe UI", 10))
        label.pack(ipadx=16, ipady=8)
        self.after(duration, self.destroy)
        self.update_idletasks()
        # Position bottom right of parent
        x = parent.winfo_rootx() + parent.winfo_width() - self.winfo_width() - 30
        y = parent.winfo_rooty() + parent.winfo_height() - self.winfo_height() - 30
        self.geometry(f"+{x}+{y}")
