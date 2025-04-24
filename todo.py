import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, Listbox, Scrollbar, Frame, Label, Entry, Button, font as tkFont, Toplevel
import json
import os
from datetime import datetime

# --- Data Persistence Logic ---
TASKS_FILE = "tasks_amazing_ttk.json"

def load_tasks():
    """Loads tasks from the JSON file with validation and data migration."""
    if not os.path.exists(TASKS_FILE):
        return []
    try:
        with open(TASKS_FILE, 'r') as f:
            tasks = json.load(f)
            if not isinstance(tasks, list):
                messagebox.showwarning("Load Warning", "Task file format incorrect. Starting fresh.")
                return []
            
            valid_tasks = []
            for task in tasks:
                if isinstance(task, dict):
                    # Ensure required fields exist
                    if 'description' not in task or 'completed' not in task:
                        continue
                    
                    # Set defaults for missing optional fields
                    if 'priority' not in task or task['priority'] not in ["High", "Medium", "Low", "None"]:
                        task['priority'] = "None"
                    
                    # Add creation date if missing (for older tasks)
                    if 'created' not in task:
                        task['created'] = datetime.now().isoformat()
                        
                    # Add due date field if missing
                    if 'due_date' not in task:
                        task['due_date'] = None
                        
                    # Add category field if missing
                    if 'category' not in task:
                        task['category'] = "Uncategorized"
                        
                    valid_tasks.append(task)
            return valid_tasks
    except Exception as e:
        messagebox.showerror("Load Error", f"Error loading tasks:\n{e}\nStarting fresh.")
        return []

def save_tasks(tasks):
    """Saves the current list of tasks to the JSON file."""
    try:
        with open(TASKS_FILE, 'w') as f:
            json.dump(tasks, f, indent=4)
    except Exception as e:
        messagebox.showerror("Save Error", f"Could not save tasks:\n{e}")

# --- Constants for UI Colors and Styles ---
COLOR_BG_MAIN = "#f0f0f0"
COLOR_BG_FRAME = "#ffffff"
COLOR_TEXT_DEFAULT = "black"
COLOR_TEXT_COMPLETED = "gray"
COLOR_TEXT_HIGH_PRIORITY = "#e53935"
COLOR_TEXT_MEDIUM_PRIORITY = "#ffb300"
COLOR_TEXT_LOW_PRIORITY = "#43a047"
COLOR_TEXT_OVERDUE = "#d81b60"
COLOR_TEXT_DUE_SOON = "#8e24aa"

FONT_FAMILY = "Segoe UI"
FONT_SIZE_NORMAL = 10
FONT_SIZE_SMALL = 9
FONT_SIZE_LARGE = 12
FONT_SIZE_TITLE = 14

PRIORITY_OPTIONS = ["None", "Low", "Medium", "High"]
CATEGORY_OPTIONS = ["Uncategorized", "Work", "Personal", "Shopping", "Health", "Finance", "Other"]

