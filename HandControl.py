from djitellopy.tello import Tello
from threading import Thread
import mediapipe as mp
import keyboard
import cv2
import time

#/////////////////////////////////////////////////////////////////
global debug, drone, control
debug = True # Shows camera indicators
drone = False # Switch notebook cam and drone
control = True # Control drone with keypad
#/////////////////////////////////////////////////////////////////
#global rc
global left_right_velocity, for_back_velocity, up_down_velocity, yaw_velocity
left_right_velocity, for_back_velocity, up_down_velocity, yaw_velocity = 0,0,0,0
#/////////////////////////////////////////////////////////////////
#globals
#var of drone speed
global d_speed
d_speed = 50

global CD, KD
CD, KD = 0, 0
#/////////////////////////////////////////////////////////////////


cap = cv2.VideoCapture(0)

class Hand(Tello):
    import mediapipe as mp
    def __init__(self):
        Tello.__init__(self)
        self.hands = mp.solutions.hands.Hands(False, 4, 1, 0.8, 0.5)

        if drone:
            self.connect()
            self.streamon()
            self.image = self.get_frame_read().frame
        else:
            self.ret, self.image = cap.read()
        self.height, self.width, self.channel = self.image.shape
        self.fingis = [0,0,0,0,0]


        self.cam_thread = Thread(target=self.output_cam).start()

    def output_cam(self):
        global KD, CD, left_right_velocity, for_back_velocity, up_down_velocity, yaw_velocity
        while True:
            if drone:
                self.image = self.get_frame_read().frame
            else:
                self.ret, self.image = cap.read()

            self.image = cv2.flip(self.image, 1)

            self.fingis = [0,0,0,0,0]


            self.myHands, self.handsType = self.Marks()


            if len(self.myHands) != 0:
                KD += 1
                if KD >= 10:
                    KD = 0
                    CD = 0
                if debug:
                    self.draw_hands()
                self.finger_check()
                if drone:
                    self.gestures()
                    self.sides()
                    self.frame_check()
            else:
                left_right_velocity = 0
                up_down_velocity = 0
                for_back_velocity = 0
                yaw_velocity = 0

            if drone:
                self.get_drone_info()

            self.draw_lines()

            cv2.imshow('Tello', self.image)
            cv2.waitKey(1)

    def draw_lines(self):
        if debug:
            cv2.line(self.image, (int(self.width / 6), 0), (int(self.width / 6), self.height), (211, 0, 148), thickness=1)
            cv2.line(self.image, (self.width - int(self.width / 6), 0), (self.width - int(self.width / 6), self.height), (211, 0, 148), thickness=1)
            cv2.line(self.image, (0, int(self.height / 5)), (self.width, int(self.height / 5)), (211, 0, 148), thickness=1)
            cv2.line(self.image, (0, self.height - int(self.height / 5)), (self.width, self.height - int(self.height / 5)), (211, 0, 148), thickness=1)

    def draw_hands(self):
        for han in range(len((self.myHands))):
            cv2.circle(self.image, (self.myHands[han][9][0],self.myHands[han][4][1]), 10, (255,0,0), 3)

    def finger_check(self):
        for han in range(len((self.myHands))):
            if self.handsType[han] == 'Right':
                if self.myHands[han][4][0] > self.myHands[han][1][0]:
                    self.fingis[0] = 1
                    if debug:
                        cv2.putText(self.image, "thumb", (self.myHands[han][4][0], self.myHands[han][4][1] - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), thickness=2)
            elif self.handsType[han] == 'Left':
                if self.myHands[han][4][0] < self.myHands[han][1][0]:
                    self.fingis[0] = 1
                    if debug:
                        cv2.putText(self.image, "thumb", (self.myHands[han][4][0], self.myHands[han][4][1] - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), thickness=2)

            if self.myHands[han][8][1] > self.myHands[han][6][1]:
                self.fingis[1] = 1
                if debug:
                    cv2.putText(self.image, "index", (self.myHands[han][8][0], self.myHands[han][8][1] - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), thickness=2)

            if self.myHands[han][12][1] > self.myHands[han][10][1]:
                self.fingis[2] = 1
                if debug:
                    cv2.putText(self.image, "midle", (self.myHands[han][12][0], self.myHands[han][12][1] - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), thickness=2)

            if self.myHands[han][16][1] > self.myHands[han][14][1]:
                self.fingis[3] = 1
                if debug:
                    cv2.putText(self.image, "ring", (self.myHands[han][16][0], self.myHands[han][16][1] - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), thickness=2)

            if self.myHands[han][20][1] > self.myHands[han][18][1]:
                self.fingis[4] = 1
                if debug:
                    cv2.putText(self.image, "pinky", (self.myHands[han][20][0], self.myHands[han][20][1] - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), thickness=2)


    def Marks(self):
        myHands = []
        handsType = []
        frameRGB = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frameRGB)
        if results.multi_hand_landmarks != None:
            for hand in results.multi_handedness:
                handType = hand.classification[0].label
                handsType.append(handType)
            for handLandMarks in results.multi_hand_landmarks:
                myHand = []
                for landMark in handLandMarks.landmark:
                    myHand.append((int(landMark.x * self.width), int(landMark.y * self.height), landMark.z))
                myHands.append(myHand)
        return myHands, handsType


    def get_drone_info(self):
        if drone:
            battery = self.get_battery()
            height = self.get_height()
            speed_x = self.get_speed_x()
            speed_y = self.get_speed_y()
            speed_z = self.get_speed_z()
            speed = (speed_x + speed_y + speed_z) / 1.5
            cv2.putText(self.image, f"B: {battery}", (int(self.width - 105), 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), thickness=1)
            cv2.putText(self.image, f"S: {speed}", (int(self.width - 105), 53), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), thickness=1)
            cv2.putText(self.image, f"H: {int(height)}", (int(self.width - 105), 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), thickness=1)

    def gestures(self):
        global CD, KD, for_back_velocity, d_speed
        if self.fingis[1] == 1 and self.fingis[2] == 0 and self.fingis[3] == 0 and self.fingis[4] == 0:
            for_back_velocity = -d_speed
            if debug:
                cv2.putText(self.image, "backward", (int(self.width / 2) + 90, int(self.height / 6) + 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), thickness=2)
        elif self.fingis[1] == 0 and self.fingis[2] == 1 and self.fingis[3] == 1 and self.fingis[4] == 1:
            for_back_velocity = d_speed
            if debug:
                cv2.putText(self.image, "forward", (int(self.width / 2) + 65, int(self.height / 6) + 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), thickness=2)
        elif self.fingis[0] == 0 and self.fingis[1] == 1 and self.fingis[2] == 1 and self.fingis[3] == 1 and self.fingis[4] == 1:
            CD += 1
            KD = 0
            if CD >= 20:
                CD = -10
                KD = 0
                if drone:
                    self.land()
                if debug:
                    cv2.putText(self.image, "land", (int(self.width / 2) + 65, int(self.height / 6) + 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), thickness=2)
        elif self.fingis[0] == 1 and self.fingis[1] == 0 and self.fingis[2] == 0 and self.fingis[3] == 0 and self.fingis[4] == 1:
            CD += 1
            KD = 0
            if CD >= 20:
                CD = -10
                KD = 0
                if drone:
                    self.flip_forward()
                if debug:
                    cv2.putText(self.image, "flip", (int(self.width / 2) + 65, int(self.height / 6) + 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), thickness=2)
        else:
            for_back_velocity = 0


    def sides(self):
        global d_speed, left_right_velocity
        lenght = (self.myHands[0][0][0]-self.myHands[0][12][0])/self.myHands[0][0][2]
        if lenght > 360000000:
            left_right_velocity = d_speed
            if debug:
                cv2.putText(self.image, "right", (int(self.width / 4), int(self.height / 6)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), thickness=2)
        elif lenght<-400326265:
            left_right_velocity = -d_speed
            if debug:
                cv2.putText(self.image, "left", (int(self.width / 4), int(self.height / 6)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0),thickness=2)
        else:
            left_right_velocity = 0


    def frame_check(self):
        global d_speed, yaw_velocity, up_down_velocity
        if self.myHands[0][9][0] > self.width - int(self.width / 4):
            if debug:
                cv2.putText(self.image, "right", (int(self.width / 4 - 30), int(self.height / 2 - 110)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), thickness=2)
            yaw_velocity = d_speed
        elif self.myHands[0][9][0] < int(self.width / 4):
            if debug:
                cv2.putText(self.image, "left", (int(self.width / 4 - 30), int(self.height / 2 - 110)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), thickness=2)
            yaw_velocity = -d_speed
        elif self.myHands[0][9][1] > self.height - int(self.height / 3):
            if debug:
                cv2.putText(self.image, "down", (int(self.width / 4 - 30), int(self.height / 2 - 110)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), thickness=2)
            up_down_velocity = -d_speed
        elif self.myHands[0][9][1] < int(self.height / 3):
            if debug:
                cv2.putText(self.image, "up", (int(self.width / 4 - 30), int(self.height / 2 - 110)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), thickness=2)
            up_down_velocity = d_speed
        else:
            up_down_velocity = 0
            yaw_velocity = 0


