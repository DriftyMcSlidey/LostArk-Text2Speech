# LostArk-Text2Speech
Script um die Dialoge in LostArk vorzulesen, welche nicht vertont wurden.

Video: https://youtu.be/E3Yn_T0XA1I

Benötigte pythonModule:

pip3.9 install opencv-python opencv-contrib-python numpy gtts playsound pytesseract mss pygame

tesseract-ocr install, bei der installatiion deutsch als sprachpaket installieren!:
für windows 64bit: https://github.com/UB-Mannheim/tesseract/wiki -> tesseract-ocr-w64-setup-v5.0.1.20220118.exe

Todo:
Erkennung der Maus -> Ton nur ausgeben wenn Maus im unteren Bereich des Textfeldes ist. 
Texterkennung verbessern -> falschen Erkennung von Wörtern, wenn der Text (3-4 Wörter) sehr kurz ist.

bekannte Bugs:
Wenn mann im Lager oder beim Shop ist liest er den Text vor. Schaut man Items an, überlagert das Beschreibungspopup des Items den Text und das Script erkennt Müll