# --- GUI Application Class ---
class TodoApp:
    def __init__(self, root_window):
        self.root = root_window
        self.root.title("Amazing To-Do App")
        self.root.geometry("700x600")
        self.root.minsize(600, 500)
        
        # Configure the main window grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)
        
        # --- Style Configuration ---
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Define fonts
        self.default_font = tkFont.Font(family=FONT_FAMILY, size=FONT_SIZE_NORMAL)
        self.small_font = tkFont.Font(family=FONT_FAMILY, size=FONT_SIZE_SMALL)
        self.large_font = tkFont.Font(family=FONT_FAMILY, size=FONT_SIZE_LARGE)
        self.title_font = tkFont.Font(family=FONT_FAMILY, size=FONT_SIZE_TITLE, weight="bold")
        self.strikethrough_font = tkFont.Font(family=FONT_FAMILY, size=FONT_SIZE_NORMAL, overstrike=True)
        
        # --- Data ---
        self.tasks = load_tasks()
        self.current_filter = "All"  # Can be "All", "Active", "Completed", or category name
        self.sort_method = "Priority"  # Can be "Priority", "Due Date", "Creation Date", "Alphabetical"
        
        # --- UI Elements ---
        self.create_widgets()
        self.setup_menu()
        
        # --- Initial Population ---
        self.populate_listbox()
        self.update_status(f"Ready. {len(self.tasks)} tasks loaded.")
        if not self.tasks:
            self.update_status("No tasks yet. Add one!")
        
        # Set focus to entry field on start
        self.task_entry.focus_set()
        
        # Configure window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        """Creates all the widgets for the application."""
        # Title Label
        self.title_label = ttk.Label(self.root, text="Your Task List", font=self.title_font)
        self.title_label.grid(row=0, column=0, pady=(10, 5), sticky="ew", padx=10)
        
        # --- Filter/Sort Controls ---
        self.control_frame = ttk.Frame(self.root, padding="5 5 5 5")
        self.control_frame.grid(row=1, column=0, sticky="ew", padx=10)
        
        # Filter label and combobox
        ttk.Label(self.control_frame, text="Filter:", font=self.default_font).grid(row=0, column=0, padx=(0, 5))
        self.filter_combobox = ttk.Combobox(
            self.control_frame,
            values=["All", "Active", "Completed"] + CATEGORY_OPTIONS,
            state="readonly",
            width=15,
            font=self.default_font
        )
        self.filter_combobox.grid(row=0, column=1, padx=(0, 10))
        self.filter_combobox.set("All")
        self.filter_combobox.bind("<<ComboboxSelected>>", self.apply_filter)
        
        # Sort label and combobox
        ttk.Label(self.control_frame, text="Sort by:", font=self.default_font).grid(row=0, column=2, padx=(0, 5))
        self.sort_combobox = tttk.Combobox(
            self.control_frame,
            values=["Priority", "Due Date", "Creation Date", "Alphabetical"],
            state="readonly",
            width=15,
            font=self.default_font
        )
        self.sort_combobox.grid(row=0, column=3)
        self.sort_combobox.set("Priority")
        self.sort_combobox.bind("<<ComboboxSelected>>", self.apply_sort)
        
        # --- Input Frame ---
        self.input_frame = ttk.Frame(self.root, padding="10 5 10 5")
        self.input_frame.grid(row=2, column=0, sticky="ew", padx=10)
        self.input_frame.columnconfigure(0, weight=1)
        
        # Task entry
        self.task_entry = ttk.Entry(self.input_frame, font=self.default_font)
        self.task_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5), pady=5)
        self.task_entry.bind("<Return>", self.add_task_event)
        
        # Priority combobox
        self.priority_combobox = ttk.Combobox(
            self.input_frame,
            values=PRIORITY_OPTIONS,
            state="readonly",
            width=8,
            font=self.default_font
        )
        self.priority_combobox.grid(row=0, column=1, padx=(0, 5), pady=5)
        self.priority_combobox.set(PRIORITY_OPTIONS[0])
        
        # Category combobox
        self.category_combobox = ttk.Combobox(
            self.input_frame,
            values=CATEGORY_OPTIONS,
            state="readonly",
            width=12,
            font=self.default_font
        )
        self.category_combobox.grid(row=0, column=2, padx=(0, 5), pady=5)
        self.category_combobox.set(CATEGORY_OPTIONS[0])
        
        # Due date button
        self.due_date_button = ttk.Button(
            self.input_frame,
            text="Set Due Date",
            width=10,
            command=self.set_due_date
        )
        self.due_date_button.grid(row=0, column=3, padx=(0, 5), pady=5)
        
        # Add button
        self.add_button = ttk.Button(
            self.input_frame,
            text="Add Task",
            width=8,
            command=self.add_task
        )
        self.add_button.grid(row=0, column=4, pady=5)
        
        # --- List Frame ---
        self.list_frame = ttk.Frame(self.root)
        self.list_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=(0, 5))
        self.list_frame.columnconfigure(0, weight=1)
        self.list_frame.rowconfigure(0, weight=1)
        
        # Task listbox with scrollbar
        self.task_listbox = Listbox(
            self.list_frame,
            font=self.default_font,
            selectbackground="#0078D7",
            selectforeground="white",
            borderwidth=0,
            highlightthickness=0,
            relief=tk.FLAT
        )
        self.task_listbox.grid(row=0, column=0, sticky="nsew")
        self.task_listbox.bind("<Double-Button-1>", self.toggle_complete_event)
        self.task_listbox.bind("<<ListboxSelect>>", self.on_task_select)
        
        self.scrollbar = ttk.Scrollbar(
            self.list_frame,
            orient=tk.VERTICAL,
            command=self.task_listbox.yview
        )
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.task_listbox.config(yscrollcommand=self.scrollbar.set)
        
        # --- Action Frame ---
        self.action_frame = ttk.Frame(self.root, padding="10 5 10 5")
        self.action_frame.grid(row=4, column=0, sticky="ew", padx=10)
        
        # Action buttons
        buttons = [
            ("Toggle Complete", self.toggle_complete),
            ("Edit Task", self.edit_task),
            ("Delete Task", self.delete_task),
            ("Clear Completed", self.clear_completed),
            ("Export Tasks", self.export_tasks)
        ]
        
        for i, (text, command) in enumerate(buttons):
            ttk.Button(
                self.action_frame,
                text=text,
                command=command
            ).grid(row=0, column=i, padx=5)
        
        # Status Bar
        self.status_bar = Label(
            self.root,
            text="Ready",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=self.small_font
        )
        self.status_bar.grid(row=5, column=0, sticky="ew")
    
    def setup_menu(self):
        """Sets up the menu bar."""
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Export Tasks", command=self.export_tasks)
        file_menu.add_command(label="Import Tasks", command=self.import_tasks)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Task menu
        task_menu = tk.Menu(menubar, tearoff=0)
        task_menu.add_command(label="Add Task", command=self.add_task)
        task_menu.add_command(label="Edit Task", command=self.edit_task)
        task_menu.add_command(label="Delete Task", command=self.delete_task)
        task_menu.add_separator()
        task_menu.add_command(label="Clear Completed", command=self.clear_completed)
        menubar.add_cascade(label="Task", menu=task_menu)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Show All", command=lambda: self.set_filter("All"))
        view_menu.add_command(label="Show Active", command=lambda: self.set_filter("Active"))
        view_menu.add_command(label="Show Completed", command=lambda: self.set_filter("Completed"))
        view_menu.add_separator()
        
        # Add category filters
        for category in CATEGORY_OPTIONS:
            view_menu.add_command(
                label=f"Show {category}",
                command=lambda c=category: self.set_filter(c)
            )
        
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    # --- Helper Methods ---
    def get_selected_task_index(self):
        """Gets the index of the selected item in the listbox."""
        selected = self.task_listbox.curselection()
        return selected[0] if selected else None
    
    def update_status(self, message):
        """Updates the status bar text."""
        self.status_bar.config(text=message)
    
    def update_button_states(self):
        """Enable/disable action buttons based on selection."""
        has_selection = self.get_selected_task_index() is not None
        
        for button in [self.toggle_button, self.edit_button, self.delete_button]:
            button.config(state=tk.NORMAL if has_selection else tk.DISABLED)
    
    def format_due_date(self, due_date_str):
        """Formats the due date for display."""
        if not due_date_str:
            return ""
        
        try:
            due_date = datetime.fromisoformat(due_date_str)
            return due_date.strftime("%Y-%m-%d")
        except ValueError:
            return ""
    
    def is_overdue(self, due_date_str):
        """Checks if a task is overdue."""
        if not due_date_str:
            return False
        
        try:
            due_date = datetime.fromisoformat(due_date_str).date()
            return due_date < datetime.now().date()
        except ValueError:
            return False
    
    def is_due_soon(self, due_date_str, days=3):
        """Checks if a task is due soon."""
        if not due_date_str:
            return False
        
        try:
            due_date = datetime.fromisoformat(due_date_str).date()
            today = datetime.now().date()
            return today <= due_date <= (today + timedelta(days=days))
        except ValueError:
            return False
    
    # --- Core Functionality Methods ---
    def populate_listbox(self):
        """Populates the listbox with tasks based on current filter and sort."""
        self.task_listbox.delete(0, tk.END)
        
        # Filter tasks
        if self.current_filter == "All":
            filtered_tasks = self.tasks
        elif self.current_filter == "Active":
            filtered_tasks = [t for t in self.tasks if not t['completed']]
        elif self.current_filter == "Completed":
            filtered_tasks = [t for t in self.tasks if t['completed']]
        else:  # Category filter
            filtered_tasks = [t for t in self.tasks if t['category'] == self.current_filter]
        
        # Sort tasks
        if self.sort_method == "Priority":
            priority_order = {"High": 0, "Medium": 1, "Low": 2, "None": 3}
            filtered_tasks.sort(key=lambda x: (
                priority_order[x['priority']],
                x['due_date'] or "",  # Sort None at the end
                x['description'].lower()
            ))
        elif self.sort_method == "Due Date":
            filtered_tasks.sort(key=lambda x: (
                x['due_date'] or "9999-12-31",  # Sort tasks without due date last
                x['priority'],
                x['description'].lower()
            ))
        elif self.sort_method == "Creation Date":
            filtered_tasks.sort(key=lambda x: (
                x['created'],
                x['priority'],
                x['description'].lower()
            ))
        else:  # Alphabetical
            filtered_tasks.sort(key=lambda x: x['description'].lower())
        
        # Add tasks to listbox with appropriate formatting
        for task in filtered_tasks:
            status = "[✓]" if task['completed'] else "[ ]"
            priority = f"({task['priority']})" if task['priority'] != "None" else ""
            category = f"#{task['category']}" if task['category'] != "Uncategorized" else ""
            due_date = f"⏰{self.format_due_date(task['due_date'])}" if task['due_date'] else ""
            
            display_text = f"{status} {priority} {category} {task['description']} {due_date}".strip()
            self.task_listbox.insert(tk.END, display_text)
            
            # Apply styling
            index = self.task_listbox.size() - 1
            if task['completed']:
                self.task_listbox.itemconfig(index, {'fg': COLOR_TEXT_COMPLETED, 'font': self.strikethrough_font})
            else:
                # Color based on priority and due date
                if self.is_overdue(task['due_date']):
                    color = COLOR_TEXT_OVERDUE
                elif self.is_due_soon(task['due_date']):
                    color = COLOR_TEXT_DUE_SOON
                elif task['priority'] == "High":
                    color = COLOR_TEXT_HIGH_PRIORITY
                elif task['priority'] == "Medium":
                    color = COLOR_TEXT_MEDIUM_PRIORITY
                elif task['priority'] == "Low":
                    color = COLOR_TEXT_LOW_PRIORITY
                else:
                    color = COLOR_TEXT_DEFAULT
                
                self.task_listbox.itemconfig(index, {'fg': color, 'font': self.default_font})
        
        self.update_button_states()
        self.update_status(f"Showing {len(filtered_tasks)} of {len(self.tasks)} tasks")
    
    def add_task(self):
        """Adds a new task to the list."""
        description = self.task_entry.get().strip()
        if not description:
            messagebox.showwarning("Input Error", "Task description cannot be empty.")
            return
        
        new_task = {
            "description": description,
            "completed": False,
            "priority": self.priority_combobox.get(),
            "category": self.category_combobox.get(),
            "due_date": self.current_due_date if hasattr(self, 'current_due_date') else None,
            "created": datetime.now().isoformat()
        }
        
        self.tasks.append(new_task)
        self.task_entry.delete(0, tk.END)
        self.priority_combobox.set(PRIORITY_OPTIONS[0])
        self.category_combobox.set(CATEGORY_OPTIONS[0])
        
        if hasattr(self, 'current_due_date'):
            del self.current_due_date
        
        self.populate_listbox()
        self.update_status(f"Added: {description}")
    
    def add_task_event(self, event):
        """Handles Enter key press in task entry."""
        self.add_task()
    
    def set_due_date(self):
        """Opens a dialog to set due date for new task."""
        from tkinter import simpledialog
        date_str = simpledialog.askstring(
            "Set Due Date",
            "Enter due date (YYYY-MM-DD):",
            parent=self.root
        )
        
        if date_str:
            try:
                # Validate date format
                datetime.strptime(date_str, "%Y-%m-%d")
                self.current_due_date = date_str
                self.update_status(f"Due date set to: {date_str}")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD.")
    
    def toggle_complete(self):
        """Toggles completion status of selected task."""
        index = self.get_selected_task_index()
        if index is None:
            return
        
        # Get the actual task from the filtered list
        filtered_indices = self.get_filtered_indices()
        if index >= len(filtered_indices):
            return
        
        task_index = filtered_indices[index]
        self.tasks[task_index]['completed'] = not self.tasks[task_index]['completed']
        self.populate_listbox()
    
    def toggle_complete_event(self, event):
        """Handles double-click to toggle completion."""
        if self.task_listbox.curselection():
            self.toggle_complete()
    
    def edit_task(self):
        """Opens a dialog to edit the selected task."""
        index = self.get_selected_task_index()
        if index is None:
            return
        
        # Get the actual task from the filtered list
        filtered_indices = self.get_filtered_indices()
        if index >= len(filtered_indices):
            return
        
        task_index = filtered_indices[index]
        task = self.tasks[task_index]
        
        # Create edit dialog
        edit_dialog = Toplevel(self.root)
        edit_dialog.title("Edit Task")
        edit_dialog.transient(self.root)
        edit_dialog.grab_set()
        
        # Description
        ttk.Label(edit_dialog, text="Description:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        desc_entry = ttk.Entry(edit_dialog, width=40, font=self.default_font)
        desc_entry.grid(row=0, column=1, columnspan=3, padx=5, pady=5, sticky="ew")
        desc_entry.insert(0, task['description'])
        
        # Priority
        ttk.Label(edit_dialog, text="Priority:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        priority_combo = ttk.Combobox(
            edit_dialog,
            values=PRIORITY_OPTIONS,
            state="readonly",
            width=10,
            font=self.default_font
        )
        priority_combo.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        priority_combo.set(task['priority'])
        
        # Category
        ttk.Label(edit_dialog, text="Category:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        category_combo = ttk.Combobox(
            edit_dialog,
            values=CATEGORY_OPTIONS,
            state="readonly",
            width=12,
            font=self.default_font
        )
        category_combo.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        category_combo.set(task['category'])
        
        # Due Date
        ttk.Label(edit_dialog, text="Due Date:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        due_date_entry = ttk.Entry(edit_dialog, width=15, font=self.default_font)
        due_date_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        due_date_entry.insert(0, self.format_due_date(task['due_date']))
        
        def save_changes():
            """Saves the edited task details."""
            new_desc = desc_entry.get().strip()
            if not new_desc:
                messagebox.showwarning("Error", "Description cannot be empty.")
                return
            
            # Validate due date
            new_due_date = due_date_entry.get().strip()
            if new_due_date:
                try:
                    datetime.strptime(new_due_date, "%Y-%m-%d")
                    new_due_date = new_due_date
                except ValueError:
                    messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.")
                    return
            else:
                new_due_date = None
            
            # Update task
            task['description'] = new_desc
            task['priority'] = priority_combo.get()
            task['category'] = category_combo.get()
            task['due_date'] = new_due_date
            
            self.populate_listbox()
            edit_dialog.destroy()
            self.update_status("Task updated successfully.")
        
        # Buttons
        ttk.Button(edit_dialog, text="Save", command=save_changes).grid(row=3, column=2, padx=5, pady=10)
        ttk.Button(edit_dialog, text="Cancel", command=edit_dialog.destroy).grid(row=3, column=3, padx=5, pady=10)
    
    def delete_task(self):
        """Deletes the selected task after confirmation."""
        index = self.get_selected_task_index()
        if index is None:
            return
        
        # Get the actual task from the filtered list
        filtered_indices = self.get_filtered_indices()
        if index >= len(filtered_indices):
            return
        
        task_index = filtered_indices[index]
        task = self.tasks[task_index]
        
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Delete this task?\n\n{task['description']}",
            parent=self.root
        )
        
        if confirm:
            del self.tasks[task_index]
            self.populate_listbox()
            self.update_status("Task deleted.")
    
    def clear_completed(self):
        """Removes all completed tasks after confirmation."""
        if not any(task['completed'] for task in self.tasks):
            messagebox.showinfo("Info", "No completed tasks to clear.", parent=self.root)
            return
        
        confirm = messagebox.askyesno(
            "Confirm Clear",
            "Delete all completed tasks?",
            parent=self.root
        )
        
        if confirm:
            self.tasks = [task for task in self.tasks if not task['completed']]
            self.populate_listbox()
            self.update_status("Cleared all completed tasks.")
    
    def export_tasks(self):
        """Exports tasks to a JSON file."""
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Export tasks to file"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(self.tasks, f, indent=4)
                self.update_status(f"Tasks exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export tasks:\n{e}")
    
    def import_tasks(self):
        """Imports tasks from a JSON file."""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Import tasks from file"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    imported_tasks = json.load(f)
                
                if not isinstance(imported_tasks, list):
                    messagebox.showerror("Import Error", "File must contain a list of tasks.")
                    return
                
                confirm = messagebox.askyesno(
                    "Confirm Import",
                    f"Import {len(imported_tasks)} tasks? Current tasks will be preserved.",
                    parent=self.root
                )
                
                if confirm:
                    self.tasks.extend(imported_tasks)
                    self.populate_listbox()
                    self.update_status(f"Imported {len(imported_tasks)} tasks from {file_path}")
            except Exception as e:
                messagebox.showerror("Import Error", f"Failed to import tasks:\n{e}")
    
    def set_filter(self, filter_name):
        """Sets the current filter and updates the view."""
        self.current_filter = filter_name
        self.filter_combobox.set(filter_name)
        self.populate_listbox()
    
    def apply_filter(self, event=None):
        """Applies the selected filter."""
        self.current_filter = self.filter_combobox.get()
        self.populate_listbox()
    
    def apply_sort(self, event=None):
        """Applies the selected sort method."""
        self.sort_method = self.sort_combobox.get()
        self.populate_listbox()
    
    def get_filtered_indices(self):
        """Returns the original indices of tasks in the filtered view."""
        if self.current_filter == "All":
            return list(range(len(self.tasks)))
        elif self.current_filter == "Active":
            return [i for i, t in enumerate(self.tasks) if not t['completed']]
        elif self.current_filter == "Completed":
            return [i for i, t in enumerate(self.tasks) if t['completed']]
        else:  # Category filter
            return [i for i, t in enumerate(self.tasks) if t['category'] == self.current_filter]
    
    def on_task_select(self, event):
        """Handles task selection changes."""
        self.update_button_states()
    
    def show_about(self):
        """Displays the about dialog."""
        about_text = (
            "Amazing To-Do App\n"
            "Version 2.0\n\n"
            "A feature-rich task management application\n"
            "with filtering, sorting, and due dates."
        )
        
        messagebox.showinfo("About", about_text, parent=self.root)
    
    def on_closing(self):
        """Handles window closing event."""
        self.update_status("Saving tasks...")
        save_tasks(self.tasks)
        self.root.destroy()

# --- Main Execution ---
if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()