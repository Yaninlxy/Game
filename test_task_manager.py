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

if __name__ == "__main__":
    test_add_task()
    print("Тесты пройдены!")