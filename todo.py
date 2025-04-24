import json
import os

# Define the file where tasks will be stored
TASKS_FILE = "tasks.json"

def load_tasks():
    """Loads tasks from the JSON file."""
    if not os.path.exists(TASKS_FILE):
        return []  # Return empty list if file doesn't exist
    try:
        with open(TASKS_FILE, 'r') as f:
            tasks = json.load(f)
            # Ensure structure integrity (basic check)
            if not isinstance(tasks, list):
                print("Warning: Task file format incorrect. Starting fresh.")
                return []
            for task in tasks:
                if not isinstance(task, dict) or 'description' not in task or 'completed' not in task:
                   print("Warning: Invalid task found in file. Skipping it.")
                   # A more robust approach might try to fix or remove just the invalid task
                   # For simplicity here, we might just return [] or filter invalid ones out
                   return [] # Simplest recovery: start fresh if any task is bad
            return tasks
    except json.JSONDecodeError:
        print(f"Warning: Could not decode JSON from {TASKS_FILE}. Starting fresh.")
        return []
    except Exception as e:
        print(f"An error occurred loading tasks: {e}. Starting fresh.")
        return []

def save_tasks(tasks):
    """Saves the current list of tasks to the JSON file."""
    try:
        with open(TASKS_FILE, 'w') as f:
            json.dump(tasks, f, indent=4) # indent for readability
    except Exception as e:
        print(f"An error occurred saving tasks: {e}")

def display_tasks(tasks):
    """Displays the tasks to the user."""
    print("\n--- Your To-Do List ---")
    if not tasks:
        print("No tasks yet!")
        return

    # Find the width needed for the index number
    max_index_width = len(str(len(tasks)))

    for index, task in enumerate(tasks):
        status = "[X]" if task['completed'] else "[ ]"
        # Pad the index number so descriptions align
        print(f"{index + 1:<{max_index_width}}. {status} {task['description']}")
    print("-----------------------\n")

def add_task(tasks):
    """Prompts the user to add a new task."""
    description = input("Enter the task description: ")
    if description:
        tasks.append({"description": description, "completed": False})
        print(f"Task '{description}' added.")
        save_tasks(tasks)
    else:
        print("Task description cannot be empty.")

def mark_complete(tasks):
    """Marks a specific task as complete."""
    display_tasks(tasks)
    if not tasks:
        return

    while True:
        try:
            choice = input("Enter the number of the task to mark as complete (or 'c' to cancel): ")
            if choice.lower() == 'c':
                return
            task_index = int(choice) - 1 # User sees 1-based index

            if 0 <= task_index < len(tasks):
                if tasks[task_index]['completed']:
                     print(f"Task {task_index + 1} is already marked as complete.")
                else:
                    tasks[task_index]['completed'] = True
                    print(f"Task {task_index + 1} marked as complete.")
                    save_tasks(tasks)
                break # Exit the loop after valid input
            else:
                print("Invalid task number.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        except IndexError:
             print("Invalid task number (Index out of range).")


def delete_task(tasks):
    """Deletes a specific task."""
    display_tasks(tasks)
    if not tasks:
        return

    while True:
        try:
            choice = input("Enter the number of the task to delete (or 'c' to cancel): ")
            if choice.lower() == 'c':
                return
            task_index = int(choice) - 1 # User sees 1-based index

            if 0 <= task_index < len(tasks):
                removed_task = tasks.pop(task_index)
                print(f"Task '{removed_task['description']}' deleted.")
                save_tasks(tasks)
                break # Exit the loop after valid input
            else:
                print("Invalid task number.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        except IndexError:
             print("Invalid task number (Index out of range).")


def display_menu():
    """Displays the main menu options."""
    print("\n--- To-Do App Menu ---")
    print("1. View Tasks")
    print("2. Add Task")
    print("3. Mark Task as Complete")
    print("4. Delete Task")
    print("5. Exit")
    print("----------------------")

# --- Main Program ---
if __name__ == "__main__":
    tasks = load_tasks()

    while True:
        display_menu()
        choice = input("Enter your choice (1-5): ")

        if choice == '1':
            display_tasks(tasks)
        elif choice == '2':
            add_task(tasks)
        elif choice == '3':
            mark_complete(tasks)
        elif choice == '4':
            delete_task(tasks)
        elif choice == '5':
            print("Exiting To-Do App. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")