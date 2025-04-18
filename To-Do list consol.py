import os

FILENAME = "todo.txt"

# Загружаем список из файла
def load_tasks():
    tasks = []
    if os.path.exists(FILENAME):
        with open(FILENAME, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    status, category, text = line.strip().split("|", 2)
                    tasks.append({"done": status == "1", "category": category, "text": text})
                except ValueError:
                    print(f"Пропущена строка: {line.strip()}")
    return tasks

# Сохраняем список в файл
def save_tasks(tasks):
    with open(FILENAME, "w", encoding="utf-8") as f:
        for task in tasks:
            status = "1" if task["done"] else "0"
            f.write(f"{status}|{task['category']}|{task['text']}\n")

# Показываем задачи
def show_tasks(tasks, category=None):
    filtered_tasks = [task for task in tasks if category is None or task["category"] == category]
    if not filtered_tasks:
        print("Список пуст или нет задач в этой категории.")
        return
    
    print(f"\nТекущие задачи{' (' + category + ')' if category else ''}:")
    # Сортируем: невыполненные наверх
    sorted_tasks = sorted(filtered_tasks, key=lambda x: x["done"])
    for i, task in enumerate(sorted_tasks, 1):
        mark = "[x]" if task["done"] else "[ ]"
        print(f"{i}. {mark} {task['text']} ({task['category']})")

# Получаем номер задачи с проверкой
def get_task_number(tasks, prompt):
    show_tasks(tasks)
    try:
        num = int(input(prompt))
        if 1 <= num <= len(tasks):
            return num - 1
        print("Неверный номер.")
        return None
    except ValueError:
        print("Нужно ввести число.")
        return None

# Добавляем задачу
def add_task(tasks):
    text = input("Введи задачу: ").strip()
    if not text:
        print("Ошибка: задача не может быть пустой!")
        return
    if any(task["text"] == text for task in tasks):
        print("Ошибка: такая задача уже есть!")
        return
    category = input("Категория (Работа/Личное/другое): ").strip() or "Без категории"
    tasks.append({"done": False, "category": category, "text": text})
    save_tasks(tasks)
    print("Задача добавлена!")

# Отмечаем задачу как выполненную
def mark_task(tasks):
    num = get_task_number(tasks, "Номер выполненной задачи: ")
    if num is not None:
        tasks[num]["done"] = True
        save_tasks(tasks)
        print("Задача отмечена как выполненная!")

# Удаляем задачу
def delete_task(tasks):
    num = get_task_number(tasks, "Номер задачи для удаления: ")
    if num is not None:
        removed = tasks.pop(num)
        save_tasks(tasks)
        print(f"Удалено: {removed['text']}")

# Редактируем задачу
def edit_task(tasks):
    num = get_task_number(tasks, "Номер задачи для редактирования: ")
    if num is not None:
        new_text = input("Новый текст задачи: ").strip()
        if not new_text:
            print("Ошибка: текст не может быть пустым!")
            return
        if any(task["text"] == new_text for task in tasks if task != tasks[num]):
            print("Ошибка: такая задача уже есть!")
            return
        new_category = input("Новая категория (Enter для той же): ").strip()
        tasks[num]["text"] = new_text
        if new_category:
            tasks[num]["category"] = new_category
        save_tasks(tasks)
        print("Задача обновлена!")

# Показываем задачи по категории
def show_by_category(tasks):
    category = input("Введи категорию (или Enter для всех): ").strip()
    show_tasks(tasks, category or None)

# Основной цикл
def main():
    tasks = load_tasks()
    
    while True:
        print("\n=== Список дел ===")
        print("1. Показать все задачи")
        print("2. Показать задачи по категории")
        print("3. Добавить задачу")
        print("4. Отметить как выполненную")
        print("5. Удалить задачу")
        print("6. Редактировать задачу")
        print("7. Выйти")
        
        choice = input("Твой выбор: ").strip()
        
        if choice == "1":
            show_tasks(tasks)
        elif choice == "2":
            show_by_category(tasks)
        elif choice == "3":
            add_task(tasks)
        elif choice == "4":
            mark_task(tasks)
        elif choice == "5":
            delete_task(tasks)
        elif choice == "6":
            edit_task(tasks)
        elif choice == "7":
            print("Пока!")
            break
        else:
            print("Неверный выбор, попробуй снова.")

if __name__ == "__main__":
    main()