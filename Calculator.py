num1 =input("Введи первое число: ")
num2 =input("Введи второе число: ")
operation = input ("Какое действие сделать? (+ или -, (* или/): ")

num1 = float(num1)
num2 = float(num2)

if operation == "+":
    result = num1 + num2
    print(f"{num1} + {num2} = {result}")
    
elif operation == "-":
    result = num1 + num2
    print(f"{num1} - {num2} = {result}")

elif operation == "*":
    result = num1 * num2
    print(f"{num1} * {num2} = {result}")
    
elif operation == "/":
    if num2 == 0:
        print("На ноль делить нельзя!")
    else:
        result = num1 / num2
        print(f"{num1} / {num2} = {result}")
    
else:
    print("Я пока умею только складывать, вычитать, умножать и делить!")