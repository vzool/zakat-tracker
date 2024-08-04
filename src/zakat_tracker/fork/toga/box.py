from __future__ import annotations

from collections.abc import Iterable

from typing import Protocol
from toga.handlers import wrapped_handler

from toga import Widget


class OnPressHandler(Protocol):
    def __call__(self, widget: Box, /, **kwargs: Any) -> object:
        """A handler that will be invoked when a box is pressed.

        :param widget: The box that was pressed.
        :param kwargs: Ensures compatibility with arguments added in future versions.
        """

class Box(Widget):
    _MIN_WIDTH = 0
    _MIN_HEIGHT = 0

    def __init__(
        self,
        id: str | None = None,
        style: None = None,
        children: Iterable[Widget] | None = None,
        on_press: toga.widgets.box.OnPressHandler | None = None,
    ):
        """Create a new Box container widget.

        :param id: The ID for the widget.
        :param style: A style object. If no style is provided, a default style
            will be applied to the widget.
        :param children: An optional list of children for to add to the Box.
        :param on_press: An optional handler that will be invoked when the Box is pressed.
        """
        super().__init__(id=id, style=style)

        # Create a platform specific implementation of a Box
        self._impl = self.factory.Box(interface=self)
        self.on_press = on_press

        # Children need to be added *after* the impl has been created.
        self._children: list[Widget] = []
        if children is not None:
            self.add(*children)

    @property
    def enabled(self) -> bool:
        """Is the widget currently enabled? i.e., can the user interact with the widget?

        Box widgets cannot be disabled; this property will always return True; any
        attempt to modify it will be ignored.
        """
        return True

    @enabled.setter
    def enabled(self, value: bool) -> None:
        pass

    def focus(self) -> None:
        """No-op; Box cannot accept input focus."""
        pass

    @property
    def on_press(self) -> OnPressHandler:
        """The handler to invoke when the button is pressed."""
        return self._on_press

    @on_press.setter
    def on_press(self, handler: toga.widgets.box.OnPressHandler) -> None:
        self._on_press = wrapped_handler(self, handler)
