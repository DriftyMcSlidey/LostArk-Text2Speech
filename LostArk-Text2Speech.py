# folgende pakete brauchen wir
# pip3.9 install opencv-python opencv-contrib-python numpy gtts pytesseract mss pygame
from gtts import gTTS
import pytesseract
import cv2
import numpy as np
from mss import mss
import os
import time
from pygame import mixer

#default install pfad, bei der installatiion deutsch als sprachpaket installieren!
#für windows: https://github.com/UB-Mannheim/tesseract/wiki -> tesseract-ocr-w64-setup-v5.0.1.20220118.exe
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

#lautsträke der ausgabe 0 (0%) - 1 (100%)
lautstaerke = 0.7

#wenn due eine andere sprache eingestellt hast muss du das hier anpassen
sprache_ausgabe = 'de'
tesseract_ausgabe = "deu"
exit_dialog_text = "Verlassen"

#beispiel für englisch
sprache_ausgabe_eng = 'en'
tesseract_ausgabe_eng = "eng"
exit_dialog_text_eng = "Leave"

#multi monitor setups zu capturen des richtigen bild ausschnittes,
#single monitor 1920x1080 primär monitor
monitor_x_start = 0
monitor_y_start = 0
#bei dual monitor oder triple die ausrichtung zu primären bildschirm beachten linker monitor bei 1920x1080
#monitor_x_start = - 1920
#monitor_y_start = 0
#bei dual monitor oder triple die ausrichtung zu primären bildschirm beachten rechter monitor bei 1920x1080
#monitor_x_start = 1920
#monitor_y_start = 0

#wir capturen aus performance gründen nur den unter unteren teil des bildes mit einer höhe von 100 pixel
#spiel_gesamt = {'top': 0, 'left': monitor_x_start - 1920, 'width': 1920, 'height': 1080}
spiel_gesamt = {'top': 985, 'left': monitor_x_start + 440, 'width': 1920, 'height': 100}

#audio dateien und ordner
mp3_1 = "audio/1.mp3"
mp3_2 = "audio/2.mp3"
if not os.path.exists('audio'):
    os.makedirs('audio')
#wir löschen mal alte mp3s
if os.path.isfile(mp3_1):
    os.remove(mp3_1)
if os.path.isfile(mp3_2):
    os.remove(mp3_2)

#screencapture aktivieren
sct = mss()

#das hier nicht ändern
dialog_detect_false = False
string_old = ""
string = "Willkommen zu LostArk2Speech"
laenge_old = 0
debug = ""

print(string + " " + sprache_ausgabe + " " + tesseract_ausgabe)

