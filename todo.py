import tkinter as tk
from tkinter import messagebox, simpledialog, Listbox, Scrollbar, Entry, Button, Frame
import json
import os

# --- Data Persistence Logic (same as before) ---
TASKS_FILE = "tasks_gui.json" # Use a different file name to avoid conflict with CLI version

def load_tasks():
    """Loads tasks from the JSON file."""
    if not os.path.exists(TASKS_FILE):
        return []
    try:
        with open(TASKS_FILE, 'r') as f:
            tasks = json.load(f)
            if not isinstance(tasks, list):
                print("Warning: Task file format incorrect. Starting fresh.")
                return []
            # Basic validation of task structure
            valid_tasks = []
            for task in tasks:
                if isinstance(task, dict) and 'description' in task and 'completed' in task:
                    valid_tasks.append(task)
                else:
                    print(f"Warning: Skipping invalid task data: {task}")
            return valid_tasks
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
            json.dump(tasks, f, indent=4)
    except Exception as e:
        messagebox.showerror("Save Error", f"Could not save tasks:\n{e}")

# --- GUI Application Class ---
class TodoApp:
    def __init__(self, root_window):
        self.root = root_window
        self.root.title("Simple To-Do App")
        # Make window slightly larger
        self.root.geometry("450x450")

        # --- Data ---
        self.tasks = load_tasks() # Load tasks on initialization

        # --- UI Elements ---
        # Frame for Input and Add Button
        self.input_frame = Frame(self.root)
        self.input_frame.pack(pady=10, fill=tk.X, padx=10) # Pack frame first

        self.task_entry = Entry(self.input_frame, width=35, font=('Arial', 12))
        self.task_entry.pack(side=tk.LEFT, padx=(0, 5), ipady=4) # Pad internal y
        # Bind <Return> key (Enter) to add_task method
        self.task_entry.bind("<Return>", self.add_task_event)

        self.add_button = Button(self.input_frame, text="Add Task", command=self.add_task, relief=tk.RAISED, borderwidth=2)
        self.add_button.pack(side=tk.LEFT, ipady=1)

        # Frame for Listbox and Scrollbar
        self.list_frame = Frame(self.root)
        self.list_frame.pack(pady=10, fill=tk.BOTH, expand=True, padx=10) # Allow frame to expand

        self.scrollbar = Scrollbar(self.list_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.task_listbox = Listbox(
            self.list_frame,
            width=50,
            height=15,
            yscrollcommand=self.scrollbar.set,
            font=('Arial', 11),
            selectbackground="#a6a6a6", # Color when selected
            selectforeground="#ffffff"
        )
        self.task_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.task_listbox.yview)

        # Frame for Action Buttons
        self.action_frame = Frame(self.root)
        self.action_frame.pack(pady=10, fill=tk.X, padx=10)

        self.complete_button = Button(self.action_frame, text="Mark Complete", command=self.mark_complete, relief=tk.RAISED, borderwidth=2)
        self.complete_button.pack(side=tk.LEFT, padx=5, ipady=1)

        self.delete_button = Button(self.action_frame, text="Delete Task", command=self.delete_task, relief=tk.RAISED, borderwidth=2)
        self.delete_button.pack(side=tk.LEFT, padx=5, ipady=1)

        # --- Initial Population ---
        self.populate_listbox()

        # --- Save on Close ---
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)


    def populate_listbox(self):
        """Clears and refills the listbox based on the self.tasks list."""
        self.task_listbox.delete(0, tk.END) # Clear existing items
        for index, task in enumerate(self.tasks):
            status = "[X]" if task['completed'] else "[ ]"
            display_text = f"{status} {task['description']}"
            self.task_listbox.insert(tk.END, display_text)
            # Optionally change color for completed tasks
            if task['completed']:
                self.task_listbox.itemconfig(index, {'fg': 'gray'}) # Change text color
            else:
                 self.task_listbox.itemconfig(index, {'fg': 'black'}) # Ensure it's black if not complete

    def add_task(self):
        """Adds a task from the entry field to the list."""
        task_description = self.task_entry.get().strip()
        if task_description:
            new_task = {"description": task_description, "completed": False}
            self.tasks.append(new_task)
            self.populate_listbox() # Update the display
            self.task_entry.delete(0, tk.END) # Clear the entry field
            # No need to save here, save on close or explicit action
        else:
            messagebox.showwarning("Input Error", "Task description cannot be empty.")

    # Event handler for pressing Enter in the entry box
    def add_task_event(self, event):
        self.add_task()

    def mark_complete(self):
        """Marks the selected task as complete."""
        selected_indices = self.task_listbox.curselection() # Returns a tuple of indices
        if not selected_indices:
            messagebox.showwarning("Selection Error", "Please select a task to mark as complete.")
            return

        task_index = selected_indices[0] # Get the first selected index

        if 0 <= task_index < len(self.tasks):
            self.tasks[task_index]['completed'] = True
            self.populate_listbox() # Update the display
            # Optionally de-select after action
            # self.task_listbox.selection_clear(0, tk.END)
        else:
             messagebox.showerror("Error", "Invalid task index selected (this shouldn't normally happen).")


    def delete_task(self):
        """Deletes the selected task."""
        selected_indices = self.task_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Selection Error", "Please select a task to delete.")
            return

        task_index = selected_indices[0]

        # Confirmation dialog
        task_text = self.tasks[task_index]['description']
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete this task?\n\n'{task_text}'")

        if confirm:
            if 0 <= task_index < len(self.tasks):
                del self.tasks[task_index]
                self.populate_listbox() # Update the display
            else:
                 messagebox.showerror("Error", "Invalid task index selected (this shouldn't normally happen).")


    def on_closing(self):
        """Handles window closing event, saves tasks."""
        print("Saving tasks before closing...")
        save_tasks(self.tasks)
        self.root.destroy() # Close the window


# --- Main Execution ---
if __name__ == "__main__":
    main_window = tk.Tk()
    app = TodoApp(main_window)
    main_window.mainloop() # Start the Tkinter event loop