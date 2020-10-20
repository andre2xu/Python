#First Input
def first(firstnum):
    while True:
        try:
            inp1 = float(firstnum)
            return inp1
        except:
            print("Invalid number. Please retry.")
            return first(input("Enter a number: "))
num1 = first(input("Enter a number: "))

#Operation
def operat(oper):
    while True:
        if oper == "+":
            res1 = "+"
            return res1
        if oper == "-":
            res2 = "-"
            return res2
        if oper == "*":
            res3 = "*"
            return res3
        if oper == "/":
            res4 = "/"
            return res4
        else:
            print("Invalid operator. Please retry.")
            return operat(input("Enter an operator: "))
op = operat(input("Enter an operator: "))

#Second Input
def second(secondnum):
    while True:
        try:
            inp2 = float(secondnum)
            return inp2
        except:
            print("Invalid number. Please retry.")
            return second(input("Enter a number: "))
num2 = second(input("Enter a number: "))

#Checker & Result
if op == "+":
    print("Answer = ", num1 + num2)
if op == "-":
    print("Answer = ", num1 - num2)
if op == "*":
    print("Answer = ", num1 * num2)
if op == "/":
    print("Answer = ", num1 / num2)