import cv2
import json
import math
import pathlib
import time
import art
from art import *


# Define the video file path
import  tkinter as tk
from tkinter import filedialog
root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename()
# path of this script
directory = "Nitral-VideoMocap2Funscipt\Input\input.mp4"
# Define the output .funscript file path
output_path = 'Nitral-VideoMocap2Funscipt\Output\output.funscript'

# Open the video file
video = cv2.VideoCapture(file_path)

# Print the video FPS
print("###########################################################################")
tprint("Nitral MoCap")
print("###########################################################################")
print(file_path)
print("Video FPS:", video.get(cv2.CAP_PROP_FPS))

# Check if the video FPS is zero
if video.get(cv2.CAP_PROP_FPS) == 0:
    print("Error: video FPS is zero")
else:
    # Initialize motion list to store motion data
    motions = []

    # Define a mapping function to map x and y coordinates to corresponding values in the .funscript format
    def map_to_funscript(x, y):
        x_mapped = int((x / width) * 99)
        y_mapped = int(99 - (y / height) * 99)
        return x_mapped, y_mapped

    # Get the width and height of the video frame
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Set the video fps as the duration of each frame in the .funscript file
    duration = 1 / video.get(cv2.CAP_PROP_FPS)

    # Print the Frame duration
    print("Frame Duration:", duration)

    
    

    # Use a loop to process each frame of the video
    while True:

        # Capture the next frame from the video
        ret, frame = video.read()

        # Break the loop if there are no more frames
        if not ret:
            break

        # Convert the frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (15, 15), 0)

        # Set the current frame as the reference frame
        if not 'reference' in locals():
            reference = blurred
            continue

        # Calculate the difference between the current frame and the reference frame
        delta = cv2.absdiff(reference, blurred)

        # Apply threshold to the delta frame
        thresh = cv2.threshold(delta, 30, 255, cv2.THRESH_BINARY)[1]

        # Find contours in the thresholded image
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Find the largest contour
        if contours:
            motion = max(contours, key=cv2.contourArea)

            # Calculate the center of the motion
            M = cv2.moments(motion)
            if M["m00"] == 0:
                center = (0, 0)
            else:
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            # Add the mapped center to the motion list
            x, y = map_to_funscript(center[0], center[1])
            motions.append((x, y, 0))

        # Update the reference frame
        reference = blurred

    # Release the video
    video.release()

    # Convert the motion list to a dictionary with the required keys for the .funscript format
    funscript = {
        "Version":1.0,
        "range":100,
        "inverted":False,
        "bookmark":0,
        "graphDuration":11628,
        "lastPosition":0, #wtf is this Original Value 7313646973
        "injectionBias":0.0,
        "speedRatio": 1.0,
        "scriptingMode":1,
        "simulatorPresets":[{"name":"Simulator 1"}],
        "direction":1,
        "actions": [
            {"pos": motion[0], "at": math.trunc( i * duration * 1000)} for i, motion in enumerate(motions)
        ]
    }

    # Save the .funscript file as a JSON file
    with open(output_path, 'w') as f:
        json.dump(funscript, f)
print(output_path)        
