
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty, AliasProperty, BooleanProperty, OptionProperty
from kivy.metrics import dp

from kivy.uix.slider import Slider


Builder.load_string(
    """
<-Slider>:
    canvas:
        Color:
            rgb: 1, 1, 1
        BorderImage:
            border: self.border_horizontal if self.orientation == 'horizontal' else self.border_vertical
            pos: (self.x + self.padding, self.center_y - self.background_width / 2) if self.orientation == 'horizontal' else (self.center_x - self.background_width / 2, self.y + self.padding)
            size: (self.width - self.padding * 2, self.background_width) if self.orientation == 'horizontal' else (self.background_width, self.height - self.padding * 2)
            source: (self.background_disabled_horizontal if self.orientation == 'horizontal' else self.background_disabled_vertical) if self.disabled else (self.background_horizontal if self.orientation == 'horizontal' else self.background_vertical)
        Color:
            rgba: root.value_track_color if self.value_track and self.orientation == 'horizontal' else [1, 1, 1, 0]
        Line:
            width: self.value_track_width
            points: (self.x + self.padding) if self.direction == 'left' else self.value_pos[0], self.center_y - self.value_track_width / 2, self.value_pos[0] if self.direction == 'left' else (self.x + self.width - self.padding), self.center_y - self.value_track_width / 2
        Color:
            rgba: root.value_track_color if self.value_track and self.orientation == 'vertical' else [1, 1, 1, 0]
        Line:
            width: self.value_track_width
            points: self.center_x, self.y + self.padding, self.center_x, self.value_pos[1]
        Color:
            rgb: 1, 1, 1
    Image:
        pos: (root.value_pos[0] - root.cursor_width / 2, root.center_y - root.cursor_height / 2) if root.orientation == 'horizontal' else (root.center_x - root.cursor_width / 2, root.value_pos[1] - root.cursor_height / 2)
        size: root.cursor_size
        source: root.cursor_disabled_image if root.disabled else root.cursor_image


<ViewSlider>
    id: slider

    Card:
        id: hint_box
        size_hint: None, None
        background_color: root.hint_bgcolor if root.active else [0, 0, 0, 0]
        elevation: 0 if slider._is_off else (4 if root.active else 0)
        size:
            (dp(12), dp(12)) if root.disabled else ((dp(28), dp(28)) \
            if root.active else (dp(20), dp(20)))
        pos:
            (slider.value_pos[0] - dp(14), slider.center_y - hint_box.height / 2 + dp(30)) \
            if slider.orientation == 'horizontal' \
            else (slider.center_x - hint_box.width / 2 + dp(30), \
            slider.value_pos[1] - dp(8))
        Label:
            text: str(int(slider.value))
            halign: "center"
            color: root.hint_color if root.active else [0, 0, 0, 0]

<Card>
    canvas:
        Color:
            rgba: self.background_color
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: [dp(3)]
	background_color: [1, 1, 1, 0]

"""
)

class Card(BoxLayout):
    pass

class ViewSlider(Slider):
    # Direction of the slider
    direction = OptionProperty("left", options=["left", "right"])

    # If the slider is clicked
    active = BooleanProperty(False)
 
    # If True, then the current value is displayed above the slider
    hint = BooleanProperty(True)
    hint_color = ListProperty([0, 0, 0, 1])
    hint_bgcolor = ListProperty([1, 1, 1, 1])

    # Show the "off" ring when set to minimum value
    show_off = BooleanProperty(True)

    # Internal state of ring
    _is_off = BooleanProperty(False)

    # Internal adjustment to reposition sliders for ring
    _offset = ListProperty((0, 0))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_hint(self, instance, value):
        if not value:
            self.remove_widget(self.ids.hint_box)

    def on_value_normalized(self, *args):
        """ When the value == min set it to "off" state and make slider a ring """

        self._update_is_off()

    def on_show_off(self, *args):
        self._update_is_off()

    def _update_is_off(self):
        self._is_off = self.show_off and (self.value_normalized == 0)

    def on__is_off(self, *args):
        self._update_offset()

    def on_active(self, *args):
        self._update_offset()

    def _update_offset(self):
        """Offset is used to shift the sliders so the background color
        shows through the off circle."""

        d = 2 if self.active else 0
        self._offset = (dp(11 + d), dp(11 + d)) if self._is_off else (0, 0)

    def _get_norm_value(self):

        vmin = self.min
        d = self.max - vmin
        if d == 0:
            return 0

        # direction add
        if self.direction == 'right':
            return 1 - (self.value - vmin) / float(d)
        else:
            return (self.value - vmin) / float(d)

    def _set_norm_value(self, value):

        vmin = self.min
        vmax = self.max
        step = self.step
        val = min(value * (vmax - vmin) + vmin, vmax)

        if step == 0:
            self.value = val
        else:
            self.value = min(round((val - vmin) / step) * step + vmin, vmax)

        # direction add
        if self.direction == 'right':
            self.value = vmax - self.value + vmin

    value_normalized = AliasProperty(_get_norm_value, _set_norm_value,
                                     bind=('value', 'min', 'max','direction'),
                                     cache=True)

 
    def on_touch_down(self, touch):
        if super().on_touch_down(touch):
            self.active = True

    def on_touch_up(self, touch):
        if super().on_touch_up(touch):
            self.active = False


if __name__ == "__main__":
    from kivy.app import App
    from kivy.config import Config
    Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

    class SliderApp(App):
        def build(self):
            return Builder.load_string(
                """
#:import hex kivy.utils.get_color_from_hex
Screen
    name: 'ViewSlider Example'
    BoxLayout:
        orientation:'vertical'
        padding: '8dp'
        Label:
            text: "Slider with [b]direction = 'left'[/b]"
            markup: True
            halign: "center"
        ViewSlider:
            min: 1
            max: 100
            value: 40
            value_track: True
            value_track_color: hex('#3F575F')
            size_hint_x: 0.8
            pos_hint:{'center_x':0.5}
            hint_color: hex('#d3d3d3')
            hint_bgcolor: hex('#303030')

        Label:
            text: "Slider with [b]direction = 'right'[/b]"
            markup: True
            halign: "center"
        ViewSlider:
            min: -10
            max: 100
            value: 40
            direction: 'right'
            value_track: True
            value_track_color: hex('#3F575F')
            size_hint_x: 0.8
            pos_hint:{'center_x':0.5}
"""
            )

    SliderApp().run()