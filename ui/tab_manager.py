"""
Module for managing and initializing tabs in a Tkinter application.

This module defines the `TabManager` class, which handles the registration
and creation of tabs in a notebook widget. Additionally, it includes the
`setup_tabs` function to initialize specific tabs like `ConnectionTab` and
`ExtrusionCalibrationTab`.
"""

from ui.connection_tab import ConnectionTab
from ui.extrusion_calibration_tab import ExtrusionCalibrationTab


class TabManager:
    """
    A class to manage the creation and registration of tabs in a Tkinter notebook.

    The `TabManager` allows for registering tab classes along with their names,
    and then creates instances of those tabs in the provided notebook widget.

    Attributes:
        tabs (ttk.Notebook): The notebook widget where tabs will be added.
        app (Any): The main application instance providing shared resources and context.
        tab_classes (list): A list of tuples containing tab classes and their corresponding names.
    """

    def __init__(self, tabs, app):
        """
        Initialize the TabManager instance.

        Args:
            tabs (ttk.Notebook): The notebook widget to manage.
            app (Any): The main application instance.
        """
        self.tabs = tabs
        self.app = app
        self.tab_classes = []

    def register_tab(self, tab_class, name):
        """
        Register a tab class with a name.

        This method allows dynamic registration of tabs to be managed by the TabManager.

        Args:
            tab_class (type): The class representing the tab to be added.
            name (str): The display name for the tab.
        """
        self.tab_classes.append((tab_class, name))

    def create_tabs(self):
        """
        Create and add all registered tabs to the notebook.

        This method iterates through the registered tab classes and initializes
        each one with the notebook widget, application context, and tab name.
        """
        for tab_class, name in self.tab_classes:
            tab_class(self.tabs, self.app, name)


def setup_tabs(tabs, app):
    """
    Set up the tabs for the application using the TabManager.

    This function initializes a `TabManager`, registers the required tabs,
    and creates them in the provided notebook widget.

    Args:
        tabs (ttk.Notebook): The notebook widget where tabs will be added.
        app (Any): The main application instance providing shared resources.
    """
    manager = TabManager(tabs, app)
    manager.register_tab(ConnectionTab, "Connection")
    manager.register_tab(ExtrusionCalibrationTab, "Extrusion Calibration")
    manager.create_tabs()
