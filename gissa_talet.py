#!/usr/bin/env python3
"""Ett litet terminalspel: gissa talet!"""

import random


def spela():
    hemligt_tal = random.randint(1, 100)
    antal_gissningar = 0

    print("\n🎯 Välkommen till Gissa talet!")
    print("Jag tänker på ett tal mellan 1 och 100.")

    while True:
        svar = input("Din gissning (eller q för att avsluta): ").strip()

        if svar.lower() == "q":
            print(f"Spelet avslutas. Talet var {hemligt_tal}. Hej då!")
            return

        try:
            gissning = int(svar)
        except ValueError:
            print("Skriv ett heltal, eller q för att avsluta.")
            continue

        if not 1 <= gissning <= 100:
            print("Talet måste vara mellan 1 och 100.")
            continue

        antal_gissningar += 1

        if gissning < hemligt_tal:
            print("För lågt! Försök med ett högre tal. ⬆️")
        elif gissning > hemligt_tal:
            print("För högt! Försök med ett lägre tal. ⬇️")
        else:
            print(f"🎉 Rätt! Du klarade det på {antal_gissningar} gissningar!")
            break


if __name__ == "__main__":
    while True:
        spela()
        igen = input("\nVill du spela igen? (j/n): ").strip().lower()
        if igen != "j":
            print("Tack för att du spelade! 👋")
            break
