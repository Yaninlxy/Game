from task_manager import TaskManager

def test_add_task():
    manager = TaskManager()
    initial_len = len(manager.tasks)
    manager.tasks.append({
        "done": False,
        "category": "Тест",
        "text": "Тестовая задача",
        "priority": "средний",
        "deadline": "",
        "tags": [],
        "repeat": "",
        "subtasks": []
    })
    assert len(manager.tasks) == initial_len + 1
    assert manager.tasks[-1]["text"] == "Тестовая задача"

def test_save_tasks():
    manager = TaskManager()
    manager.tasks = [{"done": False, "category": "Тест", "text": "Сохранить", "priority": "средний", "deadline": "", "tags": [], "repeat": "", "subtasks": []}]
    manager.save_tasks("test_todo.txt", manager.tasks)
    assert os.path.exists("test_todo.txt")
    os.remove("test_todo.txt")

if __name__ == "__main__":
    test_add_task()
    test_save_tasks()
    print("Тесты пройдены!")