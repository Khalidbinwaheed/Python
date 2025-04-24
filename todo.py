import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, Listbox, Scrollbar, Frame, Label, Entry, Button, font as tkFont, Toplevel
import json
import os

# --- Data Persistence Logic ---
TASKS_FILE = "tasks_amazing_ttk.json"

def load_tasks():
    """Loads tasks from the JSON file."""
    if not os.path.exists(TASKS_FILE):
        return []
    try:
        with open(TASKS_FILE, 'r') as f:
            tasks = json.load(f)
            if not isinstance(tasks, list):
                messagebox.showwarning("Load Warning", "Task file format incorrect. Starting fresh.")
                return []
            # Validate and add default fields for older data if necessary
            valid_tasks = []
            for task in tasks:
                if isinstance(task, dict):
                    # Ensure 'description' and 'completed' exist
                    if 'description' not in task or 'completed' not in task:
                         print(f"Warning: Skipping invalid task data: {task}") # Log invalid structure
                         continue

                    # Ensure 'priority' exists, add default if not
                    if 'priority' not in task or task['priority'] not in ["High", "Medium", "Low", "None"]:
                        task['priority'] = "None" # Default priority

                    valid_tasks.append(task)
                else:
                    print(f"Warning: Skipping non-dict task data: {task}")
            return valid_tasks
    except json.JSONDecodeError:
        messagebox.showwarning("Load Warning", f"Could not decode JSON from {TASKS_FILE}. Starting fresh.")
        return []
    except Exception as e:
        messagebox.showerror("Load Error", f"An error occurred loading tasks:\n{e}\nStarting fresh.")
        return []

def save_tasks(tasks):
    """Saves the current list of tasks to the JSON file."""
    try:
        with open(TASKS_FILE, 'w') as f:
            json.dump(tasks, f, indent=4)
    except Exception as e:
        messagebox.showerror("Save Error", f"Could not save tasks:\n{e}")

# --- Constants for UI Colors and Styles ---
COLOR_BG_MAIN = "#f0f0f0" # Light gray background
COLOR_BG_FRAME = "#ffffff" # White background for inner frames
COLOR_TEXT_DEFAULT = "black"
COLOR_TEXT_COMPLETED = "gray"
COLOR_TEXT_HIGH_PRIORITY = "#e53935" # Red-ish
COLOR_TEXT_MEDIUM_PRIORITY = "#ffb300" # Orange-ish
COLOR_TEXT_LOW_PRIORITY = "#43a047"  # Green-ish

FONT_FAMILY = "Segoe UI" # Or "Arial", "Helvetica"
FONT_SIZE_NORMAL = 10
FONT_SIZE_STATUS = 9
FONT_SIZE_TITLE = 12 # Slightly larger for title

PRIORITY_OPTIONS = ["None", "Low", "Medium", "High"] # Order them for clarity