class TelloDrone(Hand, Tello):
    def __init__(self):
        Tello.__init__(self)
        self.control_speed = [0, 0, 0, 0]

        if drone:
            self.keyboard_thread = Thread(target=self.getKeyboardInput).start()

            self.send_rc_thread = Thread(target=self.send_rc).start()


    def getKeyboardInput(self):
        global d_speed
        while True:
            self.control_speed = [left_right_velocity, for_back_velocity, up_down_velocity, yaw_velocity]
            # left/right
            if keyboard.is_pressed("LEFT"):
                self.control_speed[0] = -d_speed
            elif keyboard.is_pressed("RIGHT"):
                self.control_speed[0] = d_speed
            # forward/backward
            if keyboard.is_pressed("UP"):
                self.control_speed[1] = d_speed
            elif keyboard.is_pressed("DOWN"):
                self.control_speed[1] = -d_speed
            # uo/down
            if keyboard.is_pressed("w"):
                self.control_speed[2] = d_speed
            elif keyboard.is_pressed("s"):
                self.control_speed[2] = -d_speed
            # rotate
            if keyboard.is_pressed("a"):
                self.control_speed[3] = -d_speed
            elif keyboard.is_pressed("d"):
                self.control_speed[3] = d_speed
            # land
            if keyboard.is_pressed("q"): self.land(); time.sleep(3)
            # takeoff
            if keyboard.is_pressed("e"): self.takeoff()
            # flips
            if keyboard.is_pressed("j"):
                self.flip_left(); time.sleep(1)
            elif keyboard.is_pressed("l"):
                self.flip_right(); time.sleep(1)
            elif keyboard.is_pressed("i"):
                self.flip_forward(); time.sleep(1)
            elif keyboard.is_pressed("k"):
                self.flip_back(); time.sleep(1)
            # Stop
            if keyboard.is_pressed("ESC"): self.land(); time.sleep(3); self.end()
            time.sleep(0.05)


    def send_rc(self):
        while True:
            self.send_rc_control(self.control_speed[0], self.control_speed[1], self.control_speed[2], self.control_speed[3])





if __name__ == '__main__':
    Hand()
    TelloDrone()