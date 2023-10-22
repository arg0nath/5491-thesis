import ctypes
import math
import cv2
import psutil
import constants as my_const
import variables as my_vars
import webbrowser

from tkinter import messagebox
from tkinter import *
from sys import exit


import logging


def popupError(errorMessage):
    popupRoot = Tk()
    popupRoot.title(my_vars.windowName)
    popupRoot.after(10000, popupRoot.destroy)
    popupLabel = Label(popupRoot, text=errorMessage, font=("Verdana", 11), anchor="center")
    popupLabel.pack()
    popupRoot.geometry("400x50+800+500")
    popupRoot.mainloop()


def checkIfVlcIsRunning():
    for p in psutil.process_iter(["name"]):
        if p.info["name"] == "vlc.exe":
            return True
    return False


def checkIfVlcIsFocused():
    """
    This function checks if VLC is focused (is in the foreground).
    """
    user32 = ctypes.windll.user32
    active_window_title = ctypes.create_unicode_buffer(1024)
    user32.GetWindowTextW(user32.GetForegroundWindow(), active_window_title, len(active_window_title))
    return "VLC" in active_window_title.value


def customLog(logLevel, message):
    """
    This function prints custom logs on the console, using different colors depending on the log level.
    INFO -> green
    WARNING -> yellow
    ERROR -> red
    """
    logging.basicConfig(format="myLog %(levelname)s: %(message)s", level=logging.INFO)
    if logLevel == logging.INFO:
        logging.info(my_const.LOG_GREEN_LETTERS_START + str(message) + my_const.LOG_LETTERS_END)
    elif logLevel == logging.WARNING:
        logging.warning(my_const.LOG_YELLOW_LETTERS_START + str(message) + my_const.LOG_LETTERS_END)
    elif logLevel == logging.ERROR:
        logging.error(my_const.LOG_RED_LETTERS_START + str(message) + my_const.LOG_LETTERS_END)


def detectHandsLandmarks(mpDrawing, mpHands, image, hands):
    results = hands.process(image)
    # check if landmarks are found
    if results.multi_hand_landmarks:
        # for each hand found
        for hand_landmarks in results.multi_hand_landmarks:
            # draw landmarks
            mpDrawing.draw_landmarks(
                image=image,
                landmark_list=hand_landmarks,
                connections=mpHands.HAND_CONNECTIONS,
                landmark_drawing_spec=mpDrawing.DrawingSpec(color=(255, 255, 255), thickness=2, circle_radius=2),
                connection_drawing_spec=mpDrawing.DrawingSpec(
                    color=(0, 255, 0),
                    thickness=2,
                    circle_radius=2,
                ),
            )
    return results


