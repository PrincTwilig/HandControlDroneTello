from djitellopy.tello import Tello
from threading import Thread
import cv2
import keyboard
import time


class TelloDrone(Tello):

    def __init__(self):
        Tello.__init__(self)
        self.connect()
        print("battery: ", self.get_battery())

        # keyboard control
        self.control_speed = [0, 0, 0, 0]
        self.keyboard_thread = Thread(target=self.getKeyboardInput).start()

        # drone video
        self.streamon()
        self.cap = self.get_frame_read()
        self.drone_frame()

    def getKeyboardInput(self):

        while True:
            self.control_speed = [0, 0, 0, 0]
            speed = 50
            # 左右
            if keyboard.is_pressed("LEFT"):
                self.control_speed[0] = -speed
            elif keyboard.is_pressed("RIGHT"):
                self.control_speed[0] = speed

            # 前後
            if keyboard.is_pressed("UP"):
                self.control_speed[1] = speed
            elif keyboard.is_pressed("DOWN"):
                self.control_speed[1] = -speed

            # 上下
            if keyboard.is_pressed("w"):
                self.control_speed[2] = speed
            elif keyboard.is_pressed("s"):
                self.control_speed[2] = -speed

            # 旋轉
            if keyboard.is_pressed("a"):
                self.control_speed[3] = -speed
            elif keyboard.is_pressed("d"):
                self.control_speed[3] = speed

            # 降落
            if keyboard.is_pressed("q"): self.land(); time.sleep(3)

            # 起飛
            if keyboard.is_pressed("e"): self.takeoff()

            # flip
            if keyboard.is_pressed("j"):
                self.flip_left(); time.sleep(1)
            elif keyboard.is_pressed("l"):
                self.flip_right(); time.sleep(1)
            elif keyboard.is_pressed("i"):
                self.flip_forward(); time.sleep(1)
            elif keyboard.is_pressed("k"):
                self.flip_back(); time.sleep(1)

            # 退出
            if keyboard.is_pressed("ESC"): self.land(); time.sleep(3); self.end()

            time.sleep(0.05)

    def drone_frame(self):
        pTime = 0
        while True:
            img = self.cap.frame

            # fly keyboard control
            self.send_rc_control(self.control_speed[0], self.control_speed[1], self.control_speed[2],
                                 self.control_speed[3])

            # fps
            cTime = time.time()
            fps = 1 / (cTime - pTime)
            pTime = cTime
            cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

            cv2.imshow('frame', img)
            if cv2.waitKey(1) & 0xFF == 27:
                break

        self.streamoff()
        cv2.destroyAllWindows()
        self.land()
        self.end()


if __name__ == '__main__':
    TelloDrone()