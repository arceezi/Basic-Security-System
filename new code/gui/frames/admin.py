import tkinter as tk
import tkinter.ttk as ttk
from admin import reset_password, list_users, unlock_system

class AdminFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        ttk.Label(self, text="Admin", style="Header.TLabel").pack(anchor="w", pady=(8,12))

        section = ttk.Labelframe(self, text="Reset Password")
        section.pack(fill="x", pady=8)
        self.u_var = tk.StringVar()
        self.p_var = tk.StringVar()
        ttk.Entry(section, textvariable=self.u_var).pack(side="left", padx=4)
        ttk.Entry(section, textvariable=self.p_var, show="*").pack(side="left", padx=4)
        ttk.Button(section, text="Reset", command=self.on_reset).pack(side="left", padx=4)

        ttk.Button(self, text="List Users", command=self.on_list).pack(anchor="w", pady=(4,0))
        ttk.Button(self, text="Unlock System", command=self.on_unlock).pack(anchor="w", pady=(4,12))
        ttk.Button(self, text="Back", command=self.app.show_files).pack(anchor="w")

        self.out = tk.Text(self, height=12)
        self.out.pack(fill="both", expand=True, pady=8)

    def on_reset(self):
        ok, msg = reset_password(self.u_var.get().strip(), self.p_var.get().strip())
        self.app.set_status(msg)

    def on_list(self):
        users = list_users()
        self.out.delete("1.0", tk.END)
        for u in users:
            self.out.insert("end", f"{u['username']}\tadmin={u['is_admin']}\tfails={u['failed_attempts']}\tlast={u['last_login_at']}\n")

    def on_unlock(self):
        unlock_system()
        self.app.set_status("System unlocked")