# --- GUI Application Class ---
class TodoApp:
    def __init__(self, root_window):
        self.root = root_window
        self.root.title("Amazing To-Do App")
        self.root.geometry("500x500") # Set initial size
        self.root.minsize(400, 400) # Set minimum size

        # Configure the main window grid
        self.root.columnconfigure(0, weight=1) # Main column expands
        self.root.rowconfigure(2, weight=1)    # Listbox row expands

        # --- Style Configuration ---
        self.style = ttk.Style()
        # self.style.theme_use('clam') # Experiment with themes

        # Custom styles (optional, can be tricky with themes)
        # self.style.configure('TFrame', background=COLOR_BG_FRAME)
        # self.style.configure('TButton', padding=5, font=(FONT_FAMILY, FONT_SIZE_NORMAL))
        # self.style.configure('TEntry', padding=5, font=(FONT_FAMILY, FONT_SIZE_NORMAL))
        # self.style.configure('TCombobox', padding=5, font=(FONT_FAMILY, FONT_SIZE_NORMAL))


        # Define fonts
        self.default_font = tkFont.Font(family=FONT_FAMILY, size=FONT_SIZE_NORMAL)
        self.strikethrough_font = tkFont.Font(family=FONT_FAMILY, size=FONT_SIZE_NORMAL, overstrike=True)
        self.status_font = tkFont.Font(family=FONT_FAMILY, size=FONT_SIZE_STATUS)
        self.title_font = tkFont.Font(family=FONT_FAMILY, size=FONT_SIZE_TITLE, weight="bold")


        # --- Data ---
        self.tasks = load_tasks()

        # --- UI Elements ---

        # Title Label
        self.title_label = ttk.Label(self.root, text="Your Task List", font=self.title_font)
        self.title_label.grid(row=0, column=0, pady=(10, 5), sticky="ew", padx=10)
        self.title_label.config(anchor="center") # Center the text

        # --- Input Frame ---
        self.input_frame = ttk.Frame(self.root, padding="10 5 10 5", relief=tk.RIDGE) # Add ridge border
        self.input_frame.grid(row=1, column=0, sticky="ew", padx=10)
        self.input_frame.columnconfigure(0, weight=1) # Task entry expands

        self.task_entry = ttk.Entry(self.input_frame, width=30, font=self.default_font)
        self.task_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5), pady=5)
        self.task_entry.bind("<Return>", self.add_task_event)

        self.priority_combobox = ttk.Combobox(
            self.input_frame,
            values=PRIORITY_OPTIONS,
            state="readonly", # Prevent typing custom values
            width=10,
            font=self.default_font
        )
        self.priority_combobox.grid(row=0, column=1, padx=(0, 5), pady=5)
        self.priority_combobox.set(PRIORITY_OPTIONS[0]) # Set default value

        self.add_button = ttk.Button(self.input_frame, text="Add Task", command=self.add_task)
        self.add_button.grid(row=0, column=2, pady=5)

        # Separator below input
        self.sep1 = ttk.Separator(self.root, orient='horizontal')
        self.sep1.grid(row=2, column=0, sticky="ew", padx=10, pady=5)


        # --- List Frame ---
        self.list_frame = ttk.Frame(self.root, padding="0 0 0 5") # Pad bottom within main grid
        self.list_frame.grid(row=3, column=0, sticky="nsew", padx=10)
        self.list_frame.columnconfigure(0, weight=1) # Listbox column expands
        self.list_frame.rowconfigure(0, weight=1)    # Listbox row expands


        # Use standard tk Listbox as ttk doesn't have itemconfig for color/font easily
        self.task_listbox = Listbox(
            self.list_frame,
            font=self.default_font,
            selectbackground="#0078D7", # More modern selection color
            selectforeground="white",
            borderwidth=0,
            highlightthickness=0,
            relief=tk.FLAT # Use flat relief
        )
        self.task_listbox.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.task_listbox.bind("<Double-Button-1>", self.toggle_complete_event) # Double click to toggle

        self.scrollbar = ttk.Scrollbar(
            self.list_frame,
            orient=tk.VERTICAL,
            command=self.task_listbox.yview
        )
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.task_listbox.config(yscrollcommand=self.scrollbar.set)


        # Separator below listbox
        self.sep2 = ttk.Separator(self.root, orient='horizontal')
        self.sep2.grid(row=4, column=0, sticky="ew", padx=10, pady=5)

        # --- Action Frame ---
        self.action_frame = ttk.Frame(self.root, padding="10 5 10 5")
        self.action_frame.grid(row=5, column=0, sticky="ew", padx=10)
        # Center buttons
        self.action_frame.columnconfigure(0, weight=1) # Spacer
        self.action_frame.columnconfigure(1, weight=0) # Button column
        self.action_frame.columnconfigure(2, weight=0) # Button column
        self.action_frame.columnconfigure(3, weight=0) # Button column
        self.action_frame.columnconfigure(4, weight=1) # Spacer


        self.toggle_button = ttk.Button(self.action_frame, text="Toggle Complete", command=self.toggle_complete)
        self.toggle_button.grid(row=0, column=1, padx=5)

        self.edit_button = ttk.Button(self.action_frame, text="Edit Task", command=self.edit_task)
        self.edit_button.grid(row=0, column=2, padx=5)

        self.delete_button = ttk.Button(self.action_frame, text="Delete Task", command=self.delete_task)
        self.delete_button.grid(row=0, column=3, padx=5)

        # Status Bar
        self.status_bar = Label(self.root, text="Loading tasks...", bd=1, relief=tk.SUNKEN, anchor=tk.W, font=self.status_font)
        self.status_bar.grid(row=6, column=0, sticky="ew")


        # --- Initial Population ---
        self.populate_listbox()
        self.update_status(f"Ready. {len(self.tasks)} tasks loaded.")
        if not self.tasks:
             self.update_status("No tasks yet. Add one!")

        # --- Save on Close ---
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Set focus to entry field on start
        self.task_entry.focus_set()

    # --- Helper Methods ---
    def get_selected_task_index(self):
        """Gets the index of the selected item in the listbox. Returns None if none selected."""
        selected_indices = self.task_listbox.curselection()
        if not selected_indices:
            return None
        return selected_indices[0]

    def update_status(self, message):
        """Updates the text in the status bar."""
        self.status_bar.config(text=message)

    def update_button_states(self):
        """Enable/disable action buttons based on selection"""
        if self.get_selected_task_index() is None:
             self.toggle_button.config(state=tk.DISABLED)
             self.edit_button.config(state=tk.DISABLED)
             self.delete_button.config(state=tk.DISABLED)
        else:
            self.toggle_button.config(state=tk.NORMAL)
            self.edit_button.config(state=tk.NORMAL)
            self.delete_button.config(state=tk.NORMAL)


    # --- Core Functionality Methods ---
    def populate_listbox(self):
        """Clears and refills the listbox based on the self.tasks list."""
        current_selection_index = self.get_selected_task_index() # Preserve selection

        self.task_listbox.delete(0, tk.END) # Clear existing items
        for index, task in enumerate(self.tasks):
            priority_text = f"({task.get('priority', 'None')})" if task.get('priority', 'None') != 'None' else ""
            status_text = "[X]" if task['completed'] else "[ ]"
            display_text = f"{status_text} {priority_text} {task['description']}".strip() # Strip extra spaces

            self.task_listbox.insert(tk.END, display_text)

            # Apply styling
            if task['completed']:
                # Completed tasks are gray and struck through, regardless of original priority
                self.task_listbox.itemconfig(index, {'fg': COLOR_TEXT_COMPLETED})
                self.task_listbox.itemconfig(index, {'font': self.strikethrough_font})
            else:
                 # Not completed - apply priority color and default font
                 color = COLOR_TEXT_DEFAULT
                 if task.get('priority') == "High":
                     color = COLOR_TEXT_HIGH_PRIORITY
                 elif task.get('priority') == "Medium":
                     color = COLOR_TEXT_MEDIUM_PRIORITY
                 elif task.get('priority') == "Low":
                      color = COLOR_TEXT_LOW_PRIORITY

                 self.task_listbox.itemconfig(index, {'fg': color})
                 self.task_listbox.itemconfig(index, {'font': self.default_font})


        # Re-select the previously selected item if it still exists
        if current_selection_index is not None and current_selection_index < self.task_listbox.size():
             self.task_listbox.selection_set(current_selection_index)
             self.task_listbox.activate(current_selection_index)
             self.task_listbox.see(current_selection_index) # Ensure it's visible

        # Update action button states based on selection
        self.update_button_states()


    def add_task(self):
        """Adds a task from the entry field and priority combobox to the list."""
        task_description = self.task_entry.get().strip()
        task_priority = self.priority_combobox.get()

        if task_description:
            new_task = {
                "description": task_description,
                "completed": False,
                "priority": task_priority
            }
            self.tasks.append(new_task)
            self.populate_listbox()
            # Select and scroll to the newly added task
            new_index = len(self.tasks) - 1
            self.task_listbox.selection_clear(0, tk.END) # Clear previous selection
            self.task_listbox.selection_set(new_index)
            self.task_listbox.activate(new_index)
            self.task_listbox.see(new_index)

            self.task_entry.delete(0, tk.END) # Clear entry
            self.priority_combobox.set(PRIORITY_OPTIONS[0]) # Reset priority combo
            self.update_status(f"Task '{task_description}' ({task_priority}) added.")
        else:
            messagebox.showwarning("Input Error", "Task description cannot be empty.")
            self.update_status("Add task failed: Description empty.")
        self.task_entry.focus_set() # Keep focus on entry


    def add_task_event(self, event):
        """Callback for pressing Enter in the entry field."""
        self.add_task()

    def toggle_complete(self):
        """Toggles the completion status of the selected task."""
        task_index = self.get_selected_task_index()
        if task_index is None:
            messagebox.showwarning("Selection Error", "Please select a task to toggle.")
            self.update_status("Toggle failed: No task selected.")
            return

        if 0 <= task_index < len(self.tasks):
            task = self.tasks[task_index]
            task['completed'] = not task['completed'] # Toggle status
            status_text = "completed" if task['completed'] else "marked incomplete"
            self.populate_listbox() # Update the display (will preserve selection)
            self.update_status(f"Task {task_index + 1} {status_text}.")
        else:
             messagebox.showerror("Error", "Invalid task index selected.") # Should not happen
             self.update_status("Toggle failed: Invalid index.")


    def toggle_complete_event(self, event):
        """Callback for double-clicking a task."""
        # Ensure double click was on an actual item
        if self.task_listbox.curselection():
             self.toggle_complete()

    def edit_task(self):
        """Opens a dialog to edit the description of the selected task."""
        task_index = self.get_selected_task_index()
        if task_index is None:
            messagebox.showwarning("Selection Error", "Please select a task to edit.")
            self.update_status("Edit failed: No task selected.")
            return

        current_task = self.tasks[task_index]

        # Use a simpledialog for now, a custom Toplevel window would be better for editing priority too
        # simpledialog is part of tkinter.simpledialog, already imported implicitly by messagebox
        # It's not ideal for editing *both* description and priority easily
        # Let's create a custom simple Toplevel for description editing only for now.
        # If more fields needed editing, a more complex custom dialog would be required.

        # Using simpledialog.askstring is the easiest way for just the description
        from tkinter.simpledialog import askstring
        new_description = askstring(
            "Edit Task",
            "Edit Task Description:",
            initialvalue=current_task['description']
        )

        # askstring returns None if Cancel is pressed, or the new string
        if new_description is not None:
            new_description = new_description.strip()
            if new_description:
                # Check if description actually changed to avoid unnecessary update/save
                if new_description != current_task['description']:
                    self.tasks[task_index]['description'] = new_description
                    self.populate_listbox()
                    self.update_status(f"Task {task_index + 1} description updated.")
                else:
                    self.update_status("Edit cancelled (no change).")
            else:
                messagebox.showwarning("Input Error", "Task description cannot be empty.")
                self.update_status("Edit failed: Description empty.")
        else:
            self.update_status("Edit cancelled.")


    def delete_task(self):
        """Deletes the selected task after confirmation."""
        task_index = self.get_selected_task_index()
        if task_index is None:
            messagebox.showwarning("Selection Error", "Please select a task to delete.")
            self.update_status("Delete failed: No task selected.")
            return

        task_description = self.tasks[task_index]['description']
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to permanently delete this task?\n\n'{task_description}'"
        )

        if confirm:
            if 0 <= task_index < len(self.tasks):
                del self.tasks[task_index]
                self.populate_listbox() # Update the display
                # Selection is automatically cleared when the deleted item's index is removed
                self.update_status(f"Task '{task_description}' deleted.")
            else:
                 messagebox.showerror("Error", "Invalid task index selected during deletion.") # Should not happen
                 self.update_status("Delete failed: Invalid index.")
        else:
            self.update_status("Deletion cancelled.")

    def on_closing(self):
        """Handles window closing event, saves tasks."""
        self.update_status("Saving tasks...")
        save_tasks(self.tasks)
        print("Tasks saved. Exiting.")
        self.root.destroy()


# --- Main Execution ---
if __name__ == "__main__":
    main_window = tk.Tk()
    app = TodoApp(main_window)
    main_window.mainloop()