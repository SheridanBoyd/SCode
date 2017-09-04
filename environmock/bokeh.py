from bokeh.io import curdoc
from bokeh.models import Div, Button

def click():
    global div
    div.text = 'stuff'

div = Div(text = 'hello world')

btn = Button(label='stuff')
btn.on_click(click)

curdoc().add_root(div, btn)