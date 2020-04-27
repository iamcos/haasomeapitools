from kivy.app import App
from BaseHaas import Haas
from botsellector import BotSellector
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scatter import Scatter
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty)
from kivy.vector import Vector
from kivy.clock import Clock
from random import randint
import random
from kivy.properties import ListProperty

class HaasData(Widget):
    pass

class ScatterTextWidget(BoxLayout):

    text_colour = ListProperty([1,0,0,1])
    def change_label_color(self, *args):
        colour = [random.random() for i in range(3)] + [1]
        label = self.ids['my_label']
        label.color = colour
        self.text_colour = colour

class HaasApp(App):
    def build(self):
        return ScatterTextWidget()

        # return b
def some_function(*args):
    print('text changed')
if __name__ == "__main__":
    HaasApp().run()
