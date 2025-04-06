import random
guessesTaken = 0

print ('Привет, как тебя зовут?')

myName = input()
number = random.randint(1,20)

print ('Я рад тебя видеть, ' + myName + ' , я загадал число от 1 до 20 попробуй угадать число')
for guessesTaken in range (6):
   
    guess = input()
    guess = int(guess)
    
    if guess < number:
        print ("Твое число слишком маленькое.")
        
    if guess > number:
        print ("Твое число слишком большое")    
if guess == number:
    guessesTaken = str(guessesTaken + 1)
    print ('Отлично, ' + myName + '! Ты справился за ' + guessesTaken + ' попытки!')

    
if guess != number:
    number = str(number)
    print('Увы. Я загадал число ' + number +' .')