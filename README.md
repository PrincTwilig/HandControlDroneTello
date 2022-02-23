# Що це?<a name="what"></a>

Це проект для контролю дрона Tello за допомогою руки.

# Як це працює?<a name="how"></a>

Дрон Tello передає зображення, через OpenCV обробляємо картинку в сірий колір та передаємо зображення mediapipe. Mediapipe повертає масив данних з усіма точками на руці, і далі по цим точкам визначаємо наклон руки, зжаті пальці, та записані жести.

![](https://i.imgur.com/vXQ3nLY.png)

Наклон руки вліво і вправо відповідає за політ вліво чи вправо.
Також, якщо центр руки перемістився за сітку, дрон повертається щоб тримати руку в центрі.


# Навігація<a name="navigation"></a>

 + [Що це?](#what)
 + [Як це працює?](#how)
 + [Навігація](#navigation)
 + [Настройка](#settings)
 + [Потрібні бібліотеки](#libs)
 + [MediaPipe](#mediapipe)
 + [Компютерне бачення, та визначення жесів руки](#opencv)
   + [Як шукати точки?](#dots)
   + [Як визначати жести?](#gests)
     + [Визначення чи загнуті пальці руки](#hadifingers)
     + [Визначення нахилу руки](#handyaw)
     + [Визначення руки в рамках](#frame)
 + [Керування дроном Tello](#tello)
   + [Підключення до Tello та отримання зображення](#telloconnect)
   + [Відправка пакетів](#sendpackets)

# Настройка<a name="settings"></a>

> Python

``` Python
debug = True # Shows camera indicators
drone = False # Switch notebook cam and drone
control = True # Control drone with keypad

d_speed = 50
```
+ debug - Показує сітку та індикатори зжатих пальців
+ drone - якщо True то пробує підключитись до дрона в локальній мережі, якщо False запускає камеру з пристрою на якому запущено
+ control - дає можливість керуванню з клавіатури
+ d_speed - відповідає за швидкість маневрів дрона від 0 до 100


# Потрібні бібліотеки<a name="libs"></a>

> pip install djitellopy
> 
> pip install mediapipe
> 
> pip install keyboard
> 
> pip install opencv-python

+ djitellopy  - бібліотека для підключення до дрона, отримання данних з нього та управління.
+ threading  - бібліотека потоків, для створення віддільних потоків виконання програми.
+ mediapipe  - бібліотека від гугл, яка вертає точки руки на зображенні.
+ keyboard  - бібліотека для зчитування нажать клавіш.
+ opencv-python  - бібліотека компютерного бачення OpenCV, допомагає обробляти зображення, а також виводить зображення і всі індикатори на екран.
+  time  - бібліотека для визначення часу.

# MediaPipe<a name="mediapipe"></a>

Ця бібліотека має багато можливостей, зчитування поз, форми лиця і т.д. в проекті буде використано тільки руки.

![](https://google.github.io/mediapipe/images/mobile/hand_landmarks.png)
> Точки на руках

![](https://google.github.io/mediapipe/images/mobile/hand_crops.png)
> Угорі: вирівняні ручні посіви передані в мережу відстеження з анотацією правди землі. Унизу: відтворені синтетичні зображення рук з анотацією правди.

# Компютерне бачення, та визначення жесів руки<a name="opencv"></a>

![image](https://user-images.githubusercontent.com/93429979/155216314-18e82abe-7a48-47a2-99a9-bfbd74c6fada.png)

> Невелика блок схема роботи програми

## Як шукати точки?<a name="dots"></a>

Отримане зображення в OpenCV зберігається в форматі BGR(Blue Green Red) для вірної обробки переводимо його в RGB, далі відправляємо його на обробку mediapipe і отримуємо масив точок, та їх координат XYZ де X від 0(ліва частина екрану) до 1(права частина екрану) Y від 0(ліва частина екрану) до 1(права частина екрану) Z глибина точок відносно камери. За такими координатами трішки важко визначати положення точок, тому переводимо їх в координати по пікселям на зображені, потрібно X помножити на ширину екрану та Y на його висоту.

```Python
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
```

+ myHands - піксельні координати точки XYZ
+ handsType - визначає ліва рука чи права

## Як визначати жести?<a name="gests"></a>

### Визначення чи загнуті пальці руки<a name="hadifingers"></a>

Щоб визначити чи загнутий палець, ми можемо порівняти найвищу та найнищу точку пальці, якщо верхня точка на зображенні опинеться нижчи найнищої точки, значіть палець загнутий. Тому порівнюємо координату Y обох точок.

```Python
self.myHands[han][8][1] > self.myHands[han][6][1]
```

![](https://i.imgur.com/J6J1pV5.jpg)

> Зелений - верхня точка; Червоний - нижня точка.

> Назви точки та їх номер в масиві можна знайти на картинці вище в розділі mediapipe

Але таким способом ми не можемо визначити великий палець руки, оскільки він загинається не вниз а всередину руки, тому будемо порівнювати координату X.

```Python
self.myHands[han][4][0] > self.myHands[han][1][0]
```

![](https://i.imgur.com/ExOsMhi.jpg)

> Зелений - верхня точка; Червоний - нижня точка.

Ще нам потрібно визначати яка це рука, оскільки ліва рука на зображенні буде мати великий палець лівіше від найнижчої точка, а права правіше, тому робимо перевірку і міняємо знак.

```Python
if self.handsType[han] == 'Right':
	if self.myHands[han][4][0] > self.myHands[han][1][0]:
		###
elif self.handsType[han] == 'Left':
	if self.myHands[han][4][0] < self.myHands[han][1][0]:
		###
```

### Визначення нахилу руки<a name="handyaw"></a>

Нахил руки можна визначити різницею координати X між найвищою та найнижчою точками руки. Якщо верхня точка лівіше від нижньої то різниця буде додатня, якщо правіше то відємна.

![](https://i.imgur.com/BrgIM8N.jpg)

> Різниця між точками близька до 0, рука стоїть рівно

![](https://i.imgur.com/DF1TNQm.jpg)

> Різниця між точками додатня, рука нахилена вліво

### Визначення руки в рамках<a name="frame"></a>

Щоб завжди тримати руку в центрі зображення, потрібно визначити в якій частині екрану вона знаходиться, для цього порівнюємо координати X та Y з усіма сторонами екрану.

```Python
def frame_check(self):
	if self.myHands[0][9][0] > self.width - int(self.width / 4):
		#Рука в правій частині екрану
	elif self.myHands[0][9][0] < int(self.width / 4):
		#Рука в лівій частині екрану
	elif self.myHands[0][9][1] > self.height - int(self.height / 3):
		#Рука в нижній частині екрану
	elif self.myHands[0][9][1] < int(self.height / 3):
		#Рука в верхній частині екрану
```

# Керування дроном Tello<a name="tello"></a>

## Підключення до Tello та отримання зображення<a name="telloconnect"></a>

Перш за все, потрібно підключитись до вайфай мережі яку роздає Tello, та за допомогою djitellopy підключаємось до дрона, включаємо запис камери та отримуємо зображення.

```Python
self.connect() #Підключаємось до Tello
self.streamon() #Запускаємо камеру
self.image = self.get_frame_read().frame #Отримуємо та зберігаємо зображення в змінній
```

Ще нам можуть знадобитись деякі данні з дрона, такі як заряд батареї, висота польоту, швидкість. Тому ми їх також отримуємо та зберігаємо.

```Python
def get_drone_info(self):
	battery = self.get_battery()
	height = self.get_height()
	speed_x = self.get_speed_x()
	speed_y = self.get_speed_y()
	speed_z = self.get_speed_z()
	speed = (speed_x + speed_y + speed_z) / 1.5
```
> Середню швидкість обраховуємо за формулою

## Відправка пакетів<a name="sendpackets"></a>

У бібліотеці djitellopy вже є встроєний модуль для відправки UDP пакетів на дрон, тому нам потрібно просто відправити данні про рух вперед чи назад, вліво чи вправо, вверх чи вниз та поворот. Також щоб не було затримки між відправкою пакетів через виконання програми, відправку пакетів ми організуєм в окремому потоці. (Швидкість має бути від -100 до 100)

```Python
self.send_rc_thread = Thread(target=self.send_rc).start()

def send_rc(self):
	while True:
		self.send_rc_control(self.control_speed[0], self.control_speed[1], self.control_speed[2], self.control_speed[3])
```
> send_rc_control(-ліво/+право, -назад/+вперед, -вниз/+вверх, -оборот проти часової/+оборот за часовою)

Деякі команди мають виконуватись за допомогою TCP запросів, такі як посадка, взліт чи сальто. Відправляємо їх з самого коду.

```Python
self.land() #Посадка
self.flip_forward() #Сальто вперед
```