def newRecognizeGestures(mpHands, image, results, draw=True, display=True):
    isFist = False
    count = {my_const.RIGHT_STRING: 0, my_const.LEFT_STRING: 0}
    fingersTipsIds = [
        mpHands.HandLandmark.INDEX_FINGER_TIP,
        mpHands.HandLandmark.MIDDLE_FINGER_TIP,
        mpHands.HandLandmark.RING_FINGER_TIP,
        mpHands.HandLandmark.PINKY_TIP,
    ]
    fingersStatuses = {
        # Right hand
        my_const.RIGHT_THUMB_STRING: False,
        my_const.RIGHT_INDEX_STRING: False,
        my_const.RIGHT_MIDDLE_STRING: False,
        my_const.RIGHT_RING_STRING: False,
        my_const.RIGHT_PINKY_STRING: False,
        # Left hand
        my_const.LEFT_THUMB_STRING: False,
        my_const.LEFT_INDEX_STRING: False,
        my_const.LEFT_MIDDLE_STRING: False,
        my_const.LEFT_RING_STRING: False,
        my_const.LEFT_PINKY_STRING: False,
    }
    hands_gesture = my_const.EMPTY_STRING
    for handIndex, handInfo in enumerate(results.multi_handedness):
        # get the label of the found hand.
        handLabel = handInfo.classification[0].label
        handLandmarks = results.multi_hand_landmarks[handIndex]
        # for each finger tip
        for tipIndex in fingersTipsIds:
            fingerName = tipIndex.name.split("_")[0]
            if handLandmarks.landmark[tipIndex].y < handLandmarks.landmark[tipIndex - 2].y:
                fingersStatuses[handLabel.upper() + "_" + fingerName] = True
                count[handLabel.upper()] += 1
            isFist = all(handLandmarks.landmark[tipIndex].y < handLandmarks.landmark[0].y and handLandmarks.landmark[tipIndex].y > handLandmarks.landmark[tipIndex - 2].y for tipIndex in fingersTipsIds)
        # x-coordinates of the tip and mcp of the thumb
        thumb_tip_x = handLandmarks.landmark[mpHands.HandLandmark.THUMB_TIP].x
        thumb_mcp_x = handLandmarks.landmark[mpHands.HandLandmark.THUMB_TIP - 2].x
        # if the thumb is up
        if (handLabel.upper() == my_const.RIGHT_STRING and (thumb_tip_x < thumb_mcp_x)) or (handLabel.upper() == my_const.LEFT_STRING and (thumb_tip_x > thumb_mcp_x)):
            # update the status of the thumb in the dictionary to true.
            fingersStatuses[handLabel.upper() + "_THUMB"] = True
            # increase count of the fingers up of the hand by 1.
            count[handLabel.upper()] += 1

    if draw:
        # show the total count of the fingers of both hands on the output
        cv2.putText(image, ("Total Fingers: % s" % str(sum(count.values()))), (5, 25), cv2.FONT_HERSHEY_COMPLEX, my_const.CV2_FONT_SIZE, my_const.GREEN, 2)
        if count[my_const.LEFT_STRING] > 0 and count[my_const.RIGHT_STRING] > 0:
            cv2.putText(image, ("Hand_label: Left & Right"), (5, 50), cv2.FONT_HERSHEY_COMPLEX, my_const.CV2_FONT_SIZE, my_const.GREEN, 2)
        elif count[my_const.LEFT_STRING] == 0 and count[my_const.RIGHT_STRING] > 0:
            cv2.putText(image, ("Hand_label: Right"), (5, 50), cv2.FONT_HERSHEY_COMPLEX, my_const.CV2_FONT_SIZE, my_const.GREEN, 2)
        elif count[my_const.LEFT_STRING] > 0 and count[my_const.RIGHT_STRING] == 0:
            cv2.putText(image, ("Hand_label: Left"), (5, 50), cv2.FONT_HERSHEY_COMPLEX, my_const.CV2_FONT_SIZE, my_const.GREEN, 2)
        else:
            cv2.putText(image, ("Hand_label: Empty"), (5, 50), cv2.FONT_HERSHEY_COMPLEX, my_const.CV2_FONT_SIZE, my_const.GREEN, 2)
    hands_gesture = my_const.EMPTY_STRING
    if count[my_const.RIGHT_STRING] == 1 and fingersStatuses[my_const.RIGHT_INDEX_STRING]:
        isFist = False
        hands_gesture = my_const.RIGHT_POINTER
    elif count[my_const.LEFT_STRING] == 2 and fingersStatuses["LEFT_MIDDLE"] and fingersStatuses[my_const.LEFT_INDEX_STRING]:
        isFist = False
        hands_gesture = my_const.LEFT_V_SIGN
    elif count[my_const.RIGHT_STRING] == 3 and fingersStatuses[my_const.RIGHT_THUMB_STRING] and fingersStatuses[my_const.RIGHT_INDEX_STRING] and fingersStatuses[my_const.RIGHT_PINKY_STRING]:
        isFist = False
        hands_gesture = my_const.RIGHT_SPIDERMAN_SIGN
    elif count[my_const.LEFT_STRING] == 3 and fingersStatuses[my_const.LEFT_THUMB_STRING] and fingersStatuses[my_const.LEFT_INDEX_STRING] and fingersStatuses[my_const.LEFT_PINKY_STRING]:
        isFist = False
        hands_gesture = my_const.LEFT_SPIDERMAN_SIGN
    elif handLabel.upper() == my_const.LEFT_STRING and isFist:
        hands_gesture = my_const.LEFT_FIST
    elif count[my_const.RIGHT_STRING] + count[my_const.LEFT_STRING] == 10:
        isFist = False
        hands_gesture = my_const.BOTH_OPEN_PALMS
    elif count[my_const.LEFT_STRING] == 5 and count[my_const.RIGHT_STRING] == 0:
        isFist = False
        hands_gesture = my_const.LEFT_OPEN_PALM
    else:
        isFist = False
        hands_gesture = my_const.EMPTY_STRING
    cv2.putText(image, ("Hands_gesture: % s" % hands_gesture), (5, 150), cv2.FONT_HERSHEY_COMPLEX, my_const.CV2_FONT_SIZE, my_const.GREEN, 2)
    return hands_gesture


def reset_counter(counter):
    if any(value != 0 for value in counter.values()):
        customLog(my_const.LOG_ERROR, "reset_counter")
        for key in counter:
            counter[key] = 0
    return counter
