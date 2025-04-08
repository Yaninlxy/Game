import os  # Для работы с файлами

# Путь к файлу для сохранения
FILE_PATH = "shopping_list.txt"

# Загружаем список из файла, если он есть
def load_list():
    shopping_list = []
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r", encoding="utf-8") as file:
            shopping_list = [line.strip() for line in file if line.strip()]
    return shopping_list

# Сохраняем список в файл
def save_list(shopping_list):
    with open(FILE_PATH, "w", encoding="utf-8") as file:
        for item in shopping_list:
            file.write(item + "\n")

# Функция для добавления продукта
def add_item(shopping_list):
    item = input("Введи продукт: ").strip()
    if not item:
        print("Ошибка: нельзя добавить пустой продукт!")
    elif item in shopping_list:
        print(f"Ошибка: {item} уже в списке!")
    else:
        shopping_list.append(item)
        save_list(shopping_list)
        print(f"{item} добавлен!")

# Функция для показа списка
def show_list(shopping_list):
    if shopping_list:
        print("Твой список покупок:")
        for index, item in enumerate(shopping_list, 1):
            print(f"{index}. {item}")
    else:
        print("Список пуст!")

# Функция для удаления продукта
def remove_item(shopping_list):
    show_list(shopping_list)
    choice = input("Введи номер продукта для удаления (или название): ").strip()
    
    # Проверяем, ввёл ли пользователь номер
    try:
        index = int(choice) - 1  # Номера начинаются с 1, а индексы с 0
        if 0 <= index < len(shopping_list):
            item = shopping_list.pop(index)
            save_list(shopping_list)
            print(f"{item} удалён!")
        else:
            print("Неверный номер!")
    except ValueError:
        # Если ввели не число, пробуем удалить по названию
        if choice in shopping_list:
            shopping_list.remove(choice)
            save_list(shopping_list)
            print(f"{choice} удалён!")
        else:
            print("Такого продукта нет в списке!")

# Функция для очистки списка
def clear_list(shopping_list):
    if shopping_list:
        shopping_list.clear()
        save_list(shopping_list)
        print("Список очищен!")
    else:
        print("Список и так пуст!")

# Основной цикл программы
def main():
    shopping_list = load_list()  # Загружаем список при старте
    
    while True:
        print("\nСписок покупок:")
        print("1. Добавить продукт")
        print("2. Показать список")
        print("3. Удалить продукт")
        print("4. Очистить список")
        print("5. Выход")
        
        choice = input("Выбери действие (1-5): ").strip()
        
        if choice == "1":
            add_item(shopping_list)
        elif choice == "2":
            show_list(shopping_list)
        elif choice == "3":
            remove_item(shopping_list)
        elif choice == "4":
            clear_list(shopping_list)
        elif choice == "5":
            print("Пока! Твой список сохранён.")
            break
        else:
            print("Выбери 1, 2, 3, 4 или 5!")

# Запускаем программу
if __name__ == "__main__":
    main()