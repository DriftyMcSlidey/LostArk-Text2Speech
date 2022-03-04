# folgende pakete brauchen wir
# pip3.9 install opencv-python numpy gtts playsound pytesseract mss pygame
from gtts import gTTS
import pytesseract
import cv2
import numpy as np
from mss import mss
import os
import time
from pygame import mixer

# default install pfad, bei der installatiion deutsch als sprachpaket installieren!
# für windows: https://github.com/UB-Mannheim/tesseract/wiki -> tesseract-ocr-w64-setup-v5.0.1.20220118.exe
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

sprache_ausgabe = 'de'
nickname = "Driftymcslidey"
mp3_1 = "audio/1.mp3"
mp3_2 = "audio/2.mp3"
dialog_detect_false = False
string_old = ""
string = "Willkommen zu LostArk Voice"

sct = mss()
# multi monitor setups zu capturen des richtigen bild ausschnittes,
# single monitor 1920x1080 primär monitor
monitor_x_start = 0
monitor_y_start = 0
spiel_gesamt = {'top': 0, 'left': monitor_x_start - 1920, 'width': 1920, 'height': 1080}

#wir löschen mal alte mp3s
if os.path.isfile(mp3_1):
    os.remove(mp3_1)
if os.path.isfile(mp3_2):
    os.remove(mp3_2)

#endlos schleife beginnt
while 1:
    #wir nehmen mal die zeit um die fps zu berechnen
    last_time = time.time()
    #wir lesen das bild ein zum debuggen
    #image_full = cv2.imread("screenshots/screenshot_20.png")
    #wir lesen das livebild des bildschirms ein
    image_full = sct.grab(spiel_gesamt)
    image = np.array(image_full)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if dialog_detect_false:
        continue
    else:
        # bildauschnitt zum erkennen, ob das spiel sich in einem dialog befindet 1920x1080
        y = 990; #start punkt senkrecht 990
        x = 1550; #start punkt wagerecht 1550
        h = 200; #höhe senkrecht 200
        w = 400 #breite wagerecht 400
        dialog_detect = image[y:y + h, x:x + w]
        kernel = np.ones((1, 1), np.uint8)
        dialog_detect = cv2.morphologyEx(dialog_detect, cv2.MORPH_OPEN, kernel)

        # bildauschnitt des textes welcher vorgelesen wird wenn wir einen dialog detecten 1920x1080
        y = 990; #start punkt senkrecht 990
        x = 450; #start punkt wagerecht 450
        h = 200; #höhe senkrecht 200
        w = 1145 #breite wagerecht 1145
        bildausschnitt_text = image[y:y + h, x:x + w]
        kernel = np.ones((1, 1), np.uint8)
        bildausschnitt_text = cv2.morphologyEx(bildausschnitt_text, cv2.MORPH_OPEN, kernel)
        print("time: {}".format((time.time() - last_time)))
        # wir verbessern mal die texterkennung, um fehlauzswertungen druch die transperanz zu verhindern
        custom_config = r'--oem 3 --psm 6'
        string = pytesseract.image_to_string(bildausschnitt_text, config=custom_config)
        # wir löschen mal unseren nickname aus den texten, das braucht keiner
        string = string.replace(nickname, "")
        # wir zählen mal die worte, damit wie wissen wie lang die pause bei der ausgabe sein muss
        wort_anzahl = len(string.split())
        laenge = len(string.split()) * 0.7

        # bildausgabe zum debugen
        #cv2.imshow("erkennung ob ein dialog offen ist", dialog_detect)
        #cv2.imshow("text der umgewandelt wird", bildausschnitt_text)

        #if cv2.waitKey(25) & 0xFF == ord("q"):
        #    cv2.destroyAllWindows()
        #    break

        # wir verlgeichen den alten text mit dem neu erkannten. sind diese gleich spielen wir diese nicht nochmal ab
        set1 = set(string.split(' '))
        set2 = set(string_old.split(' '))
        if not string:
            print("kein text erkannt")
            continue
        if set1 == set2:
            print("keine Textänderung")
            continue
        else:
            print(laenge,"Sekunden ",wort_anzahl," Wörter vorlesen")
            # wir geben den Text einmal zum test aus
            print(string)
            mp3 = mp3_1
            try:
                if os.path.isfile(mp3_1):
                    print("lösche ", mp3_2)
                    if os.path.isfile(mp3_2):
                        os.remove(mp3_2)
                    mp3 = mp3_2
            except PermissionError:
                print("kann nicht löschen", mp3_2)
            try:
                if os.path.isfile(mp3_2):
                    print("lösche ", mp3_1)
                    if os.path.isfile(mp3_1):
                        os.remove(mp3_1)
                    mp3 = mp3_1
            except PermissionError:
                print("kann nicht löschen",mp3_1)
            tts = gTTS(text=string, lang=sprache_ausgabe)
            print("erstelle",mp3)
            tts.save(mp3)

            print("time: {}".format((time.time() - last_time)))
            string_old = string

            # mp3 abspielen
            #lostark.stimme(wort_anzahl * 0.5)
            # wir geben die mp3 aus
            mixer.init()
            if os.path.isfile(mp3):
                print("lade ", mp3)
                mixer.music.load(mp3)
                mixer.music.play()
                time.sleep(laenge)
                mixer.music.stop()
