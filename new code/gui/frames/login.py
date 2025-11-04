import tkinter as tk
import tkinter.ttk as ttk
from gui.widgets import LabeledEntry, Banner
from auth_manager import authenticate, is_system_frozen
from ..theme import apply_theme


class LoginFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=(50, 50))
        self.app = app
        self.pack_propagate(False)

        container = ttk.Frame(self)
        container.pack(expand=True)

        ttk.Label(container, text="Login", style="Header.TLabel").pack(anchor="center", pady=(8, 12))

        self.banner = Banner(container)
        if is_system_frozen():
            self.banner.show("System is frozen. Try again later or contact admin.")

        form = ttk.Frame(container)
        form.pack(anchor="center", pady=8)

        self.username = LabeledEntry(form, "Username:")
        self.password = LabeledEntry(form, "Password:", show="*")
        self.username.pack(fill="x", pady=4)
        self.password.pack(fill="x", pady=4)

        btns = ttk.Frame(container)
        btns.pack(anchor="center", pady=8)

        ttk.Button(btns, text="Login", command=self.on_login, style="Accent.TButton").pack(side="left", padx=(0, 8))
        ttk.Button(btns, text="Register", command=self.app.show_register, style="Accent.TButton").pack(side="left")

        self.msg = tk.StringVar()
        ttk.Label(container, textvariable=self.msg, foreground="#444").pack(anchor="center", pady=(6, 0))

   
    def on_login(self):
        username = self.username.get().strip()
        password = self.password.get().strip()

        ok, message = authenticate(username, password)
        self.msg.set(message)
        self.app.set_status(message)

        if ok:
            self.app.show_files()


class LoginApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Blue Themed Login")
        self.geometry("900x500")
        self.configure(bg="#0d47a1")

        apply_theme(self)

        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True)

        # Left panel: Image area
        self._build_left_panel(main_frame)

        # Right panel: Login form
        self._build_right_panel(main_frame)


    def _build_left_panel(self, parent):
        left = tk.Frame(parent, bg="#0d47a1", width=450)
        left.pack(side="left", fill="both", expand=True)

        try:
            img = tk.PhotoImage(file="path/to/your/image.png")
            img_label = tk.Label(left, image=img, bg="#0d47a1")
            img_label.image = img 
            img_label.place(relx=0.5, rely=0.5, anchor="center")
        except Exception:
            tk.Label(left, text="Image not found", fg="white", bg="#0d47a1", font=("Segoe UI", 14)).place(relx=0.5, rely=0.5, anchor="center")

    def _build_right_panel(self, parent):
        right = ttk.Frame(parent, width=450)
        right.pack(side="right", fill="both", expand=True)
        login_frame = LoginFrame(right, self)
        login_frame.pack(fill="both", expand=True)


    def show_register(self):
        print("Register button clicked")

    def set_status(self, message):
        print("Status:", message)

    def show_files(self):
        print("Login successful! Showing files...")

if __name__ == "__main__":
    app = LoginApp()
    app.mainloop()
