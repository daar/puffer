from ui.connection_tab import ConnectionTab
from ui.extrusion_calibration_tab import ExtrusionCalibrationTab


class TabManager:
    def __init__(self, tabs, app):
        self.tabs = tabs
        self.app = app
        self.tab_classes = []

    def register_tab(self, tab_class, name):
        self.tab_classes.append((tab_class, name))

    def create_tabs(self):
        for tab_class, name in self.tab_classes:
            tab_class(self.tabs, self.app, name)


def setup_tabs(tabs, app):
    manager = TabManager(tabs, app)
    manager.register_tab(ConnectionTab, "Connection")
    manager.register_tab(ExtrusionCalibrationTab, "Extrusion Calibration")
    manager.create_tabs()
