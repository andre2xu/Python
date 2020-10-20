#My Quiz
import sys,time,os,threading

#Intro
intro1 = "Welcome to my quiz.\n\n> It consists of 10 questions that will test your knowledge.\n> You only have 2 minutes to complete it.\n> Each correct answer will give you 2 points.\n> Your final score will be displayed when you are finished or when the timer runs out.\n> Type 'Y' and hit enter when you are ready.\n\nGood luck!"
for letter in intro1:
    sys.stdout.write(letter)
    sys.stdout.flush()
    time.sleep(0.02)

intro2 = "\n\nDo you want to play?"
for letter in intro2:
    sys.stdout.write(letter)
    sys.stdout.flush()
    time.sleep(0.02)

#Yes/No
def yesorno(response):
    while True:
        if response == "Y":
            intro3 = "\nGood. Let us begin.\n\n"
            for letter in intro3:
                sys.stdout.write(letter)
                sys.stdout.flush()
                time.sleep(0.05)
            break
        if response == "N":
            print("Are you afraid?")
            return yesorno(input("Y or N: ").upper())
        else:
            print("Try again.")
            return yesorno(input("Y or N: ").upper())
    return "Y"

resp = yesorno(input("\nY or N: ").upper()) #stores 'Y'

#Quiz Timer
def countd(seconds):
    mins = seconds
    while True:
        mins -= 1
        time.sleep(1)

        if mins == -1:
            print("\n\nTime's up! You were too slow.")
            print ("\nYou scored {} points.\n".format(pts))
            break

if resp == "Y": #if user inputs 'Y' timer will start
    countdown_thread = threading.Thread(target=countd, args=(120,), daemon=True) #stops timer
    countdown_thread.start()

global pts
pts = 0

#Questions/Answers/Points system
if countdown_thread.is_alive() is True:
    q1 = input("How many colours are there in a rainbow?\n").lower()
    if q1 == str(7) or q1 == "seven":
        pts += 2
if countdown_thread.is_alive() is True:
    q2 = input("\nWhich of the following four is Obama's first name?\na) Barrack\nb) Barack\nc) Borrack\nd) Barock\n\nAnswer: ").lower()
    if q2 == "b" or q2 == "barack":
        pts += 2
if countdown_thread.is_alive() is True:
    q3 = input("\nChoose the country that is not in the EU.\n1. UK\n2. Ukraine\n3. Estonia\n4. Malta\n5. Cyprus\n\nAnswer: ").lower()
    if q3 == str(1) or q3 == "uk":
        pts += 2
if countdown_thread.is_alive() is True:
    q4 = input("\nIn what country did Halloween originate?\n").lower()
    if q4 == "ireland":
        pts += 2
if countdown_thread.is_alive() is True:
    q5 = input("\nSolve 8/2(2+2)\n").lower()
    if q5 == str(16) or q5 == str(1):
        pts += 2
if countdown_thread.is_alive() is True:
    q6 = input("\nIn American currency, ten cents make what?\n").lower()
    if q6 == "dime":
        pts += 2
if countdown_thread.is_alive() is True:
    q7 = input("\nWhich zodiac sign resembles the number 69?\n").lower()
    if q7 == "cancer":
        pts += 2
if countdown_thread.is_alive() is True:
    q8 = input("\nWhat number contains the same amount in its spelling?\n").lower()
    if q8 == str(4) or q8 == "four":
        pts += 2
if countdown_thread.is_alive() is True:
    q9 = input("\nHow many sides does a pentagon have?\n").lower()
    if q9 == str(5) or q9 == "five":
        pts += 2
if countdown_thread.is_alive() is True:
    q10 = input("\nWhat word is spelled incorrectly in every dictionary?\n").lower()
    if q10 == "incorrectly":
        pts += 2
    
    countdown_thread = threading.Thread(target=countd, daemon=True) #stops timer
    print ("\nYou scored {} points.\n".format(pts))