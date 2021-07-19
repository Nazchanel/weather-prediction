import datetime
import matplotlib.pyplot as plt
import meteostat
import pandas as pd
import numpy as np
import tensorflow as tf
from keras.layers import MaxPooling2D, Conv2D, Flatten, concatenate, Dense
from tensorflow.keras import *
from keras import Model
import geocoder
import tkinter as tk
from tkinter.font import Font
from meteostat import Normals, units, Daily

posi = geocoder.ip('me').latlng


# Get Location and Time
def location_time(a, b):
    s = datetime.datetime(1970, 1, 1)
    e = datetime.datetime.now()
    p = meteostat.Point(a, b)

    return s, e, p


# Get desired data
def setup_data(s, e, p):
    d = meteostat.Daily(p, s, e)
    # d = d.convert(units.imperial)
    d = pd.DataFrame(d.fetch())
    d = d[["tavg", "prcp", "wspd", "pres"]].dropna()

    a = d[["tavg", "prcp", "wspd", "pres"]].iloc[:-2]
    b = d["tavg"].iloc[1:-1]

    return a, b, d


# Create AI
def nn_model(a, b, p):

    m = Sequential([

        layers.Dense(units=120, activation="tanh", input_shape=(4,)),
        layers.Dropout(.2),
        layers.Dense(units=64, activation="tanh"),
        layers.Dense(units=32, activation="tanh"),
        layers.Dense(units=32, activation="tanh"),
        layers.Dense(units=16, activation="tanh"),
        layers.Dense(units=1, activation="relu"),

    ])

    m.compile(optimizer=tf.optimizers.Adam(learning_rate=0.4), loss='LogCosh')
    m.fit(x=a, y=b, epochs=10)
    print(m.summary())
    return m.predict(p)


# Graph Data
def graph_data(data):
    plt.plot(data)
    plt.show()


def create_prediction():
    prediction = 0.0
    while prediction == 0.0:
        start, end, point = location_time(float(xcoord.get()), float(ycoord.get()))
        X, y, data = setup_data(start, end, point)
        z = meteostat.Daily(point, end - datetime.timedelta(days=1), end)
        # z = z.convert(units.imperial)
        z = z.fetch()
        z = z[["tavg", "prcp", "wspd", "pres"]]
        z = nn_model(X, y, z)
        prediction = z[0][0]
    predlabel.configure(text=f"Prediction: {str((prediction * (9/5) + 32))[:5]}° F")


def reset_position():
    xpos = posi[0]
    ypos = posi[1]
    xcoord.delete(0, 'end')
    xcoord.insert(0, xpos)
    ycoord.delete(0, 'end')
    ycoord.insert(0, ypos)


if __name__ == '__main__':
    window = tk.Tk()
    window.geometry("400x250")
    bgimage = tk.PhotoImage(file="bg.png")
    bg = tk.Label(image=bgimage)
    bg.place(x=-2, y=-1)
    window.title("WeatherPrediction")

    font1 = tk.font.Font(family="Georgia", weight="bold", slant="italic", size=15)
    font2 = tk.font.Font(family="Georgia", weight="normal", slant="italic", size=12)
    font3 = tk.font.Font(family="Georgia", weight="bold", slant="italic", size=12)

    title = tk.Label(text="Coordinates for prediction", font=font1, bg="#E2E50B", padx=0, pady=0)

    xlabel = tk.Label(text="Lattitude", bg="#BBBD35", font=font2, padx=2, pady=2)
    xcoord = tk.Entry(font=font2, bg="#BBBD35", justify="center")
    xcoord.insert(0, posi[0])
    ylabel = tk.Label(text="Longitude", bg="#9E9F4C", font=font2, padx=2, pady=2)
    ycoord = tk.Entry(font=font2, bg="#9E9F4C", justify="center")
    ycoord.insert(0, posi[1])

    ogcb = tk.Button(text="Reset Coordinates", command=reset_position, bg="#494949", font=font3, relief=tk.FLAT, padx=2,
                     pady=2)

    predlabel = tk.Label("", bg="#73744E", font=font2)
    predbutton = tk.Button(text="Predict Weather", command=create_prediction, bg="#73744E", font=font3, relief=tk.FLAT,
                           padx=2, pady=2)

    create_prediction()

    title.pack()
    xlabel.pack()
    xcoord.pack()
    ylabel.pack()
    ycoord.pack()
    predlabel.pack()
    predbutton.pack()
    ogcb.pack()
    window.resizable(False, False)
    window.mainloop()
