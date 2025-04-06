import random
guessesTaken = 0

print ('Привет, как тебя зовут?')

myName = input()
number = random.randint(1,20)

print ('Я рад тебя видеть, ' + myName + ' , я загадал число от 1 до 20 попробуй угадать число')
for guessesTaken in range(6):
    guess = int(input())
    
    if guess < number:
        print("Твое число слишком маленькое.")
    elif guess > number:
        print("Твое число слишком большое.")
    else:
        print(f"Отлично, {myName}! Ты справился за {guessesTaken + 1} попыток!")
        break
else:
    print(f"Увы. Я загадал число {number}.")