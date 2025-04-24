import tkinter as tk
from tkinter import ttk  # Import themed widgets
from tkinter import messagebox, Listbox, Scrollbar, Frame, Label, font as tkFont
import json
import os

# --- Data Persistence Logic (same as before) ---
TASKS_FILE = "tasks_ttk.json" # Use a different file name

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
            # Basic validation of task structure
            valid_tasks = []
            for task in tasks:
                if isinstance(task, dict) and 'description' in task and 'completed' in task:
                    valid_tasks.append(task)
                else:
                    print(f"Warning: Skipping invalid task data: {task}") # Log for debugging
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

# --- GUI Application Class ---
class TodoApp:
    def __init__(self, root_window):
        self.root = root_window
        self.root.title("Enhanced To-Do App")
        # Set a minimum size and allow resizing
        self.root.minsize(450, 400)
        # Configure the main window's grid behavior
        self.root.columnconfigure(0, weight=1) # Make column 0 expandable
        self.root.rowconfigure(1, weight=1)    # Make row 1 (listbox frame) expandable

        # --- Style Configuration (Optional but recommended) ---
        self.style = ttk.Style()
        # You can experiment with themes: 'clam', 'alt', 'default', 'classic'
        # Available themes depend on OS and Tk version
        # print(self.style.theme_names()) # See available themes
        try:
            self.style.theme_use('clam') # 'clam' often looks decent
        except tk.TclError:
            print("Clam theme not available, using default.")
        # Configure specific styles if needed
        # self.style.configure('TButton', padding=5, font=('Segoe UI', 10))
        # self.style.configure('TEntry', padding=5, font=('Segoe UI', 10))

        # Define fonts
        self.default_font = tkFont.Font(family="Segoe UI", size=10)
        self.strikethrough_font = tkFont.Font(family="Segoe UI", size=10, overstrike=True)


        # --- Data ---
        self.tasks = load_tasks()

        # --- UI Elements ---

        # Input Frame (using grid)
        self.input_frame = ttk.Frame(self.root, padding="10 10 10 5") # L,T,R,B padding
        self.input_frame.grid(row=0, column=0, sticky="ew") # ew = stretch horizontally
        self.input_frame.columnconfigure(0, weight=1) # Make entry expand

        self.task_entry = ttk.Entry(self.input_frame, width=40, font=self.default_font)
        self.task_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5)) # Pad right
        self.task_entry.bind("<Return>", self.add_task_event)

        self.add_button = ttk.Button(self.input_frame, text="Add Task", command=self.add_task)
        self.add_button.grid(row=0, column=1)


        # List Frame (using grid)
        self.list_frame = ttk.Frame(self.root, padding="10 0 10 5")
        self.list_frame.grid(row=1, column=0, sticky="nsew") # nsew = stretch all directions
        self.list_frame.columnconfigure(0, weight=1) # Listbox column expands
        self.list_frame.rowconfigure(0, weight=1)    # Listbox row expands

        # Use standard tk Listbox as ttk doesn't have one, but style its container/scrollbar
        self.task_listbox = Listbox(
            self.list_frame,
            # width=50, # Width is less important when using grid expansion
            # height=15, # Height less important with grid expansion
            font=self.default_font,
            selectbackground="#0078D7", # A more modern selection color
            selectforeground="white",
            borderwidth=0, # Use frame border if needed
            highlightthickness=0 # Remove focus border if desired
            # activestyle='none' # Removes the dotted box on selection (can reduce clarity)
        )
        self.task_listbox.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.task_listbox.bind("<Double-Button-1>", self.toggle_complete_event) # Double click binding

        self.scrollbar = ttk.Scrollbar(
            self.list_frame,
            orient=tk.VERTICAL,
            command=self.task_listbox.yview
        )
        self.scrollbar.grid(row=0, column=1, sticky="ns") # ns = stretch vertically
        self.task_listbox.config(yscrollcommand=self.scrollbar.set)


        # Action Frame (using grid)
        self.action_frame = ttk.Frame(self.root, padding="10 5 10 10")
        self.action_frame.grid(row=2, column=0, sticky="ew")
        # Center buttons within the action frame
        self.action_frame.columnconfigure(0, weight=1)
        self.action_frame.columnconfigure(1, weight=1)
        self.action_frame.columnconfigure(2, weight=1) # Add spacer columns if needed

        self.toggle_button = ttk.Button(self.action_frame, text="Toggle Complete", command=self.toggle_complete)
        self.toggle_button.grid(row=0, column=0, padx=5, sticky="e") # Align right-ish

        self.delete_button = ttk.Button(self.action_frame, text="Delete Task", command=self.delete_task)
        self.delete_button.grid(row=0, column=1, padx=5, sticky="w") # Align left-ish

        # Status Bar
        self.status_bar = Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W, font=("Segoe UI", 8))
        self.status_bar.grid(row=3, column=0, sticky="ew")


        # --- Initial Population ---
        self.populate_listbox()
        self.update_status(f"{len(self.tasks)} tasks loaded.")
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

    # --- Core Functionality Methods ---
    def populate_listbox(self):
        """Clears and refills the listbox based on the self.tasks list."""
        current_selection = self.get_selected_task_index() # Preserve selection if possible

        self.task_listbox.delete(0, tk.END) # Clear existing items
        for index, task in enumerate(self.tasks):
            status = "[X]" if task['completed'] else "[ ]"
            display_text = f"{status} {task['description']}"
            self.task_listbox.insert(tk.END, display_text)

            # Apply styling for completed tasks
            if task['completed']:
                self.task_listbox.itemconfig(index, {'fg': 'gray'})
                self.task_listbox.itemconfig(index, {'font': self.strikethrough_font})
            else:
                 self.task_listbox.itemconfig(index, {'fg': 'black'})
                 self.task_listbox.itemconfig(index, {'font': self.default_font})

        # Re-select the previously selected item if it still exists
        if current_selection is not None and current_selection < self.task_listbox.size():
             self.task_listbox.selection_set(current_selection)
             self.task_listbox.activate(current_selection) # Ensure it has focus outline
             self.task_listbox.see(current_selection) # Ensure it's visible

        # Update action button states based on selection
        self.update_button_states()


    def add_task(self):
        """Adds a task from the entry field to the list."""
        task_description = self.task_entry.get().strip()
        if task_description:
            # Check for duplicates? Optional UX decision
            # for task in self.tasks:
            #     if task['description'] == task_description and not task['completed']:
            #         messagebox.showinfo("Duplicate", "This task already exists.")
            #         return

            new_task = {"description": task_description, "completed": False}
            self.tasks.append(new_task)
            self.populate_listbox() # Update the display
            self.task_listbox.selection_clear(0, tk.END) # Clear selection
             # Select and scroll to the newly added task
            new_index = tk.END
            self.task_listbox.selection_set(new_index)
            self.task_listbox.activate(new_index)
            self.task_listbox.see(new_index)

            self.task_entry.delete(0, tk.END) # Clear the entry field
            self.update_status(f"Task '{task_description}' added.")
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
             # This case should ideally not happen with get_selected_task_index check
             messagebox.showerror("Error", "Invalid task index selected.")
             self.update_status("Toggle failed: Invalid index.")


    def toggle_complete_event(self, event):
        """Callback for double-clicking a task."""
        # Ensure double click was on an actual item, not empty space
        if self.task_listbox.curselection():
            self.toggle_complete()

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
                # Selection is automatically cleared by populate_listbox in this case
                self.update_status(f"Task '{task_description}' deleted.")
            else:
                 messagebox.showerror("Error", "Invalid task index selected during deletion.")
                 self.update_status("Delete failed: Invalid index.")
        else:
            self.update_status("Deletion cancelled.")

    def update_button_states(self):
        """Enable/disable action buttons based on selection"""
        if self.get_selected_task_index() is None:
             self.toggle_button.config(state=tk.DISABLED)
             self.delete_button.config(state=tk.DISABLED)
        else:
            self.toggle_button.config(state=tk.NORMAL)
            self.delete_button.config(state=tk.NORMAL)


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