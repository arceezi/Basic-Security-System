import tkinter.ttk as ttk

def apply_theme(root):
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass
    style.configure("TButton", padding=6)
    style.configure("TLabel", padding=4)
    style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"))
