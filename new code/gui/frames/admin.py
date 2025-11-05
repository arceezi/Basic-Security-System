import tkinter as tk
import tkinter.ttk as ttk
from admin import reset_password, list_users, unlock_system, lock_system
import tkinter as tk

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

        lock_frame = ttk.Frame(self)
        lock_frame.pack(anchor="w", pady=(4,0), fill="x")
        ttk.Button(lock_frame, text="Lock System", command=self.on_lock).pack(side="left")
        self.lock_secs_var = tk.StringVar()
        ttk.Entry(lock_frame, textvariable=self.lock_secs_var, width=6).pack(side="left", padx=(6,0))
        ttk.Label(lock_frame, text="seconds (blank for default)").pack(side="left", padx=(6,0))

        ttk.Button(self, text="Unlock System", command=self.on_unlock).pack(anchor="w", pady=(6,12))
        ttk.Button(self, text="Back", command=self.app.show_files).pack(anchor="w")

        self.freeze_status = ttk.Label(self, text="")
        self.freeze_status.pack(anchor="w", pady=(4,0))

        self.user_table = ttk.Treeview(self, columns=("username", "is_admin", "failed_attempts", "last_login_at"), show="headings", height=12)
        self.user_table.heading("username", text="Username")
        self.user_table.heading("is_admin", text="Admin")
        self.user_table.heading("failed_attempts", text="Failed Attempts")
        self.user_table.heading("last_login_at", text="Last Login")
        self.user_table.column("username", width=120)
        self.user_table.column("is_admin", width=60, anchor="center")
        self.user_table.column("failed_attempts", width=100, anchor="center")
        self.user_table.column("last_login_at", width=160)
        self.user_table.pack(fill="both", expand=True, pady=8)

        self._refresh_freeze_status()

    def _refresh_freeze_status(self):
        from auth_manager import is_system_frozen, freeze_remaining_seconds
        if is_system_frozen():
            secs = freeze_remaining_seconds()
            self.freeze_status.config(text=f"System is LOCKED (frozen) for {secs if secs else '?'} seconds")
        else:
            self.freeze_status.config(text="System is UNLOCKED (not frozen)")
        self.after(1000, self._refresh_freeze_status)

    def on_reset(self):
        ok, msg = reset_password(self.u_var.get().strip(), self.p_var.get().strip())
        self.app.set_status(msg)
        self.app.show_toast(msg)

    def on_lock(self):
        s = self.lock_secs_var.get().strip()
        try:
            secs = int(s) if s else None
        except Exception:
            self.app.set_status("Invalid seconds value")
            self.app.show_toast("Invalid seconds value")
            return
        lock_system(secs)
        msg = f"System locked for {secs if secs else 'default'} seconds"
        self.app.set_status(msg)
        self.app.show_toast(msg)

    def on_list(self):
        users = list_users()
        self.user_table.delete(*self.user_table.get_children())
        for u in users:
            self.user_table.insert("", "end", values=(u["username"], "Yes" if u["is_admin"] else "No", u["failed_attempts"], u["last_login_at"] or "-"))

    def on_unlock(self):
        unlock_system()
        msg = "System unlocked"
        self.app.set_status(msg)
        self.app.show_toast(msg)
