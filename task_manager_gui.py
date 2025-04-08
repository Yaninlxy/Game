import os
import json
import logging
from datetime import datetime, timedelta
import configparser
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

# Настройка логирования
logging.basicConfig(filename="errors.log", level=logging.ERROR, encoding="utf-8")

# Конфигурация
CONFIG_FILE = "config.ini"
FILENAME = "todo.txt"
ARCHIVE_FILENAME = "archive.txt"

def load_config():
    """Загружает конфигурацию из config.ini."""
    config = configparser.ConfigParser(interpolation=None)
    config.read(CONFIG_FILE)
    config.set("DEFAULT", "date_format", "%Y-%m-%d")
    return config

CONFIG = load_config()
DATE_FORMAT = CONFIG["DEFAULT"]["date_format"]

class TaskManager:
    def __init__(self):
        self.tasks = self.load_tasks(FILENAME)
        self.categories = set(task["category"] for task in self.tasks if task["category"])

    def load_tasks(self, filename):
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
        with open(filename, "w", encoding="utf-8") as f:
            for task in tasks:
                status = "1" if task["done"] else "0"
                tags = ",".join(task["tags"])
                subtasks = json.dumps(task["subtasks"], ensure_ascii=False)
                f.write(f"{status}|{task['category']}|{task['text']}|{task['priority']}|{task['deadline']}|{tags}|{task['repeat']}|{subtasks}\n")

    def is_overdue(self, deadline):
        if not deadline:
            return False
        try:
            deadline_date = datetime.strptime(deadline, DATE_FORMAT).date()
            today = datetime.now().date()
            return deadline_date < today
        except ValueError:
            return False

    def is_urgent(self, deadline):
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

    def export_to_ics(self):
        ics_content = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//LegendaryTaskManager//Grok3//EN",
            "CALSCALE:GREGORIAN"
        ]
        for task in self.tasks:
            if task["deadline"]:
                try:
                    deadline = datetime.strptime(task["deadline"], DATE_FORMAT)
                    uid = f"{task['text'].replace(' ', '_')}_{deadline.strftime('%Y%m%d')}@legendarytaskmanager"
                    description = f"Категория: {task['category']}\\nПриоритет: {task['priority']}"
                    if task["tags"]:
                        description += f"\\nТеги: {', '.join(task['tags'])}"
                    if task["repeat"]:
                        description += f"\\nПовтор: {task['repeat']}"
                    if task["subtasks"]:
                        subtask_list = "\\nПодзадачи:\\n" + "\\n".join(f"- {'[x]' if st['done'] else '[ ]'} {st['text']}" for st in task["subtasks"])
                        description += subtask_list
                    ics_content.extend([
                        "BEGIN:VEVENT",
                        f"UID:{uid}",
                        f"DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%SZ')}",
                        f"DTSTART;VALUE=DATE:{deadline.strftime('%Y%m%d')}",
                        f"DTEND;VALUE=DATE:{deadline.strftime('%Y%m%d')}",
                        f"SUMMARY:{task['text']}",
                        f"DESCRIPTION:{description}",
                        "STATUS:CONFIRMED",
                        "END:VEVENT"
                    ])
                except ValueError:
                    logging.error(f"Неверный формат даты для задачи: {task['text']}")
        ics_content.append("END:VCALENDAR")
        with open("tasks.ics", "w", encoding="utf-8") as f:
            f.write("\n".join(ics_content))

    def export_to_json(self):
        with open("tasks.json", "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)

def parse_date(date_str):
    """Парсит дату из строки в разных форматах и возвращает в формате %Y-%m-%d."""
    if not date_str:
        return ""
    
    # Список поддерживаемых форматов
    date_formats = [
        "%Y-%m-%d",    # 2025-04-09
        "%d.%m.%Y",    # 09.04.2025
        "%d-%m-%Y",    # 09-04-2025
        "%Y/%m/%d",    # 2025/04/09
        "%d/%m/%Y",    # 09/04/2025
        "%Y.%m.%d",    # 2025.04.09
    ]
    
    for fmt in date_formats:
        try:
            parsed_date = datetime.strptime(date_str.strip(), fmt)
            return parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            continue
    
    # Если ни один формат не подошёл
    examples = "Примеры: 2025-04-09, 09.04.2025, 09-04-2025, 2025/04/09"
    raise ValueError(f"Неверный формат даты! {examples}")

class AddTaskDialog(tk.Toplevel):
    def __init__(self, parent, manager):
        super().__init__(parent)
        self.manager = manager
        self.title("Добавить задачу")
        self.geometry("400x300")
        self.transient(parent)
        self.grab_set()

        ttk.Label(self, text="Текст задачи:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.text_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.text_var).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(self, text="Категория:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.category_var = tk.StringVar(value="")
        ttk.Combobox(self, textvariable=self.category_var, values=list(self.manager.categories) + ["Без категории"]).grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(self, text="Приоритет:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.priority_var = tk.StringVar(value="средний")
        ttk.Combobox(self, textvariable=self.priority_var, values=["высокий", "средний", "низкий"]).grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(self, text="Дедлайн:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.deadline_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.deadline_var).grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        ttk.Button(self, text="Добавить", command=self.add_task).grid(row=4, column=0, columnspan=2, pady=10)

        self.columnconfigure(1, weight=1)

    def add_task(self):
        text = self.text_var.get().strip()
        if not text:
            messagebox.showerror("Ошибка", "Текст задачи не может быть пустым!")
            return
        if any(task["text"] == text for task in self.manager.tasks):
            messagebox.showerror("Ошибка", "Такая задача уже существует!")
            return

        category = self.category_var.get()
        priority = self.priority_var.get()
        if priority not in ["высокий", "средний", "низкий"]:
            priority = "средний"
        deadline = self.deadline_var.get().strip()
        if deadline:
            try:
                deadline = parse_date(deadline)
            except ValueError as e:
                messagebox.showerror("Ошибка", str(e))
                return

        self.manager.tasks.append({
            "done": False,
            "category": category,
            "text": text,
            "priority": priority,
            "deadline": deadline,
            "tags": [],
            "repeat": "",
            "subtasks": []
        })
        self.manager.save_tasks(FILENAME, self.manager.tasks)
        self.manager.categories.add(category)
        self.destroy()

class TaskManagerApp:
    def __init__(self, root):
        self.manager = TaskManager()
        self.root = root
        self.root.title("Легендарный Менеджер Задач")
        self.root.geometry("800x600")

        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.grid(row=0, column=0, sticky="nw")

        ttk.Button(self.button_frame, text="Добавить задачу", command=self.add_task).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(self.button_frame, text="Отметить выполненной", command=self.mark_task).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.button_frame, text="Удалить задачу", command=self.delete_task).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(self.button_frame, text="Экспорт в iCalendar", command=self.export_to_ics).grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(self.button_frame, text="Экспорт в JSON", command=self.export_to_json).grid(row=0, column=4, padx=5, pady=5)

        self.filter_frame = ttk.LabelFrame(self.main_frame, text="Фильтры", padding="5")
        self.filter_frame.grid(row=1, column=0, sticky="ew", pady=10)

        ttk.Label(self.filter_frame, text="Категория:").grid(row=0, column=0, padx=5)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(self.filter_frame, textvariable=self.category_var, values=["Все"] + list(self.manager.categories))
        self.category_combo.grid(row=0, column=1, padx=5)
        self.category_combo.set("Все")

        ttk.Label(self.filter_frame, text="Приоритет:").grid(row=0, column=2, padx=5)
        self.priority_var = tk.StringVar()
        self.priority_combo = ttk.Combobox(self.filter_frame, textvariable=self.priority_var, values=["Все", "высокий", "средний", "низкий"])
        self.priority_combo.grid(row=0, column=3, padx=5)
        self.priority_combo.set("Все")

        ttk.Label(self.filter_frame, text="Поиск:").grid(row=0, column=4, padx=5)
        self.search_var = tk.StringVar()
        ttk.Entry(self.filter_frame, textvariable=self.search_var).grid(row=0, column=5, padx=5)

        ttk.Button(self.filter_frame, text="Применить фильтр", command=self.update_task_list).grid(row=0, column=6, padx=5)

        self.task_frame = ttk.LabelFrame(self.main_frame, text="Задачи", padding="5")
        self.task_frame.grid(row=2, column=0, sticky="nsew")

        self.task_tree = ttk.Treeview(self.task_frame, columns=("Done", "Text", "Category", "Priority", "Deadline"), show="headings")
        self.task_tree.heading("Done", text="Выполнено")
        self.task_tree.heading("Text", text="Задача")
        self.task_tree.heading("Category", text="Категория")
        self.task_tree.heading("Priority", text="Приоритет")
        self.task_tree.heading("Deadline", text="Дедлайн")
        self.task_tree.column("Done", width=70, anchor="center")
        self.task_tree.column("Text", width=200)
        self.task_tree.column("Category", width=100)
        self.task_tree.column("Priority", width=100)
        self.task_tree.column("Deadline", width=100)
        self.task_tree.grid(row=0, column=0, sticky="nsew")

        self.scrollbar = ttk.Scrollbar(self.task_frame, orient="vertical", command=self.task_tree.yview)
        self.task_tree.configure(yscroll=self.scrollbar.set)
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(2, weight=1)
        self.task_frame.columnconfigure(0, weight=1)
        self.task_frame.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.update_task_list()

    def update_task_list(self):
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)

        category = self.category_var.get() if self.category_var.get() != "Все" else None
        priority = self.priority_var.get() if self.priority_var.get() != "Все" else None
        search_text = self.search_var.get() if self.search_var.get() else None

        filtered_tasks = self.manager.filter_tasks(category=category, priority=priority, search_text=search_text)
        
        for task in filtered_tasks:
            done_mark = "[x]" if task["done"] else "[ ]"
            text = task["text"]
            if self.manager.is_overdue(task["deadline"]):
                text += " [Просрочено]"
            elif self.manager.is_urgent(task["deadline"]) and not task["done"]:
                text += " [Срочно]"
            self.task_tree.insert("", "end", values=(done_mark, text, task["category"], task["priority"], task["deadline"] or ""))

    def add_task(self):
        dialog = AddTaskDialog(self.root, self.manager)
        self.root.wait_window(dialog)
        self.category_combo["values"] = ["Все"] + list(self.manager.categories)
        self.update_task_list()

    def mark_task(self):
        selected = self.task_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выбери задачу!")
            return
        
        item = self.task_tree.item(selected[0])
        values = item["values"]
        if not values or len(values) < 2:
            messagebox.showerror("Ошибка", "Не удалось определить задачу!")
            return
        
        task_text = str(values[1]).split(" [")[0]
        for task in self.manager.tasks:
            if task["text"] == task_text:
                task["done"] = not task["done"]
                break
        self.manager.save_tasks(FILENAME, self.manager.tasks)
        self.update_task_list()

    def delete_task(self):
        selected = self.task_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выбери задачу!")
            return
        
        item = self.task_tree.item(selected[0])
        values = item["values"]
        if not values or len(values) < 2:
            messagebox.showerror("Ошибка", "Не удалось определить задачу!")
            return
        
        task_text = str(values[1]).split(" [")[0]
        self.manager.tasks = [task for task in self.manager.tasks if task["text"] != task_text]
        self.manager.save_tasks(FILENAME, self.manager.tasks)
        self.update_task_list()
        messagebox.showinfo("Успех", f"Удалено: {task_text}")

    def export_to_ics(self):
        self.manager.export_to_ics()
        messagebox.showinfo("Успех", "Задачи экспортированы в tasks.ics")

    def export_to_json(self):
        self.manager.export_to_json()
        messagebox.showinfo("Успех", "Задачи экспортированы в tasks.json")

def main():
    root = tk.Tk()
    app = TaskManagerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()