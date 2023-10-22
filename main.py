import os
import sys
import cv2
import pyautogui
import numpy as np
import mediapipe as mp
import constants as my_const
import variables as my_vars
import utilities as my_utils
from tkinter import *
from sys import exit

# doc
# MAKRIS VASILEIOS 5491
# ttps://mediapipe.readthedocs.io/en/latest/solutions/hands.html

"""
Hand Gestures - VLC matching:
LEFT_V_SIGN: Volume up
LEFT_SPIDERMAN_SIGN: Volume down
LEFT_FIST: mute
LEFT_OPEN_PALM: unmute
RIGHT_SPIDERMAN_SIGN: jump 5 secs backwards 
RIGHT_POINTER: jump 5 secs forward
BOTH_OPEN_PALMS: Pause / Play
"""
# print(mp.mediapipe.__path__)
my_utils.customLog(my_const.LOG_INFO, "Program started.")
# region #*Initializing Variables
widthCam, heightCam = 640, 480
hand_gesture = my_const.EMPTY_STRING
landMarkList = []
counter = {
    my_const.LEFT_V_SIGN: 0,
    my_const.LEFT_SPIDERMAN_SIGN: 0,
    my_const.LEFT_FIST: 0,
    my_const.LEFT_OPEN_PALM: 0,
    my_const.RIGHT_SPIDERMAN_SIGN: 0,
    my_const.RIGHT_POINTER: 0,
    my_const.BOTH_OPEN_PALMS: 0,
}

# initialize the mediapipe hands classs
mpHands = mp.solutions.hands

# endregion

# check if vlc is running and it's in the foreground
isVlcOpen = my_utils.checkIfVlcIsRunning()
isVlcFocused = my_utils.checkIfVlcIsFocused()
my_utils.customLog(my_const.LOG_INFO, "isVlcOpen: % s" % isVlcOpen)
my_utils.customLog(my_const.LOG_INFO, "isVlcFocused: % s" % isVlcFocused)


# set up the handsVideos instance
handsVideos = mpHands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    model_complexity=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)


# initialize the mediapipe drawing class.
mpDrawing = mp.solutions.drawing_utils

# initialize the VideoCapture object to read from the webcam.
cameraVideo = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cameraVideo.set(3, heightCam)
cameraVideo.set(4, widthCam)


if not cameraVideo.isOpened():
    # display error notification
    my_utils.customLog(my_const.LOG_ERROR, my_const.CAMERA_ERROR_MESSAGE)
    my_utils.popupError(my_const.CAMERA_ERROR_MESSAGE)


