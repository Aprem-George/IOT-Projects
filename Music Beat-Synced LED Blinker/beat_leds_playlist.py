#!/usr/bin/env python3
import sys
import time
from pathlib import Path
from gpiozero import LED
import pygame
import aubio

LED_PINS = [17, 27, 22]  # BCM pins

def detect_beats(wav_path: str):
    win_s = 1024
    hop_s = 512
    src = aubio.source(wav_path, 0, hop_s)
    sr = src.samplerate
    tempo = aubio.tempo("default", win_s, hop_s, sr)

    beats = []
    total = 0
    while True:
        samples, read = src()
        if tempo(samples):
            beats.append(total / float(sr))
        total += read
        if read < hop_s:
            break
    return beats

def play_and_blink(wav_path: str, leds):
    print(f"\nNow playing: {wav_path}")
    beat_times = detect_beats(wav_path)
    print(f"Beats detected: {len(beat_times)}")

    pygame.mixer.music.load(wav_path)
    start = time.monotonic()
    pygame.mixer.music.play()

    idx = 0
    for bt in beat_times:
        while True:
            now = time.monotonic() - start
            dt = bt - now
            if dt <= 0:
                break
            time.sleep(min(0.005, dt))

        main = idx % 3
        for i, led in enumerate(leds):
            led.on() if i == main else led.off()

        time.sleep(0.08)
        for led in leds:
            led.off()

        idx += 1

    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 beat_leds_playlist.py *.wav")
        sys.exit(1)

    files = []
    for arg in sys.argv[1:]:
        p = Path(arg)
        if p.is_file() and p.suffix.lower() == ".wav":
            files.append(str(p))

    if not files:
        print("No .wav files found.")
        sys.exit(1)

    leds = [LED(p) for p in LED_PINS]
    for led in leds:
        led.off()

    pygame.mixer.init()

    try:
        for f in files:
            play_and_blink(f, leds)
    finally:
        for led in leds:
            led.off()

if __name__ == "__main__":
    main()