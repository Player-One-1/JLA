import pandas as pd
import PySimpleGUI as sg
from random import randint



df = pd.read_csv('base.csv', index_col=0)

i = randint(0,len(df)-1)

r = df.iloc[i]
# Define the window's contents
layout = [  [sg.Text(r['kanji'],size=(40, 1), font=('Arial Bold', 60))],     # Part 2 - The Layout
            [sg.Input(key="--1--")],
            [sg.Button('Ok')] ]

# Create the window
window = sg.Window('Window Title', layout)      # Part 3 - Window Defintion

# Display and interact with the Window
event, values = window.read()                   # Part 4 - Event loop or Window.read call


# Do something with the information gathered

if values["--1--"] == r['reading']:
    print("Ok, great success")
else:
    print("WRONG!!!")

# Finish up by removing from the screen
window.close()      