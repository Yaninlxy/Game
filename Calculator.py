while True:
    print("\nКалькулятор (введи 'выход' чтобы завершить)")

    num1 = input("Введи первое число: ")
    if num1.lower() == "выход":
        break

    num2 = input("Введи второе число: ")
    if num2.lower() == "выход":
        break

    operation = input("Какое действие сделать? (+, -, *, /, **, %): ")
    if operation.lower() == "выход":
        break

    try:
        num1 = float(num1)
        num2 = float(num2)
    except ValueError:
        print("Ошибка: нужно вводить числа!")
        continue

    if operation == "+":
        result = num1 + num2
        print(f"{num1} + {num2} = {result}")

    elif operation == "-":
        result = num1 - num2
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

    elif operation == "**":
        result = num1 ** num2
        print(f"{num1} ** {num2} = {result}")

    elif operation == "%":
        if num2 == 0:
            print("На ноль делить нельзя!")
        else:
            result = num1 % num2
            print(f"{num1} % {num2} = {result}")

    else:
        print("Неизвестная операция. Доступны: +, -, *, /, **, %")
