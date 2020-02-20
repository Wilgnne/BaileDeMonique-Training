import npyscreen

class MultiLineBox(npyscreen.BoxTitle):
    # MultiLineEdit now will be surrounded by boxing
    _contained_widget = npyscreen.MultiLineEdit

class ProgressBarBox (npyscreen.BoxTitle):
    _contained_widget = npyscreen.SliderPercent