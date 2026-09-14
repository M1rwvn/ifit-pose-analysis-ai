from flask import Flask, render_template, Response
import cv2
import numpy as np
from ultralytics import YOLO
import threading
import pyttsx3
import queue
import time

app = Flask(__name__)

model = YOLO('yolo11n-pose.pt')
cap = cv2.VideoCapture(0)

# Globals
up_thresh = 150
down_thresh = 90
push_down = False
push_counter = 0

left_up = False
right_up = False
left_counter = 0
right_counter = 0

combine_down = False
combine_counter = 0

mode = 'normal'  # normal, combine, pushup
engine = pyttsx3.init()
speech_queue = queue.Queue()


def speak(text):
    speech_queue.put(text)

def worker_speak():
    while True:
        text = speech_queue.get()
        if text is None:
            break
        engine.say(text)
        engine.runAndWait()

threading.Thread(target=worker_speak, daemon=True).start()

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    if angle > 180.0:
        angle = 360.0 - angle
    return angle

def gen_frames():
    global push_down, push_counter, left_up, right_up, left_counter, right_counter, combine_down, combine_counter, mode
    while True:
        success, frame = cap.read()
        if not success:
            break
        frame = cv2.resize(frame, (1020, 500))
        result = model.track(frame)

        if result[0].keypoints is not None:
            keypoints = result[0].keypoints.xy.cpu().numpy()
            for kp in keypoints:
                if len(kp) > 10:
                    left_shoulder = (int(kp[5][0]), int(kp[5][1]))
                    left_elbow = (int(kp[7][0]), int(kp[7][1]))
                    left_wrist = (int(kp[9][0]), int(kp[9][1]))

                    right_shoulder = (int(kp[6][0]), int(kp[6][1]))
                    right_elbow = (int(kp[8][0]), int(kp[8][1]))
                    right_wrist = (int(kp[10][0]), int(kp[10][1]))

                    left_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
                    right_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)

                    if mode == 'normal':
                        combine_counter = 0
                        if left_angle < down_thresh and not left_up:
                            left_up = True
                        elif left_angle > up_thresh and left_up:
                            left_counter += 1
                            left_up = False
                            speak(f'Left {left_counter}')

                        if right_angle < down_thresh and not right_up:
                            right_up = True
                        elif right_angle > up_thresh and right_up:
                            right_counter += 1
                            right_up = False
                            speak(f'Right {right_counter}')

                        cv2.putText(frame, f"Left: {left_counter}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                        cv2.putText(frame, f"Right: {right_counter}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                    elif mode == 'combine':
                        left_counter = 0
                        right_counter = 0
                        if left_angle < down_thresh and right_angle < down_thresh and not combine_down:
                            combine_down = True
                        elif left_angle > up_thresh and right_angle > up_thresh and combine_down:
                            combine_counter += 1
                            combine_down = False
                            speak(f'Combine {combine_counter}')

                        cv2.putText(frame, f"Combine: {combine_counter}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                    elif mode == 'pushup':
                        if left_angle < down_thresh and right_angle < down_thresh and not push_down:
                            push_down = True
                        elif left_angle > up_thresh and right_angle > up_thresh and push_down:
                            push_counter += 1
                            push_down = False
                            speak(f'Push up {push_counter}')

                        cv2.putText(frame, f"Pushups: {push_counter}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('train.html')

@app.route('/video')
def video():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/set_mode/<m>')
def set_mode(m):
    global mode
    if m in ['normal', 'combine', 'pushup']:
        mode = m
        speak(f"{mode} mode")
    return ('', 204)

@app.route('/reset')
def reset():
    global push_down, push_counter, left_up, right_up, left_counter, right_counter, combine_down, combine_counter
    push_down = False
    push_counter = 0
    left_up = False
    right_up = False
    left_counter = 0
    right_counter = 0
    combine_down = False
    combine_counter = 0
    speak("Counters reset")
    return ('', 204)

if __name__ == '__main__':
    app.run(debug=True)
