import tkinter.ttk as ttk
from dashboard import read_events, summarize_events

class DashboardFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        ttk.Label(self, text="Dashboard", style="Header.TLabel").pack(anchor="w", pady=(8,12))

        self.kpis = ttk.Label(self, text="")
        self.kpis.pack(anchor="w")
        ttk.Button(self, text="Refresh", command=self.load_summary).pack(anchor="w", pady=(6,0))
        ttk.Button(self, text="Back", command=self.app.show_files).pack(anchor="w", pady=(6,0))
        self.load_summary()

    def load_summary(self):
        ev = read_events()
        s = summarize_events(ev)
        text = (
            f"Logins: {s['logins']}\n"
            f"Failed Attempts: {s['failed_attempts']}\n"
            f"Freeze Events: {s['freeze_events']}\n"
        )
        self.kpis.config(text=text)
