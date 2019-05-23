import time

import numpy as np
import pyautogui as pyautogui
from mss import mss
import threading
import cv2 as cv
from pynput import keyboard
import timeit

from directkeys import PressKeyPynput, W, A, S, D, ReleaseKeyPynput
import statistics


COMBINATIONS = [
    {keyboard.Key.shift, keyboard.KeyCode(char='a')}
]
COMBINATIONS2 = [
    {keyboard.Key.shift, keyboard.KeyCode(char='s')}
]
current = set()
driving = False
pressed = False
lower_color_bounds = (0, 28, 69)
upper_color_bounds = (2, 198, 247)
allvalue = 340
mean_min =allvalue
mean_max = allvalue
mean_ideal = allvalue
def drive():
    from pynput import keyboard
    global driving, pressed
    start = time.time()
    keyboardActuator = keyboard.Controller()
    driving = True
    previous_mean = 0

    with mss() as sct:
        while driving:
            time_now = time.time() - start
            if time_now > 250:
                ReleaseKeyPynput(W)
                driving = False
                pressed = False
                print("Driving over")
            array = np.array(pyautogui.screenshot())
            crop_img = array[300:350, 600:1600]
            converted = cv.cvtColor(crop_img, cv.COLOR_RGB2BGR)
            #cv.imshow("image", converted)
            #cv.waitKey()
            mask = cv.inRange(converted, lower_color_bounds, upper_color_bounds)
            pixelpoints = cv.findNonZero(mask)
            if pixelpoints is None:
                ReleaseKeyPynput(A)
                ReleaseKeyPynput(D)
                continue
            xs = [pixelpoint[0][0] for pixelpoint in pixelpoints]
            mean = statistics.median(xs)
            added_time = 0
            print(mean)
            #if previous_mean == 0:
            #    previous_mean = mean
            #else:
            #    added_time = (previous_mean - mean) / 10000
            if mean < mean_max:
                PressKeyPynput(A)
                time.sleep(abs(0.01 + abs((mean - mean_ideal) / 5000) + added_time))
                ReleaseKeyPynput(A)

            elif mean > mean_min:
                PressKeyPynput(D)
                time.sleep(abs(0.01 + abs((mean - mean_ideal) / 5400) + added_time))
                ReleaseKeyPynput(D)

            else:
                ReleaseKeyPynput(A)
                ReleaseKeyPynput(D)



def on_press(key):
    global pressed
    if any([key in COMBO for COMBO in COMBINATIONS]):
        current.add(key)
        if any(all(k in current for k in COMBO) for COMBO in COMBINATIONS):
            if not pressed:
                pressed = True
                xThread = threading.Thread(target=drive)
                xThread.start()

def on_release(key):
    pass

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()