#Password Generator
import secrets,sys

global lowercases
global uppercases
global numbers
global specialchars

lowercases = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]

uppercases = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]

numbers = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]

specialchars = ["!", "£", "$", "%", "&", "#", "@", "?"]

#Password length
def passlength(inp):
    while True:
        try:
            x = int(inp)
            return x
        except:
            print("Invalid value, try again.")
            return passlength(input("How long do you want the password to be?\nEnter: "))

length = passlength(input("How long do you want the password to be?\nEnter: "))

#Lowercase characters
def passlower(yeslower):
    while True:
        if yeslower == "Y":
            return True
        if yeslower == "N":
            return False
        else:
            print("Invalid answer, try again.")
            return passlower(input("Do you want lowercase characters? Y/N: ").upper())

lcase = passlower(input("Do you want lowercase characters? Y/N: ").upper())

#Uppercase characters
def passupper(yesupper):
    while True:
        if yesupper == "Y":
            return True
        if yesupper == "N":
            return False
        else:
            print("Invalid answer, try again.")
            return passupper(input("Do you want uppercase characters? Y/N: ").upper())

ucase = passupper(input("Do you want uppercase characters? Y/N: ").upper())

#Numbers
def passnum(yesnum):
    while True:
        if yesnum == "Y":
            return True
        if yesnum == "N":
            return False
        else:
            print("Invalid answer, try again.")
            return passupper(input("Do you want numbers? Y/N: ").upper())

numb = passnum(input("Do you want numbers? Y/N: ").upper())

#Special characters
def passSpec(yesSpec):
    while True:
        if yesSpec == "Y":
            return True
        if yesSpec == "N":
            return False
        else:
            print("Invalid answer, try again.")
            return passSpec(input("Do you want special characters? Y/N: ").upper())

specialSymbols = passSpec(input("Do you want special characters? Y/N: ").upper())

#template
if lcase == True and ucase == True and numb == True and specialSymbols == True:
    list1 = lowercases + uppercases + numbers + specialchars
    for _ in range(length):
        gen = secrets.choice(list1)
        sys.stdout.write(gen)
        sys.stdout.flush()

if lcase == True and ucase == False and numb == False and specialSymbols == False:
    list2 = lowercases
    for _ in range(length):
        gen = secrets.choice(list2)
        sys.stdout.write(gen)
        sys.stdout.flush()

if lcase == False and ucase == True and numb == False and specialSymbols == False:
    list3 = uppercases
    for _ in range(length):
        gen = secrets.choice(list3)
        sys.stdout.write(gen)
        sys.stdout.flush()

if lcase == False and ucase == False and numb == True and specialSymbols == False:
    list4 = numbers
    for _ in range(length):
        gen = secrets.choice(list4)
        sys.stdout.write(gen)
        sys.stdout.flush()

if lcase == False and ucase == False and numb == False and specialSymbols == True:
    list5 = specialchars
    for _ in range(length):
        gen = secrets.choice(list5)
        sys.stdout.write(gen)
        sys.stdout.flush()

if lcase == True and ucase == False and numb == True and specialSymbols == True:
    list6 = lowercases + numbers + specialchars
    for _ in range(length):
        gen = secrets.choice(list6)
        sys.stdout.write(gen)
        sys.stdout.flush()

if lcase == True and ucase == True and numb == False and specialSymbols == True:
    list7 = lowercases + uppercases + specialchars
    for _ in range(length):
        gen = secrets.choice(list7)
        sys.stdout.write(gen)
        sys.stdout.flush()

if lcase == True and ucase == False and numb == False and specialSymbols == True:
    list8 = lowercases + specialchars
    for _ in range(length):
        gen = secrets.choice(list8)
        sys.stdout.write(gen)
        sys.stdout.flush()

if lcase == False and ucase == True and numb == False and specialSymbols == False:
    list9 = uppercases
    for _ in range(length):
        gen = secrets.choice(list9)
        sys.stdout.write(gen)
        sys.stdout.flush()

if lcase == True and ucase == False and numb == True and specialSymbols == False:
    list10 = lowercases + numbers
    for _ in range(length):
        gen = secrets.choice(list10)
        sys.stdout.write(gen)
        sys.stdout.flush()

if lcase == False and ucase == True and numb == False and specialSymbols == True:
    list11 = uppercases + specialchars
    for _ in range(length):
        gen = secrets.choice(list11)
        sys.stdout.write(gen)
        sys.stdout.flush()

if lcase == False and ucase == True and numb == True and specialSymbols == False:
    list12 = uppercases + numbers
    for _ in range(length):
        gen = secrets.choice(list12)
        sys.stdout.write(gen)
        sys.stdout.flush()

if lcase == True and ucase == True and numb == True and specialSymbols == False:
    list13 = lowercases + uppercases + numbers
    for _ in range(length):
        gen = secrets.choice(list13)
        sys.stdout.write(gen)
        sys.stdout.flush()

if lcase == True and ucase == False and numb == True and specialSymbols == True:
    list14 = lowercases + numbers + specialchars
    for _ in range(length):
        gen = secrets.choice(list14)
        sys.stdout.write(gen)
        sys.stdout.flush()

if lcase == True and ucase == True and numb == False and specialSymbols == False:
    list15 = lowercases + uppercases + specialchars
    for _ in range(length):
        gen = secrets.choice(list15)
        sys.stdout.write(gen)
        sys.stdout.flush()

if lcase == False and ucase == False and numb == True and specialSymbols == True:
    list16 = numbers + specialchars
    for _ in range(length):
        gen = secrets.choice(list16)
        sys.stdout.write(gen)
        sys.stdout.flush()

if lcase == False and ucase == True and numb == True and specialSymbols == True:
    list17 = uppercases + numbers + specialchars
    for _ in range(length):
        gen = secrets.choice(list17)
        sys.stdout.write(gen)
        sys.stdout.flush()

if lcase == False and ucase == False and numb == False and specialSymbols == False:
    print("\nIf you didn't want a password then why are you using this generator?\n")