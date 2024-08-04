from rubicon.objc import objc_method
from travertino.size import at_least

from toga_cocoa.container import TogaView

from toga_cocoa.widgets.base import Widget


class Box(Widget):
    def create(self):
        self.native = TogaView.alloc().init()
        self.native.wantsLayer = True

        # Add the layout constraints
        self.add_constraints()

    @objc_method
    def onPress_(self, obj) -> None:
        self.interface.on_press()

    def rehint(self):
        content_size = self.native.intrinsicContentSize()
        self.interface.intrinsic.width = at_least(content_size.width)
        self.interface.intrinsic.height = at_least(content_size.height)
