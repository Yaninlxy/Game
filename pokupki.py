# Создаём пустой список
shopping_list = []

while True:
    print("\nСписок покупок:")
    print("1. Добавить продукт")
    print("2. Показать список")
    print("3. Удалить продукт")
    print("4. Выход")
    
    choice = input("Выбери действие (1-4): ")
    
    if choice == "1":
        item = input("Введи продукт: ")
        shopping_list.append(item)
        print(f"{item} добавлен!")
    
    elif choice == "2":
        if shopping_list:
            print("Твой список:")
            for item in shopping_list:
                print(f"- {item}")
        else:
            print("Список пуст!")
    
    elif choice == "3":
        item = input("Какой продукт удалить? ")
        if item in shopping_list:
            shopping_list.remove(item)
            print(f"{item} удалён!")
        else:
            print("Такого продукта нет в списке!")
    
    elif choice == "4":
        print("Пока!")
        break
    
    else:
        print("Выбери 1, 2, 3 или 4!")