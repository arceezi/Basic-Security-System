import tkinter.ttk as ttk

def apply_theme(root):
    style = ttk.Style(root)

    # Use a reliable base theme
    try:
        style.theme_use("clam")
    except Exception:
        pass

    # 🎨 --- GENERAL STYLE SETTINGS ---
    style.configure(".", font=("Segoe UI", 10))  # global default font
    style.configure("TFrame", background="white")
    style.configure("TLabel", background="white", foreground="#0d47a1", padding=4)
    style.configure("TEntry", padding=4)

    # 🧭 --- HEADER LABEL ---
    style.configure(
        "Header.TLabel",
        font=("Segoe UI", 18, "bold"),
        foreground="#0d47a1",
        background="white",
        padding=(0, 8)
    )

    # 🔵 --- BUTTONS (Blue Theme) ---
    style.configure(
        "TButton",
        background="#1565c0",      # blue
        foreground="white",
        padding=(8, 6),
        borderwidth=0
    )
    style.map(
        "TButton",
        background=[
            ("active", "#1e88e5"),   # lighter blue when hovered
            ("disabled", "#90caf9")  # faded when disabled
        ],
        foreground=[
            ("active", "white"),
            ("disabled", "white")
        ]
    )

    # ✨ --- OPTIONAL ACCENT BUTTON (for Login/Register) ---
    style.configure(
        "Accent.TButton",
        background="#1976d2",
        foreground="white",
        font=("Segoe UI", 10, "bold"),
        padding=(10, 6)
    )
    style.map(
        "Accent.TButton",
        background=[("active", "#2196f3")],
        foreground=[("active", "white")]
    )

    # 🩵 --- MISC ELEMENTS ---
    style.configure("Banner.TLabel", background="#e3f2fd", foreground="#0d47a1", padding=6)

    # Apply window background color (if not overridden)
    root.configure(bg="white")
