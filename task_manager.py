import os
import json
import logging
import configparser
from datetime import datetime, timedelta

try:
    from colorama import init, Fore, Style
    init()
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False

# Настройка логирования
logging.basicConfig(filename="errors.log", level=logging.ERROR, encoding="utf-8")

# Конфигурация
CONFIG_FILE = "config.ini"
FILENAME = "todo.txt"
ARCHIVE_FILENAME = "archive.txt"

def load_config():
    config = configparser.ConfigParser(interpolation=None)  # Отключаем интерполяцию
    config.read('config.ini')
    config.set("DEFAULT", "date_format", "%Y-%m-%d")  # Устанавливаем через set()
    return config
    

CONFIG = load_config()
DATE_FORMAT = CONFIG["DEFAULT"]["date_format"]

class TaskManager:
    """Класс для управления задачами с поддержкой категорий, приоритетов, дедлайнов, тегов, подзадач и повторений."""
    
    def __init__(self):
        self.tasks = self.load_tasks(FILENAME)
        self.categories = set(task["category"] for task in self.tasks if task["category"])
        self.show_notifications()

    def load_tasks(self, filename):
        """Загружает задачи из текстового файла."""
        tasks = []
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        parts = line.strip().split("|")
                        if len(parts) < 4:
                            raise ValueError("Неверный формат строки")
                        status, category, text, priority = parts[:4]
                        deadline = parts[4] if len(parts) > 4 else ""
                        tags = parts[5].split(",") if len(parts) > 5 and parts[5] else []
                        repeat = parts[6] if len(parts) > 6 else ""
                        subtasks = json.loads(parts[7]) if len(parts) > 7 and parts[7] else []
                        tasks.append({
                            "done": status == "1",
                            "category": category,
                            "text": text,
                            "priority": priority,
                            "deadline": deadline,
                            "tags": tags,
                            "repeat": repeat,
                            "subtasks": subtasks
                        })
                    except Exception as e:
                        logging.error(f"Ошибка загрузки строки: {line.strip()}, {str(e)}")
        return tasks

    def save_tasks(self, filename, tasks):
        """Сохраняет задачи в текстовый файл."""
        with open(filename, "w", encoding="utf-8") as f:
            for task in tasks:
                status = "1" if task["done"] else "0"
                tags = ",".join(task["tags"])
                subtasks = json.dumps(task["subtasks"], ensure_ascii=False)
                f.write(f"{status}|{task['category']}|{task['text']}|{task['priority']}|{task['deadline']}|{tags}|{task['repeat']}|{subtasks}\n")

    def is_overdue(self, deadline):
        """Проверяет, просрочена ли задача."""
        if not deadline:
            return False
        try:
            deadline_date = datetime.strptime(deadline, DATE_FORMAT).date()
            today = datetime.now().date()
            return deadline_date < today
        except ValueError:
            return False

    def is_urgent(self, deadline):
        """Проверяет, является ли задача срочной (сегодня/завтра)."""
        if not deadline:
            return False
        try:
            deadline_date = datetime.strptime(deadline, DATE_FORMAT).date()
            today = datetime.now().date()
            tomorrow = today + timedelta(days=1)
            return deadline_date in [today, tomorrow]
        except ValueError:
            return False

    def filter_tasks(self, category=None, priority=None, tag=None, only_overdue=False, only_urgent=False, search_text=None):
        """Фильтрует задачи по заданным критериям."""
        filtered = self.tasks
        if category:
            filtered = [t for t in filtered if t["category"] == category]
        if priority:
            filtered = [t for t in filtered if t["priority"] == priority]
        if tag:
            filtered = [t for t in filtered if tag in t["tags"]]
        if only_overdue:
            filtered = [t for t in filtered if self.is_overdue(t["deadline"])]
        if only_urgent:
            filtered = [t for t in filtered if self.is_urgent(t["deadline"])]
        if search_text:
            search_text = search_text.lower()
            filtered = [t for t in filtered if search_text in t["text"].lower() or any(search_text in st["text"].lower() for st in t["subtasks"])]
        return filtered

    def show_tasks(self, category=None, priority=None, tag=None, only_overdue=False, only_urgent=False, search_text=None):
        """Показывает отфильтрованные задачи."""
        filtered_tasks = self.filter_tasks(category, priority, tag, only_overdue, only_urgent, search_text)
        if not filtered_tasks:
            print("Список пуст или нет задач по заданным критериям.")
            return
        
        title = "Текущие задачи"
        if category:
            title += f" ({category})"
        elif priority:
            title += f" ({priority})"
        elif tag:
            title += f" (тег: {tag})"
        elif only_overdue:
            title += " (просроченные)"
        elif only_urgent:
            title += " (срочные)"
        elif search_text:
            title += f" (поиск: {search_text})"
        print(f"\n{title}:")

        priority_order = {"высокий": 1, "средний": 2, "низкий": 3}
        def sort_key(task):
            deadline = task["deadline"]
            deadline_score = datetime(9999, 12, 31) if not deadline else datetime.strptime(deadline, DATE_FORMAT)
            return (deadline_score, priority_order.get(task["priority"], 3), task["done"])
        sorted_tasks = sorted(filtered_tasks, key=sort_key)
        
        for i, task in enumerate(sorted_tasks, 1):
            mark = "[x]" if task["done"] else "[ ]"
            overdue = "[Просрочено]" if self.is_overdue(task["deadline"]) else ""
            urgent = "[Срочно]" if self.is_urgent(task["deadline"]) and not task["done"] else ""
            deadline = f", до {task['deadline']}" if task["deadline"] else ""
            tags = f", теги: {', '.join(task['tags'])}" if task["tags"] else ""
            repeat = f", повтор: {task['repeat']}" if task["repeat"] else ""
            line = f"{i}. {mark} {task['text']} ({task['category']}, {task['priority']}{deadline}{tags}{repeat}) {overdue}{urgent}"
            if COLORAMA_AVAILABLE and overdue:
                line = Fore.RED + line + Style.RESET_ALL
            print(line)
            for j, subtask in enumerate(task["subtasks"], 1):
                sub_mark = "[x]" if subtask["done"] else "[ ]"
                print(f"   {i}.{j}. {sub_mark} {subtask['text']}")

    def get_task_number(self, prompt):
        """Получает номер задачи с проверкой."""
        self.show_tasks()
        try:
            num = int(input(prompt))
            if 1 <= num <= len(self.tasks):
                return num - 1
            print("Неверный номер.")
            return None
        except ValueError:
            print("Нужно ввести число.")
            return None

    def get_priority(self, prompt="Приоритет (высокий/средний/низкий): "):
        """Получает приоритет с проверкой."""
        priority = input(prompt).strip().lower()
        if priority not in ["высокий", "средний", "низкий"]:
            print("Неверный приоритет, установлен 'средний'.")
            return "средний"
        return priority

    def get_deadline(self, prompt="Дедлайн (ГГГГ-ММ-ДД или Enter для без даты): "):
        """Получает дедлайн с проверкой."""
        deadline = input(prompt).strip()
        if not deadline:
            return ""
        try:
            datetime.strptime(deadline, DATE_FORMAT)
            return deadline
        except ValueError:
            print("Неверный формат даты, дедлайн не установлен.")
            return ""

    def get_category(self, prompt="Категория (Работа/Личное/другое): "):
        """Получает категорию с автодополнением."""
        print(f"Известные категории: {', '.join(sorted(self.categories)) or 'нет категорий'}")
        category = input(prompt).strip() or "Без категории"
        self.categories.add(category)
        return category

    def get_tags(self, prompt="Теги через запятую (или Enter для без тегов): "):
        """Получает теги."""
        tags = input(prompt).strip()
        return [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []

    def get_repeat(self, prompt="Повторение (ежедневно/еженедельно/нет): "):
        """Получает правило повторения."""
        repeat = input(prompt).strip().lower()
        return repeat if repeat in ["ежедневно", "еженедельно", ""] else ""

    def get_subtasks(self, prompt="Подзадачи через запятую (или Enter для без подзадач): "):
        """Получает подзадачи."""
        subtasks_input = input(prompt).strip()
        if not subtasks_input:
            return []
        return [{"text": text.strip(), "done": False} for text in subtasks_input.split(",") if text.strip()]

    def add_task(self):
        """Добавляет новую задачу."""
        text = input("Введи задачу: ").strip()
        if not text:
            print("Ошибка: задача не может быть пустой!")
            return
        if any(task["text"] == text for task in self.tasks):
            print("Ошибка: такая задача уже есть!")
            return
        category = self.get_category()
        priority = self.get_priority()
        deadline = self.get_deadline()
        tags = self.get_tags()
        repeat = self.get_repeat()
        subtasks = self.get_subtasks()
        self.tasks.append({
            "done": False,
            "category": category,
            "text": text,
            "priority": priority,
            "deadline": deadline,
            "tags": tags,
            "repeat": repeat,
            "subtasks": subtasks
        })
        self.save_tasks(FILENAME, self.tasks)
        print("Задача добавлена!")

    def mark_task(self, done=True):
        """Отмечает или снимает отметку с задачи."""
        num = self.get_task_number("Номер задачи: ")
        if num is not None:
            task = self.tasks[num]
            task["done"] = done
            if done and task["repeat"]:
                self._handle_repeat(task)
            self.save_tasks(FILENAME, self.tasks)
            print(f"Задача {'отмечена как выполненная' if done else 'снята с выполнения'}!")

    def _handle_repeat(self, task):
        """Обрабатывает повторяющиеся задачи."""
        if task["repeat"] == "ежедневно":
            new_deadline = (datetime.strptime(task["deadline"], DATE_FORMAT) + timedelta(days=1)).strftime(DATE_FORMAT) if task["deadline"] else ""
        elif task["repeat"] == "еженедельно":
            new_deadline = (datetime.strptime(task["deadline"], DATE_FORMAT) + timedelta(weeks=1)).strftime(DATE_FORMAT) if task["deadline"] else ""
        else:
            return
        self.tasks.append({
            "done": False,
            "category": task["category"],
            "text": task["text"],
            "priority": task["priority"],
            "deadline": new_deadline,
            "tags": task["tags"].copy(),
            "repeat": task["repeat"],
            "subtasks": [{"text": st["text"], "done": False} for st in task["subtasks"]]
        })

    def mark_multiple_tasks(self):
        """Отмечает несколько задач как выполненные."""
        self.show_tasks()
        numbers = input("Введи номера задач через запятую: ").strip()
        try:
            indices = [int(n) - 1 for n in numbers.split(",") if n.strip()]
            valid_indices = [i for i in indices if 0 <= i < len(self.tasks)]
            if not valid_indices:
                print("Нет корректных номеров.")
                return
            for i in valid_indices:
                self.tasks[i]["done"] = True
                if self.tasks[i]["repeat"]:
                    self._handle_repeat(self.tasks[i])
            self.save_tasks(FILENAME, self.tasks)
            print(f"Отмечено задач: {len(valid_indices)}")
        except ValueError:
            print("Нужно ввести числа через запятую.")

    def mark_subtask(self):
        """Отмечает подзадачу."""
        num = self.get_task_number("Номер задачи: ")
        if num is not None:
            task = self.tasks[num]
            if not task["subtasks"]:
                print("У задачи нет подзадач.")
                return
            print("\nПодзадачи:")
            for j, subtask in enumerate(task["subtasks"], 1):
                mark = "[x]" if subtask["done"] else "[ ]"
                print(f"{j}. {mark} {subtask['text']}")
            try:
                sub_num = int(input("Номер подзадачи: ")) - 1
                if 0 <= sub_num < len(task["subtasks"]):
                    task["subtasks"][sub_num]["done"] = not task["subtasks"][sub_num]["done"]
                    self.save_tasks(FILENAME, self.tasks)
                    print("Подзадача обновлена!")
                else:
                    print("Неверный номер подзадачи.")
            except ValueError:
                print("Нужно ввести число.")

    def delete_task(self):
        """Удаляет задачу."""
        num = self.get_task_number("Номер задачи для удаления: ")
        if num is not None:
            removed = self.tasks.pop(num)
            self.save_tasks(FILENAME, self.tasks)
            print(f"Удалено: {removed['text']}")

    def edit_task(self):
        """Редактирует задачу."""
        num = self.get_task_number("Номер задачи для редактирования: ")
        if num is not None:
            task = self.tasks[num]
            new_text = input("Новый текст задачи (Enter для того же): ").strip() or task["text"]
            if new_text != task["text"] and any(t["text"] == new_text for t in self.tasks if t != task):
                print("Ошибка: такая задача уже есть!")
                return
            new_category = input("Новая категория (Enter для той же): ").strip() or task["category"]
            self.categories.add(new_category)
            new_priority = input("Новый приоритет (Enter для того же): ").strip().lower()
            new_priority = self.get_priority("Новый приоритет: ") if new_priority else task["priority"]
            new_deadline = input("Новый дедлайн (ГГГГ-ММ-ДД или Enter): ").strip()
            new_deadline = self.get_deadline("Новый дедлайн: ") if new_deadline else task["deadline"]
            new_tags = self.get_tags("Новые теги через запятую (Enter для тех же): ") or task["tags"]
            new_repeat = input("Новое повторение (ежедневно/еженедельно/нет, Enter для того же): ").strip().lower()
            new_repeat = self.get_repeat("Новое повторение: ") if new_repeat else task["repeat"]
            new_subtasks = self.get_subtasks("Новые подзадачи через запятую (Enter для тех же): ") or task["subtasks"]
            task["text"] = new_text
            task["category"] = new_category
            task["priority"] = new_priority
            task["deadline"] = new_deadline
            task["tags"] = new_tags
            task["repeat"] = new_repeat
            task["subtasks"] = new_subtasks
            self.save_tasks(FILENAME, self.tasks)
            print("Задача обновлена!")

    def show_by_category(self):
        """Показывает задачи по категории."""
        category = input("Введи категорию (или Enter для всех): ").strip()
        self.show_tasks(category=category or None)

    def show_by_priority(self):
        """Показывает задачи по приоритету."""
        priority = self.get_priority("Введи приоритет (высокий/средний/низкий): ")
        self.show_tasks(priority=priority)

    def show_by_tag(self):
        """Показывает задачи по тегу."""
        tag = input("Введи тег: ").strip()
        if tag:
            self.show_tasks(tag=tag)

    def show_by_text(self):
        """Ищет задачи по тексту."""
        search_text = input("Введи текст для поиска: ").strip()
        if search_text:
            self.show_tasks(search_text=search_text)

    def show_overdue(self):
        """Показывает просроченные задачи."""
        self.show_tasks(only_overdue=True)

    def show_urgent(self):
        """Показывает срочные задачи."""
        self.show_tasks(only_urgent=True)

    def clear_done_tasks(self):
        """Архивирует и удаляет выполненные задачи."""
        done_tasks = [task for task in self.tasks if task["done"]]
        if not done_tasks:
            print("Нет выполненных задач.")
            return
        archive_tasks = self.load_tasks(ARCHIVE_FILENAME)
        archive_tasks.extend(done_tasks)
        self.save_tasks(ARCHIVE_FILENAME, archive_tasks)
        self.tasks[:] = [task for task in self.tasks if not task["done"]]
        self.save_tasks(FILENAME, self.tasks)
        print(f"Архивировано и удалено задач: {len(done_tasks)}")

    def show_archive(self):
        """Показывает архив задач."""
        archive_tasks = self.load_tasks(ARCHIVE_FILENAME)
        if not archive_tasks:
            print("Архив пуст.")
            return
        print("\nАрхивированные задачи:")
        for i, task in enumerate(archive_tasks, 1):
            deadline = f", до {task['deadline']}" if task["deadline"] else ""
            tags = f", теги: {', '.join(task['tags'])}" if task["tags"] else ""
            repeat = f", повтор: {task['repeat']}" if task["repeat"] else ""
            line = f"{i}. [x] {task['text']} ({task['category']}, {task['priority']}{deadline}{tags}{repeat})"
            print(line)
            for j, subtask in enumerate(task["subtasks"], 1):
                sub_mark = "[x]" if subtask["done"] else "[ ]"
                print(f"   {i}.{j}. {sub_mark} {subtask['text']}")

    def show_stats(self):
        """Показывает статистику с прогресс-баром."""
        total = len(self.tasks)
        done = sum(1 for task in self.tasks if task["done"])
        overdue = sum(1 for task in self.tasks if self.is_overdue(task["deadline"]))
        urgent = sum(1 for task in self.tasks if self.is_urgent(task["deadline"]) and not task["done"])
        sub_total = sum(len(task["subtasks"]) for task in self.tasks)
        sub_done = sum(sum(1 for st in task["subtasks"] if st["done"]) for task in self.tasks)
        
        # Прогресс-бар
        bar_length = 20
        done_ratio = done / total if total else 0
        bar_filled = int(bar_length * done_ratio)
        bar = "#" * bar_filled + "-" * (bar_length - bar_filled)
        progress = f"[{bar}] {done_ratio:.0%}"
        
        print(f"\nСтатистика задач:")
        print(f"Всего задач: {total}")
        print(f"Выполнено: {done}")
        print(f"Осталось: {total - done}")
        print(f"Просрочено: {overdue}")
        print(f"Срочных (сегодня/завтра): {urgent}")
        print(f"Всего подзадач: {sub_total}")
        print(f"Выполнено подзадач: {sub_done}")
        print(f"Прогресс: {progress}")

    def export_to_json(self):
        """Экспортирует задачи в JSON."""
        with open("tasks.json", "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)
        print("Задачи экспортированы в tasks.json")

    def import_from_json(self):
        """Импортирует задачи из JSON."""
        if not os.path.exists("tasks.json"):
            print("Файл tasks.json не найден.")
            return
        try:
            with open("tasks.json", "r", encoding="utf-8") as f:
                imported_tasks = json.load(f)
            for task in imported_tasks:
                if not isinstance(task, dict) or "text" not in task:
                    raise ValueError("Неверный формат задачи")
                task.setdefault("done", False)
                task.setdefault("category", "Без категории")
                task.setdefault("priority", "средний")
                task.setdefault("deadline", "")
                task.setdefault("tags", [])
                task.setdefault("repeat", "")
                task.setdefault("subtasks", [])
                if task["text"] not in (t["text"] for t in self.tasks):
                    self.tasks.append(task)
                    self.categories.add(task["category"])
            self.save_tasks(FILENAME, self.tasks)
            print("Задачи импортированы из tasks.json")
        except Exception as e:
            logging.error(f"Ошибка импорта JSON: {str(e)}")
            print("Ошибка при импорте задач.")

    def show_notifications(self):
        """Показывает уведомления о срочных и просроченных задачах."""
        urgent = [t for t in self.tasks if self.is_urgent(t["deadline"]) and not t["done"]]
        overdue = [t for t in self.tasks if self.is_overdue(t["deadline"]) and not t["done"]]
        if urgent or overdue:
            print("\nУведомления:")
            for task in urgent:
                print(f"Срочная задача: {task['text']} (до {task['deadline']})")
            for task in overdue:
                line = f"Просрочена: {task['text']} (было до {task['deadline']})"
                if COLORAMA_AVAILABLE:
                    line = Fore.RED + line + Style.RESET_ALL
                print(line)

def main():
    """Основной цикл программы."""
    manager = TaskManager()
    
    while True:
        print("\n=== Список дел ===")
        print("1. Показать все задачи")
        print("2. Показать задачи по категории")
        print("3. Показать задачи по приоритету")
        print("4. Показать задачи по тегу")
        print("5. Показать задачи по тексту")
        print("6. Показать просроченные задачи")
        print("7. Показать срочные задачи")
        print("8. Добавить задачу")
        print("9. Отметить как выполненную")
        print("10. Снять отметку выполнения")
        print("11. Отметить несколько задач")
        print("12. Отметить подзадачу")
        print("13. Удалить задачу")
        print("14. Редактировать задачу")
        print("15. Очистить и архивировать выполненные")
        print("16. Показать архив")
        print("17. Показать статистику")
        print("18. Экспортировать в JSON")
        print("19. Импортировать из JSON")
        print("20. Выйти")
        
        choice = input("Твой выбор (1-20): ").strip()
        
        if choice == "1":
            manager.show_tasks()
        elif choice == "2":
            manager.show_by_category()
        elif choice == "3":
            manager.show_by_priority()
        elif choice == "4":
            manager.show_by_tag()
        elif choice == "5":
            manager.show_by_text()
        elif choice == "6":
            manager.show_overdue()
        elif choice == "7":
            manager.show_urgent()
        elif choice == "8":
            manager.add_task()
        elif choice == "9":
            manager.mark_task(done=True)
        elif choice == "10":
            manager.mark_task(done=False)
        elif choice == "11":
            manager.mark_multiple_tasks()
        elif choice == "12":
            manager.mark_subtask()
        elif choice == "13":
            manager.delete_task()
        elif choice == "14":
            manager.edit_task()
        elif choice == "15":
            manager.clear_done_tasks()
        elif choice == "16":
            manager.show_archive()
        elif choice == "17":
            manager.show_stats()
        elif choice == "18":
            manager.export_to_json()
        elif choice == "19":
            manager.import_from_json()
        elif choice == "20":
            print("Пока! Все задачи сохранены.")
            break
        else:
            print("Неверный выбор, попробуй снова.")

if __name__ == "__main__":
    main()