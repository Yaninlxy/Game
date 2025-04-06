import tkinter as tk
from tkinter import messagebox
import os

FILENAME = "todo.txt"

class ToDoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Список дел")
        self.tasks = []
        self.check_vars = []

        # Виджеты
        self.entry = tk.Entry(root, width=40)
        self.entry.pack(pady=5)

        self.add_button = tk.Button(root, text="Добавить задачу", command=self.add_task)
        self.add_button.pack(pady=5)

        self.frame = tk.Frame(root)
        self.frame.pack(pady=5)

        self.delete_button = tk.Button(root, text="Удалить выполненные", command=self.delete_done)
        self.delete_button.pack(pady=5)

        self.load_tasks()

    def load_tasks(self):
        if os.path.exists(FILENAME):
            with open(FILENAME, "r", encoding="utf-8") as f:
                for line in f:
                    status, text = line.strip().split("|", 1)
                    self.add_task_to_ui(text, status == "1", save=False)

    def save_tasks(self):
        with open(FILENAME, "w", encoding="utf-8") as f:
            for var, task in zip(self.check_vars, self.tasks):
                status = "1" if var.get() else "0"
                f.write(f"{status}|{task}\n")

    def add_task(self):
        text = self.entry.get().strip()
        if not text:
            messagebox.showwarning("Ошибка", "Нельзя добавить пустую задачу.")
            return
        self.add_task_to_ui(text)
        self.entry.delete(0, tk.END)

    def add_task_to_ui(self, text, done=False, save=True):
        var = tk.BooleanVar(value=done)
        cb = tk.Checkbutton(self.frame, text=text, variable=var, anchor="w", width=40)
        cb.pack(anchor="w")
        self.check_vars.append(var)
        self.tasks.append(text)
        if save:
            self.save_tasks()

    def delete_done(self):
        new_tasks = []
        new_vars = []
        for widget, var, task in zip(self.frame.winfo_children(), self.check_vars, self.tasks):
            if not var.get():
                new_tasks.append(task)
                new_vars.append(var)
            else:
                widget.destroy()
        self.tasks = new_tasks
        self.check_vars = new_vars
        self.save_tasks()


root = tk.Tk()
app = ToDoApp(root)
root.mainloop()
