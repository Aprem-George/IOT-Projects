Music Beat-Synced LED Blinker (Raspberry Pi 3B)



This project makes 3 LEDs blink in sync with the beat of the music you provide.

It runs fully on a Raspberry Pi 3 Model B, using GPIO LEDs and beat detection on WAV audio.



✅ Features:



Upload MP3 from PC → Raspberry Pi

Convert MP3 → WAV on Pi

Detect beats from WAV using aubio

Play audio and blink 3 LEDs in time with detected beats

Play multiple WAV files back-to-back with beat-synced blinking



**Hardware Required**



Raspberry Pi 3 Model B

3 × LEDs

3 × resistors (220Ω–330Ω recommended)

Breadboard + jumper wires

Wiring (BCM GPIO)



**This project uses BCM pin numbering:**



LED	BCM GPIO	Physical Pin

LED 1	GPIO17	Pin 11

LED 2	GPIO27	Pin 13

LED 3	GPIO22	Pin 15

GND	GND	Pin 6 (or any GND)



**Correct LED wiring (for each LED)**



GPIO → resistor → LED anode (long leg)

LED cathode (short leg) → GND



If only one LED blinks, it’s usually due to:



wrong pin numbering (physical vs BCM)

LED reversed (legs swapped)

breadboard row/rail mistake

missing common ground



**Software Setup (Raspberry Pi)**



Update packages:



sudo apt update



Install dependencies:



sudo apt install -y python3-pip python3-gpiozero python3-pygame python3-aubio ffmpeg

Upload Music from PC to Raspberry Pi (SCP)



From Windows PowerShell:



scp "C:\\Users\\aprem\\Downloads\\your\_song.mp3" aprem@192.168.50.28:/home/aprem/

Common Error Fix



If you try uploading to /home/pi/ while logging in as aprem, you’ll get a permission error:



✅ Upload to your own home folder instead:



scp "C:\\path\\song.mp3" aprem@<PI\_IP>:/home/aprem/

Convert MP3 → WAV on the Pi



Go to the folder where your MP3 is:



cd /home/aprem



Convert:



ffmpeg -i "your\_song.mp3" -ac 2 -ar 44100 song.wav

Beat-Synced Single Track (Beat + Play + Blink)



Save this file as: beat\_leds.py



\#!/usr/bin/env python3

import sys

import time

from gpiozero import LED

import pygame

import aubio



LED\_PINS = \[17, 27, 22]  # BCM



def detect\_beats(wav\_path: str):

&#x20;   win\_s = 1024

&#x20;   hop\_s = 512

&#x20;   src = aubio.source(wav\_path, 0, hop\_s)

&#x20;   sr = src.samplerate

&#x20;   tempo = aubio.tempo("default", win\_s, hop\_s, sr)



&#x20;   beats = \[]

&#x20;   total = 0

&#x20;   while True:

&#x20;       samples, read = src()

&#x20;       if tempo(samples):

&#x20;           beats.append(total / float(sr))

&#x20;       total += read

&#x20;       if read < hop\_s:

&#x20;           break

&#x20;   return beats



def main():

&#x20;   if len(sys.argv) < 2:

&#x20;       print("Usage: python3 beat\_leds.py song.wav")

&#x20;       sys.exit(1)



&#x20;   wav\_path = sys.argv\[1]

&#x20;   leds = \[LED(p) for p in LED\_PINS]

&#x20;   for led in leds:

&#x20;       led.off()



&#x20;   print("Detecting beats...")

&#x20;   beat\_times = detect\_beats(wav\_path)

&#x20;   print(f"Beats detected: {len(beat\_times)}")



&#x20;   pygame.mixer.init()

&#x20;   pygame.mixer.music.load(wav\_path)



&#x20;   start = time.monotonic()

&#x20;   pygame.mixer.music.play()



&#x20;   idx = 0

&#x20;   for bt in beat\_times:

&#x20;       while True:

&#x20;           now = time.monotonic() - start

&#x20;           dt = bt - now

&#x20;           if dt <= 0:

&#x20;               break

&#x20;           time.sleep(min(0.005, dt))



&#x20;       main\_led = idx % 3

&#x20;       for i, led in enumerate(leds):

&#x20;           led.on() if i == main\_led else led.off()



&#x20;       time.sleep(0.08)

&#x20;       for led in leds:

&#x20;           led.off()

&#x20;       idx += 1



&#x20;   while pygame.mixer.music.get\_busy():

