import tkinter as tk
import tkinter.ttk as ttk
from file_access import list_protected_files, open_protected_file
from auth_manager import logout
from user_store import get_user
from session import session

class FilesFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        ttk.Label(self, text="Protected Files", style="Header.TLabel").pack(anchor="w", pady=(8,12))

        top = ttk.Frame(self)
        top.pack(fill="x")
        self.user_label = ttk.Label(top, text=f"Logged in as: {session.get_current_user()}")
        self.user_label.pack(side="left")

        # Admin button visible if admin
        current = session.get_current_user()
        rec = get_user(current) if current else None
        if rec and rec.get("is_admin"):
            ttk.Button(top, text="Admin", command=self.app.show_admin).pack(side="right", padx=4)
        ttk.Button(top, text="Dashboard", command=self.app.show_dashboard).pack(side="right", padx=4)
        ttk.Button(top, text="Logout", command=self.on_logout).pack(side="right", padx=4)

        body = ttk.Frame(self)
        body.pack(fill="both", expand=True, pady=8)

        self.listbox = tk.Listbox(body)
        self.listbox.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(body, orient="vertical", command=self.listbox.yview)
        sb.pack(side="left", fill="y")
        self.listbox.configure(yscrollcommand=sb.set)

        right = ttk.Frame(body)
        right.pack(side="left", fill="both", padx=8)
        ttk.Button(right, text="Refresh", command=self.refresh_list).pack(fill="x")
        ttk.Button(right, text="Open", command=self.on_open).pack(fill="x", pady=(6,0))

        self.content = tk.Text(self, height=10)
        self.content.pack(fill="both", expand=True, pady=8)

        self.refresh_list()

    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        try:
            for name in list_protected_files():
                self.listbox.insert(tk.END, name)
        except Exception as e:
            self.app.set_status(str(e))

    def on_open(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        name = self.listbox.get(sel[0])
        try:
            text = open_protected_file(name)
        except Exception as e:
            self.app.set_status(str(e))
            return
        self.content.delete("1.0", tk.END)
        self.content.insert("1.0", text)

    def on_logout(self):
        logout()
        self.app.show_login()