#endlos schleife beginnt
while 1:
    #wir nehmen mal die zeit um die fps zu berechnen
    last_time = time.time()

    #wir lesen den test screenshot ein zum debuggen
    #image_full = cv2.imread("screenshots/screenshot_20.png")
    #y = 985 ; #x = 450 ; h = 150 ; w = 1550

    #wir lesen das livebild des bildschirms ein
    image_full = sct.grab(spiel_gesamt)

    #wir wandeln das bild in für dne pc verständlche daten um
    image_full = np.array(image_full)
    image = cv2.cvtColor(image_full, cv2.COLOR_BGR2GRAY)
    figure_size = 3
    image = cv2.GaussianBlur(image, (figure_size, figure_size), 0)
    image = cv2.bitwise_not(image)
    if dialog_detect_false:
        continue
    else:
        if not string_old:
            time.sleep(1)
        #bildauschnitt zum erkennen, ob das spiel sich in einem dialog befindet 1920x1080
        #hier schneiden wir uns das "Verlassen" nutton aus den diealogen aus
        y = 25; x = 1320; h = 40; w = 120
        dialog_detect = image[y:y + h, x:x + w]

        #wir wandeln das bild ,um einen guten kotrast für die spracherkennung zu bekommen
        kernel = np.ones((1, 1), np.uint8)
        dialog_detect = cv2.morphologyEx(dialog_detect, cv2.MORPH_OPEN, kernel)

        #wir lesen den text aus dem bild
        custom_config = r'--oem 3 --psm 6'
        dialog_detect_string = str(pytesseract.image_to_string(dialog_detect, config=custom_config, lang=tesseract_ausgabe)).replace("\n", "")
        dialog_detect_string_check = str(exit_dialog_text).replace("\n", "")
        #wenn der text unserer forgabe "Verlassen" übereinstimmt, generieren wir eine mp3
        #print("erkannt: \"" + dialog_detect_string + "\"")
        if not dialog_detect_string == dialog_detect_string_check and not dialog_detect_string == exit_dialog_text_eng:
            continue
        #wenn englisch erkannt wird switchen wir die text erkennung zu englisch
        if dialog_detect_string == exit_dialog_text_eng:
            sprache_ausgabe = 'en'
            tesseract_ausgabe = "eng"
            exit_dialog_text = "Leave"

        #nachdem wir erkannt haben das es ein dialog ist machen wir uns ran den dialogtext auszulesen
        #bildauschnitt des textes, welcher vorgelesen wird wenn wir einen dialog detecten 1920x1080
        y = 0; x = 0; h = 150; w = 1145
        bildausschnitt_text = image[y:y + h, x:x + w]

        #wir verbessern mal die texterkennung, um fehlauswertungen durch die leichte transperanz zu verhindern
        kernel = np.ones((1, 1), np.uint8)
        bildausschnitt_text = cv2.morphologyEx(bildausschnitt_text, cv2.MORPH_OPEN, kernel)

        #wir geben eine Zeit aus wie lang das dauert zum benchmarken und debuggen
        #print("time: {}".format((time.time() - last_time)))

        #wir verbessern mal die texterkennung, um fehlauswertungen durch die leichte transperanz zu verhindern
        custom_config = r'--oem 3 --psm 6'
        string = str(pytesseract.image_to_string(bildausschnitt_text, config=custom_config, lang=tesseract_ausgabe)).replace("\n", " ")
        string = string.replace("...", "")
        string = string.replace(".", ". ")
        # wir zählen mal die worte, damit wie wissen wie lang die pause bei der ausgabe sein muss
        wort_anzahl = len(string.split())
        laenge = len(string.split()) * 0.8

        #bildausgabe zum debuggen, damit erennt ihr wenn ihr beii der auflösung oben rumspielen müsst
        if debug:
            cv2.imshow("erkennung ob ein dialog offen ist", dialog_detect)
            cv2.imshow("text der umgewandelt wird", bildausschnitt_text)
            if cv2.waitKey(25) & 0xFF == ord("q"):
                cv2.destroyAllWindows()
                break

        # wir verlgeichen den alten text mit dem neu erkannten. sind diese gleich spielen wir diese nicht nochmal ab
        set1 = set(string.split(' '))
        set2 = set(string_old.split(' '))
        # wir speichern die alte ausgabe zum späteren vergleich
        string_old = string

        #wenn wir keinen Text auslsen konnten verwefen wir das ganze
        if not string:
            #print("kein text erkannt")
            continue

        # wenn sich der text zum vorhergehenden umlauf nicht geändert hat, verwerfen wir das ganze
        # dies sorgt dafür das der text nur 1 mal vorgelesen wird
        wort_temp_count = 0
        if laenge == laenge_old:
            for i in set1:
                for j in set2:
                    if i == j:
                        wort_temp_count = wort_temp_count + 1
                        if wort_temp_count > 2:
                            break
                break
            if wort_temp_count > 2:
                continue
        laenge_old = laenge

        #buchstaben im string um die ausgabe länge zu ermitteln
        buchstaben = len(list(c for c in string if c.isalpha()))
        ausgabe_zeit = buchstaben / 7.5
        if not set1 == set2:
            print(wort_anzahl,"x wörter in ",ausgabe_zeit,"sekunden ")

            #rechtschreibprüfung
            #for word in string.split(" "):
            #    print("original: " + word)
            #    spell.known(['google'])
            #    print("korrektur: " +spell.correction(word))

            # wir geben den Sprach-Text einmal aus
            print(string)

            ##wir schreiben den text in eine datei. diese önnen wir verwenden um tesseract zu traiinieren
            #datei = open('log.txt', 'a')
            #datei.write(string)

            #unser script sperrt bei der ausgabe die aktuelle mp3 datei und wir können diese nicht löschen
            # daher zwitschen wir zwischen 2 dateien und löschen immer die die wir können
            mp3 = mp3_1
            try:
                if os.path.isfile(mp3_1):
                    #print("lösche ", mp3_2)
                    if os.path.isfile(mp3_2):
                        os.remove(mp3_2)
                    mp3 = mp3_2
            except PermissionError:
                print("kann nicht löschen: ", mp3_2)
            try:
                if os.path.isfile(mp3_2):
                    #print("lösche :", mp3_1)
                    if os.path.isfile(mp3_1):
                        os.remove(mp3_1)
                    mp3 = mp3_1
            except PermissionError:
                print("kann nicht löschen :",mp3_1)

            #jetzt wandeln wir den erkannten text in mp3 um
            tts = gTTS(text=string, lang=sprache_ausgabe, slow=False, lang_check=True)
            #print("erstelle",mp3)
            tts.save(mp3)

            #nochmal eine klene zeit ausgabe zum debuggen
            #print("time: {}".format((time.time() - last_time)))

            #wir geben die erstellte mp3 aus
            mixer.init()
            if os.path.isfile(mp3):
                #print("lade ", mp3)
                mixer.music.load(mp3)
                mixer.music.set_volume(lautstaerke)
                mixer.music.play()
                time.sleep(ausgabe_zeit)
                mixer.music.stop()
                if debug:
                    print("ausgabe beendet")

#das wars mehr braucht man theoretisch nicht
#da einige sätze vertont sind, könnte man noch eine erkennung des mauszeigers einbauen
#zur sprachausgabe muss man dann über das "Verlassen", erst dann beginnt die sprachausgabe.