&#x20;       time.sleep(0.1)



&#x20;   for led in leds:

&#x20;       led.off()



if \_\_name\_\_ == "\_\_main\_\_":

&#x20;   main()



Run:



python3 beat\_leds.py song.wav

Back-to-Back Playback (Multiple WAV files + Beat-Synced LEDs)



Important: aplay \*.wav only plays audio and will NOT blink LEDs.

We need a script that plays audio and blinks LEDs.



Save this file as: beat\_leds\_playlist.py



\#!/usr/bin/env python3

import sys

import time

from pathlib import Path

from gpiozero import LED

import pygame

import aubio



LED\_PINS = \[17, 27, 22]  # BCM pins



def detect\_beats(wav\_path: str):

&#x20;   win\_s = 1024

&#x20;   hop\_s = 512

&#x20;   src = aubio.source(wav\_path, 0, hop\_s)

&#x20;   sr = src.samplerate

&#x20;   tempo = aubio.tempo("default", win\_s, hop\_s, sr)



&#x20;   beats = \[]

&#x20;   total = 0

&#x20;   while True:

&#x20;       samples, read = src()

&#x20;       if tempo(samples):

&#x20;           beats.append(total / float(sr))

&#x20;       total += read

&#x20;       if read < hop\_s:

&#x20;           break

&#x20;   return beats



def play\_and\_blink(wav\_path: str, leds):

&#x20;   print(f"\\nNow playing: {wav\_path}")

&#x20;   beat\_times = detect\_beats(wav\_path)

&#x20;   print(f"Beats detected: {len(beat\_times)}")



&#x20;   pygame.mixer.music.load(wav\_path)

&#x20;   start = time.monotonic()

&#x20;   pygame.mixer.music.play()



&#x20;   idx = 0

&#x20;   for bt in beat\_times:

&#x20;       while True:

&#x20;           now = time.monotonic() - start

&#x20;           dt = bt - now

&#x20;           if dt <= 0:

&#x20;               break

&#x20;           time.sleep(min(0.005, dt))



&#x20;       main = idx % 3

&#x20;       for i, led in enumerate(leds):

&#x20;           led.on() if i == main else led.off()



&#x20;       time.sleep(0.08)

&#x20;       for led in leds:

&#x20;           led.off()



&#x20;       idx += 1



&#x20;   while pygame.mixer.music.get\_busy():

&#x20;       time.sleep(0.1)



def main():

&#x20;   if len(sys.argv) < 2:

&#x20;       print("Usage: python3 beat\_leds\_playlist.py \*.wav")

&#x20;       sys.exit(1)



&#x20;   files = \[]

&#x20;   for arg in sys.argv\[1:]:

&#x20;       p = Path(arg)

&#x20;       if p.is\_file() and p.suffix.lower() == ".wav":

&#x20;           files.append(str(p))



&#x20;   if not files:

&#x20;       print("No .wav files found.")

&#x20;       sys.exit(1)



&#x20;   leds = \[LED(p) for p in LED\_PINS]

&#x20;   for led in leds:

&#x20;       led.off()



&#x20;   pygame.mixer.init()



&#x20;   try:

&#x20;       for f in files:

&#x20;           play\_and\_blink(f, leds)

&#x20;   finally:

&#x20;       for led in leds:

&#x20;           led.off()



if \_\_name\_\_ == "\_\_main\_\_":

&#x20;   main()





**Run (all WAVs in /home/aprem/):**



cd /home/aprem

python3 beat\_leds\_playlist.py \*.wav



Tracks play in filename order. For a clean order, rename as:



01\_song.wav

02\_song.wav

03\_song.wav



**Troubleshooting**



Only one LED blinks



Confirm you used BCM pin numbers (17/27/22) not physical pin numbers.

Confirm each LED is wired: GPIO → resistor → LED → GND

Ensure all LED cathodes connect to the same GND rail.



No sound output



If you can’t hear audio, set output to headphone/HDMI:



sudo raspi-config



Then:



System Options → Audio → select output



**Folder Structure (suggested)**



music-beat-leds/

├── beat\_leds.py

├── beat\_leds\_playlist.py

├── README.md

└── songs/

&#x20;   ├── 01\_song.wav

&#x20;   ├── 02\_song.wav

&#x20;   └── 03\_song.wav



**Credits / Libraries Used**



gpiozero for GPIO LED control

aubio for beat detection

pygame for audio playback

ffmpeg for MP3 → WAV conversion

