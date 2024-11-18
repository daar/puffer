from tkinter import ttk


class BaseTab:
    def __init__(self, tabs, app, tab_name):
        self.tabs = tabs
        self.app = app
        self.tab_name = tab_name
        self.frame = ttk.Frame(self.tabs)
        self.tabs.add(self.frame, text=self.tab_name)
