import mediapipe as mp
from djitellopy.tello import Tello
import cv2
import time

debug = True # all indicators

drone = False # change camera to drone or web cam

global KD
global CD
global left_right_velocity, for_back_velocity, up_down_velocity, yaw_velocity
left_right_velocity, for_back_velocity, up_down_velocity, yaw_velocity = 0, 0, 0, 0

global speeds
speeds = 60
flying = False
KD = 0
CD = 0



if drone:
    me = Tello()
    me.connect()
    me.streamon()


#hand vision

def draw_lines():
    if debug:
        cv2.line(image, (int(width/6), 0), (int(width/6), height), (211, 0, 148), thickness=1)
        cv2.line(image, (width - int(width/6), 0), (width - int(width/6), height), (211, 0, 148), thickness=1)
        cv2.line(image, (0, int(height/5)), (width, int(height/5)), (211, 0, 148), thickness=1)
        cv2.line(image, (0, height - int(height/5)), (width, height - int(height/5)), (211, 0, 148), thickness=1)

def finger_cord():
    wrist_x = int(hand.landmark[mp_hands.HandLandmark.WRIST].x * width)
    wrist_y = int(hand.landmark[mp_hands.HandLandmark.WRIST].y * height)
    wrist_z = hand.landmark[mp_hands.HandLandmark.WRIST].z * -1
    thumb_x = int(hand.landmark[mp_hands.HandLandmark.THUMB_TIP].x * width)
    thumb_y = int(hand.landmark[mp_hands.HandLandmark.THUMB_TIP].y * height)
    thumb_z = hand.landmark[mp_hands.HandLandmark.THUMB_TIP].z * -1
    index_x = int(hand.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * width)
    index_y = int(hand.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * height)
    index_z = hand.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].z * -1
    middle_x = int(hand.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].x * width)
    middle_y = int(hand.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y * height)
    middle_z = hand.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].z * -1
    ring_x = int(hand.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].x * width)
    ring_y = int(hand.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].y * height)
    ring_z = hand.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].z * -1
    pinky_x = int(hand.landmark[mp_hands.HandLandmark.PINKY_TIP].x * width)
    pinky_y = int(hand.landmark[mp_hands.HandLandmark.PINKY_TIP].y * height)
    pinky_z = hand.landmark[mp_hands.HandLandmark.PINKY_TIP].z * -1
    handmid_x = int(hand.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].x * width)
    handmid_y = int(hand.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y * height)
    handmid_z = hand.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].z * -1
    return [
        [#0
            wrist_x,
            wrist_y,
            wrist_z
        ],
        [#1
            thumb_x,
            thumb_y,
            thumb_z
        ],
        [#2
            index_x,
            index_y,
            index_z
        ],
        [#3
            middle_x,
            middle_y,
            middle_z
        ],
        [#4
            ring_x,
            ring_y,
            ring_z
        ],
        [#5
            pinky_x,
            pinky_y,
            pinky_z
        ],
        [#6
            handmid_x,
            handmid_y,
            handmid_z
        ]
    ]

def fingers_check(list,any):
    array = [0,0,0,0,0]


    if hand_dots[1][0] > hand.landmark[mp_hands.HandLandmark.THUMB_CMC].x*width:
        array[0] = 1
        if debug:
            cv2.putText(image, "thumb", (hand_dots[1][0], hand_dots[1][1] - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), thickness=3)

    if hand_dots[2][1] > hand.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP].y*height:
        array[1] = 1
        if debug:
            cv2.putText(image, "index", (hand_dots[2][0], hand_dots[2][1] - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), thickness=3)

    if hand_dots[3][1] > hand.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y*height:
        array[2] = 1
        if debug:
            cv2.putText(image, "middle", (hand_dots[3][0], hand_dots[3][1] - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), thickness=3)

    if hand_dots[4][1] > hand.landmark[mp_hands.HandLandmark.RING_FINGER_PIP].y*height:
        array[3] = 1
        if debug:
            cv2.putText(image, "ring", (hand_dots[4][0], hand_dots[4][1] - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), thickness=3)

    if hand_dots[5][1] > hand.landmark[mp_hands.HandLandmark.PINKY_PIP].y*height:
        array[4] = 1
        if debug:
            cv2.putText(image, "pinky", (hand_dots[5][0], hand_dots[5][1] - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), thickness=3)

    return array

def check_frame(list):
    if hand_dots[6][0]>width-int(width/4):
        if debug:
            cv2.putText(image, "right", (int(width / 4-30), int(height / 2 - 110)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0),thickness=3)
        return "right"
    elif hand_dots[6][0] < int(width/4):
        if debug:
            cv2.putText(image, "left", (int(width / 4-30), int(height / 2 - 110)), cv2.FONT_HERSHEY_SIMPLEX, 1,(255, 255, 0), thickness=3)
        return "left"
    elif hand_dots[6][1] > height - int(height/3):
        if debug:
            cv2.putText(image, "down", (int(width / 4-30), int(height / 2 - 110)), cv2.FONT_HERSHEY_SIMPLEX, 1,(255, 255, 0), thickness=3)
        return "down"
    elif hand_dots[6][1] < int(height/3):
        if debug:
            cv2.putText(image, "up", (int(width / 4-30), int(height / 2 - 110)), cv2.FONT_HERSHEY_SIMPLEX, 1,(255, 255, 0), thickness=3)
        return "up"
    else:
        return 'none'