with handsVideos as hands:
    # loop until the webcam is accessed successfully
    while cameraVideo.isOpened():
        cameraIsOk, frame = cameraVideo.read()
        # flip to selfie-view
        frame = cv2.flip(frame, 1)
        if cameraIsOk:
            isVlcFocused = my_utils.checkIfVlcIsFocused()
            if isVlcFocused:
                #   performance improvment
                frame.flags.writeable = False
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(frame)
                frame.flags.writeable = True
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                if results.multi_hand_landmarks:
                    detectedLandmarks = my_utils.detectHandsLandmarks(mpDrawing, mpHands, frame, hands)
                    hand_gesture = my_utils.newRecognizeGestures(mpHands, frame, results, display=False)
                    my_utils.customLog(my_const.LOG_INFO, "hands_gesture in main: % s" % (hand_gesture))
                    # * BOTH_OPEN_PALM
                    if hand_gesture == my_const.BOTH_OPEN_PALMS:
                        counter[my_const.BOTH_OPEN_PALMS] += 1
                        if counter[my_const.BOTH_OPEN_PALMS] == my_const.NUM_OF_FRAMES:
                            pyautogui.press(["space"])
                            counter[my_const.BOTH_OPEN_PALMS] = 0
                    # * LEFT_SPIDERMAN_SIGN
                    elif hand_gesture == my_const.LEFT_SPIDERMAN_SIGN:
                        counter[my_const.LEFT_SPIDERMAN_SIGN] += 1
                        if counter[my_const.LEFT_SPIDERMAN_SIGN] == my_const.NUM_OF_FRAMES:
                            with pyautogui.hold("ctrl"):
                                pyautogui.press(["down"])
                                pyautogui.press(["down"])

                            counter[my_const.LEFT_SPIDERMAN_SIGN] = 0
                    # * LEFT_FIST
                    elif hand_gesture == my_const.LEFT_FIST:
                        counter[my_const.LEFT_FIST] += 1
                        if counter[my_const.LEFT_FIST] == my_const.NUM_OF_FRAMES:
                            pyautogui.press(["m"])
                            counter[my_const.LEFT_FIST] = 0
                    # * LEFT_OPEN_PALM
                    elif hand_gesture == my_const.LEFT_OPEN_PALM:
                        counter[my_const.LEFT_OPEN_PALM] += 1
                        if counter[my_const.LEFT_OPEN_PALM] == my_const.NUM_OF_FRAMES:
                            pyautogui.press(["m"])
                            counter[my_const.LEFT_OPEN_PALM] = 0
                    # * LEFT_V_SIGN
                    elif hand_gesture == my_const.LEFT_V_SIGN:
                        counter[my_const.LEFT_V_SIGN] += 1
                        if counter[my_const.LEFT_V_SIGN] == my_const.NUM_OF_FRAMES:
                            with pyautogui.hold("ctrl"):
                                pyautogui.press(["up"])
                                pyautogui.press(["up"])
                            counter[my_const.LEFT_V_SIGN] = 0
                    # * RIGHT_POINTER
                    elif hand_gesture == my_const.RIGHT_POINTER:
                        counter[my_const.RIGHT_POINTER] += 1
                        if counter[my_const.RIGHT_POINTER] == my_const.NUM_OF_FRAMES:
                            with pyautogui.hold("shift"):
                                pyautogui.press(["right"])
                            counter[my_const.RIGHT_POINTER] = 0
                    # * RIGHT_SPIDERMAN_SIGN
                    elif hand_gesture == my_const.RIGHT_SPIDERMAN_SIGN:
                        counter[my_const.RIGHT_SPIDERMAN_SIGN] += 1
                        if counter[my_const.RIGHT_SPIDERMAN_SIGN] == my_const.NUM_OF_FRAMES:
                            with pyautogui.hold("shift"):
                                pyautogui.press(["left"])
                            counter[my_const.RIGHT_SPIDERMAN_SIGN] = 0
                    else:
                        counter = my_utils.reset_counter(counter)
                else:
                    counter = my_utils.reset_counter(counter)
                    cv2.imshow(my_vars.windowName, frame)
            else:
                counter = my_utils.reset_counter(counter)
                cv2.putText(
                    frame,
                    ("Please bring VLC in the foreground."),
                    (5, 80),
                    cv2.FONT_HERSHEY_COMPLEX,
                    my_const.CV2_FONT_SIZE,
                    my_const.RED,
                    2,
                )
                isVlcFocused = my_utils.checkIfVlcIsFocused()
        else:
            # show error
            my_utils.customLog(my_const.LOG_ERROR, my_const.CAMERA_ERROR_MESSAGE)
            my_utils.popupError(my_const.CAMERA_ERROR_MESSAGE)
            break
        cv2.imshow(my_vars.windowName, frame)
        # if esc thenbreak the loop.
        if cv2.waitKey(5) & 0xFF == 27:
            break

# release the videoCapture  and close the windows.
cameraVideo.release()
cv2.destroyAllWindows()


def main():
    # if we 're running this script the do :..this..   # if __name__ == "__main__":
    main()


""" 
def resource_path(relative_path):
   # Get absolute path to resource, works for dev and for PyInstaller
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS2  # or without 2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path) """
