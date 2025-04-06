import os

FILENAME = "todo.txt"

# Загружаем список из файла
def load_tasks():
    tasks = []
    if os.path.exists(FILENAME):
        with open(FILENAME, "r", encoding="utf-8") as f:
            for line in f:
                status, text = line.strip().split("|", 1)
                tasks.append({"done": status == "1", "text": text})
    return tasks

# Сохраняем список в файл
def save_tasks(tasks):
    with open(FILENAME, "w", encoding="utf-8") as f:
        for task in tasks:
            status = "1" if task["done"] else "0"
            f.write(f"{status}|{task['text']}\n")

# Показываем задачи
def show_tasks(tasks):
    if not tasks:
        print("Список пуст.")
    else:
        print("\nТекущие задачи:")
        for i, task in enumerate(tasks, 1):
            mark = "[x]" if task["done"] else "[ ]"
            print(f"{i}. {mark} {task['text']}")

# Программа
tasks = load_tasks()

while True:
    print("\n=== Список дел ===")
    print("1. Показать задачи")
    print("2. Добавить задачу")
    print("3. Отметить как выполненную")
    print("4. Удалить задачу")
    print("5. Выйти")

    choice = input("Твой выбор: ")

    if choice == "1":
        show_tasks(tasks)

    elif choice == "2":
        text = input("Введи задачу: ")
        tasks.append({"done": False, "text": text})
        save_tasks(tasks)
        print("Задача добавлена!")

    elif choice == "3":
        show_tasks(tasks)
        try:
            num = int(input("Номер выполненной задачи: "))
            if 1 <= num <= len(tasks):
                tasks[num - 1]["done"] = True
                save_tasks(tasks)
                print("Задача отмечена как выполненная!")
            else:
                print("Неверный номер.")
        except ValueError:
            print("Нужно ввести число.")

    elif choice == "4":
        show_tasks(tasks)
        try:
            num = int(input("Номер задачи для удаления: "))
            if 1 <= num <= len(tasks):
                removed = tasks.pop(num - 1)
                save_tasks(tasks)
                print(f"Удалено: {removed['text']}")
            else:
                print("Неверный номер.")
        except ValueError:
            print("Нужно ввести число.")

    elif choice == "5":
        print("Пока!")
        break

    else:
        print("Неверный выбор, попробуй снова.")
