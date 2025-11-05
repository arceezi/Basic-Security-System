import os
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox, filedialog
from file_access import list_protected_files, open_protected_file, add_protected_file, delete_protected_file
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
        ttk.Button(right, text="Add File", command=self.on_add).pack(fill="x", pady=(6,0))
        ttk.Button(right, text="Delete", command=self.on_delete).pack(fill="x", pady=(6,0))
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

    def on_add(self):
        # Popup to add a new file
        popup = tk.Toplevel(self)
        popup.title("Add File")
        popup.geometry("400x300")

        ttk.Label(popup, text="Filename:").pack(anchor="w", padx=8, pady=(8,0))
        name_entry = ttk.Entry(popup)
        name_entry.pack(fill="x", padx=8)

        ttk.Label(popup, text="Content:").pack(anchor="w", padx=8, pady=(8,0))
        content_text = tk.Text(popup, height=10)
        content_text.pack(fill="both", expand=True, padx=8, pady=(0,8))

        btn_frame = ttk.Frame(popup)
        btn_frame.pack(fill="x", padx=8, pady=(0,8))

        def create_and_close():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Filename cannot be empty")
                return
            # basic sanity: no path separators
            if os.path.sep in name or os.path.altsep and os.path.altsep in name:
                messagebox.showerror("Error", "Invalid filename")
                return
            content = content_text.get("1.0", tk.END)
            try:
                add_protected_file(name, content)
            except Exception as e:
                messagebox.showerror("Error", str(e))
                return
            self.refresh_list()
            self.app.set_status(f"Added {name}")
            popup.destroy()

        def choose_file():
            path = filedialog.askopenfilename(title="Choose file to add")
            if not path:
                return
            # populate filename and content
            try:
                with open(path, "r", encoding="utf-8") as rf:
                    data = rf.read()
            except Exception as e:
                messagebox.showerror("Error", f"Could not read file: {e}")
                return
            name_entry.delete(0, tk.END)
            name_entry.insert(0, os.path.basename(path))
            content_text.delete("1.0", tk.END)
            content_text.insert("1.0", data)

        ttk.Button(btn_frame, text="Create", command=create_and_close).pack(side="right")
        ttk.Button(btn_frame, text="Cancel", command=popup.destroy).pack(side="right", padx=(0,8))
        # file chooser
        ttk.Button(btn_frame, text="Choose File...", command=choose_file).pack(side="left")

    def on_delete(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        name = self.listbox.get(sel[0])
        ok = messagebox.askyesno("Confirm Delete", f'Do you want to delete "{name}" ?')
        if not ok:
            return
        try:
            delete_protected_file(name)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.app.set_status(str(e))
            return
        # clear displayed content if that file was open
        current = self.listbox.get(sel[0])
        if self.content.get("1.0", tk.END) and current == name:
            self.content.delete("1.0", tk.END)
        self.refresh_list()
        self.app.set_status(f"Deleted {name}")
