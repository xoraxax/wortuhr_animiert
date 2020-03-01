# Wortuhr mit Matrix-Fading

Ich hatte mir eine Wortuhr von Build-yours.de als Bausatz gekauft. Leider gab der Flashspeicher den Geist auf, so dass ich einen neuen
Controller brauchte. Um nicht von der Originalfirmware mit Update-Funktionalität via HTTP abhängig zu sein, habe ich mir ein eigenes
Programm geschrieben, das auch Fading wie im Film Matrix unterstützt.

Um mein Programm nutzen zu können, braucht ihr einen ESP8266-Controller, auf dem Micropython installiert ist. Dann könnt ihr mit `update.sh`
die Wortuhr auf den Controller aufspielen. Hierzu wird mpfshell benötigt (`pip install mpfshell`). Vorher solltet ihr die wordclock_config.py.sample
in wordclock_config.py umbenennen und dort die WLAN-Zugangsdaten eintragen.

Lizenz: AGPL v3
