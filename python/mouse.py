"""
监听鼠标事件
"""
from pynput.mouse import Events
from threading import Thread


class MouseEvents(Thread):
    def __init__(self, caller=None, daemon=True):
        super().__init__(daemon=daemon)
        self.__caller = caller
        self.__mouse_events = Events()
        self.__mouseEventHandles = {
            "click": [],
            "move": [],
            "scroll": []
        }
        self.leftPressed = False

    def set_caller(self, caller):
        self.__caller = caller

    def listen(self, event):
        def inner(handle):
            assert event in self.__mouseEventHandles.keys(), "Event not supported"
            self.__mouseEventHandles[event].append(handle)

        return inner

    def __trigger(self, event: Events.Event, handlers: list):
        for handler in handlers:
            if self.__caller is not None:
                handler(self.__caller, event)
            else:
                handler(event)

    def __trigger_event(self, event: Events.Event):
        if isinstance(event, Events.Move):
            event_key = "move"
        elif isinstance(event, Events.Scroll):
            event_key = "scroll"
        else:
            event_key = "click"

        self.__trigger(event, self.__mouseEventHandles[event_key])

    def __dispatch(self, events: Events):
        for event in events:
            self.__trigger_event(event)

    def run(self):
        with self.__mouse_events as events:
            self.__dispatch(events)

