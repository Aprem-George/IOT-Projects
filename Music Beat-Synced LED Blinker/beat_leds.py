#!/usr/bin/env python3
import sys
import time
from gpiozero import LED
import pygame
import aubio

LED_PINS = [17, 27, 22]  # BCM

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

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 beat_leds.py song.wav")
        sys.exit(1)

    wav_path = sys.argv[1]
    leds = [LED(p) for p in LED_PINS]
    for led in leds:
        led.off()

    print("Detecting beats...")
    beat_times = detect_beats(wav_path)
    print(f"Beats detected: {len(beat_times)}")

    pygame.mixer.init()
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

        main_led = idx % 3
        for i, led in enumerate(leds):
            led.on() if i == main_led else led.off()

        time.sleep(0.08)
        for led in leds:
            led.off()
        idx += 1

    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

    for led in leds:
        led.off()

if __name__ == "__main__":
    main()