def hand_angle(list):
    lenght = (hand_dots[0][0]-hand_dots[3][0])/hand_dots[0][2]
    if lenght>360000000:
        if debug:
            cv2.putText(image, "right", (int(width / 4), int(height / 6)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0),thickness=3)
        return "right"
    elif lenght<-478326265:
        if debug:
            cv2.putText(image, "left", (int(width / 4), int(height / 6)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0),thickness=3)
        return "left"
    else:
        return "none"

def gestures(list):
    global CD, KD
    if fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
        if debug:
            cv2.putText(image, "backward", (int(width / 2)+90, int(height / 6)+10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0),thickness=3)
        return "backward"
    elif fingers[0] == 0 and fingers[1] == 0 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 1:
        if debug:
            cv2.putText(image, "forward", (int(width / 2)+65, int(height / 6)+10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0),thickness=3)
        return "forward"
    elif fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 1 and fingers[4] == 1:
        CD+=1
        KD = 0
        if CD >= 20:
            CD = -10
            KD = 0
            if debug:
                cv2.putText(image, "land", (int(width / 2)+65, int(height / 6)+10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0),thickness=3)
            return "land"
    elif fingers[1] == 0 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 1:
        CD+=1
        KD = 0
        if CD >= 20:
            CD = -10
            KD = 0
            if debug:
                cv2.putText(image, "flip", (int(width / 2)+65, int(height / 6)+10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0),thickness=3)
            return "flip"

def get_drone_info():
    if drone:
        battery = me.get_battery()
        height = me.get_height()
        speed_x = me.get_speed_x()
        speed_y = me.get_speed_y()
        speed_z = me.get_speed_z()
        speed = (speed_x + speed_y + speed_z)/1.5
        cv2.putText(image, f"B: {battery}", (int(width - 105), 25), cv2.FONT_HERSHEY_SIMPLEX, 1,(255, 255, 0), thickness=1)
        cv2.putText(image, f"S: {speed}", (int(width - 105), 53), cv2.FONT_HERSHEY_SIMPLEX, 1,(255, 255, 0), thickness=1)
        cv2.putText(image, f"H: {int(height)}", (int(width - 105), 80), cv2.FONT_HERSHEY_SIMPLEX, 1,(255, 255, 0), thickness=1)


#drone flight

def rotate(list):
    if h_frame == "right":
        return -speeds
    elif h_frame == "left":
        return speeds
    else:
        return 0

def up_dw(list):
    if h_frame == "down":
        return -speeds
    elif h_frame == "up":
        return speeds
    else:
        return 0

def gests(list):
    global speeds
    if gest == "forward":
        return speeds
    elif gest == "backward":
        return -speeds
    elif gest == "land":
        me.land()
    elif gest == "flip":
        me.flip_forward()
    else:
        return 0

def lef_rig(list):
    global speeds
    if h_angel == "right":
        return speeds
    elif h_angel == "left":
        return -speeds
    else:
        return 0

mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose


cap = cv2.VideoCapture(0)
with mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5) as face_detection:
    with mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.5) as hands:
        with mp_pose.Pose(min_detection_confidence=0.5,min_tracking_confidence=0.5) as pose:
            while True:


                if drone:
                    frame = me.get_frame_read().frame
                else:
                    ret,frame = cap.read()




                frame = cv2.flip(frame, 1)

                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False
                result_h = hands.process(image)
                result_p = pose.process(image)
                results_f = face_detection.process(image)
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                height, width, channels = image.shape

                draw_lines()

                get_drone_info()

                if results_f.detections:
                    for detection in results_f.detections:
                        #mp_drawing.draw_detection(image, detection)
                        pass

                if result_h.multi_hand_landmarks:
                    for num, hand in enumerate(result_h.multi_hand_landmarks):
                        KD+=1
                        if KD >= 10:
                            KD = 0
                            CD = 0

                        hand_dots = finger_cord()

                        fingers = fingers_check(hand_dots,hand)

                        h_frame = check_frame(hand_dots)

                        h_angel = hand_angle(hand_dots)

                        gest = gestures(fingers)


                        if drone:
                            yaw_velocity = rotate(h_frame)
                            up_down_velocity = up_dw(h_frame)
                            left_right_velocity = lef_rig(h_angel)
                            for_back_velocity = gests(gest)
                            me.send_rc_control(left_right_velocity, for_back_velocity, up_down_velocity, yaw_velocity)
                            time.sleep(0.05)


                        mp_drawing.draw_landmarks(image, hand, mp_hands.HAND_CONNECTIONS)


                #mp_drawing.draw_landmarks(image,result_p.pose_landmarks,mp_pose.POSE_CONNECTIONS,landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())

                cv2.imshow('Hand capture', image)

                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break

frame.release()
cv2.destroyAllWindows()