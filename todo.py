import tkinter as tk
from tkinter import ttk, messagebox, Listbox, Scrollbar, Frame, Label, font as tkFont, Menu, Radiobutton, StringVar, Toplevel, OptionMenu, Button as tkButton # Need standard button for dialog
import json
import os

# --- Color Themes ---
LIGHT_THEME = {
    "bg": "#F0F0F0",
    "fg": "#000000",
    "entry_bg": "#FFFFFF",
    "entry_fg": "#000000",
    "button_bg": "#E0E0E0", # Less relevant for ttk buttons, but good for tk
    "button_fg": "#000000",
    "list_bg": "#FFFFFF",
    "list_fg": "#000000",
    "list_select_bg": "#0078D7",
    "list_select_fg": "#FFFFFF",
    "completed_fg": "#888888",
    "prio_low_bg": "#DFF0D8",    # Light green background
    "prio_medium_bg": "#FCF8E3", # Light yellow background
    "prio_high_bg": "#F2DEDE",   # Light red background
    "status_bg": "#D9D9D9",
    "status_fg": "#333333",
}

DARK_THEME = {
    "bg": "#2E2E2E",
    "fg": "#EAEAEA",
    "entry_bg": "#3C3C3C",
    "entry_fg": "#EAEAEA",
    "button_bg": "#505050",
    "button_fg": "#EAEAEA",
    "list_bg": "#3C3C3C",
    "list_fg": "#EAEAEA",
    "list_select_bg": "#005A9E", # Slightly darker blue
    "list_select_fg": "#FFFFFF",
    "completed_fg": "#777777",
    "prio_low_bg": "#3A5F3A",    # Darker green
    "prio_medium_bg": "#6B603C", # Darker yellow/brown
    "prio_high_bg": "#724343",   # Darker red
    "status_bg": "#404040",
    "status_fg": "#CCCCCC",
}

# --- Data Persistence Logic ---
TASKS_FILE = "tasks_enhanced_ui.json"
PRIORITIES = ["Low", "Medium", "High"] # Order matters for display logic later

def load_tasks():
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
                # Add default priority if missing from old file format
                if isinstance(task, dict) and 'description' in task and 'completed' in task:
                    if 'priority' not in task or task['priority'] not in PRIORITIES:
                        task['priority'] = "Medium" # Default priority
                    valid_tasks.append(task)
                else:
                    print(f"Warning: Skipping invalid task data: {task}")
            return valid_tasks
    except json.JSONDecodeError:
        messagebox.showwarning("Load Warning", f"Could not decode JSON. Starting fresh.")
        return []
    except Exception as e:
        messagebox.showerror("Load Error", f"An error occurred loading tasks:\n{e}\nStarting fresh.")
        return []

def save_tasks(tasks):
    try:
        with open(TASKS_FILE, 'w') as f:
            json.dump(tasks, f, indent=4)
    except Exception as e:
        messagebox.showerror("Save Error", f"Could not save tasks:\n{e}")

# --- GUI Application Class ---
class TodoApp:
    def __init__(self, root_window):
        self.root = root_window
        self.root.title("Advanced To-Do App")
        self.root.geometry("600x550") # Slightly larger window
        self.root.minsize(500, 450)

        # --- Data ---
        self.tasks = load_tasks()
        self.current_filter = StringVar(value="All") # Filter state
        self.current_theme = StringVar(value="Light") # Theme state

        # --- Style Configuration ---
        self.style = ttk.Style()
        # Try to set a decent theme
        available_themes = self.style.theme_names()
        if 'clam' in available_themes:
            self.style.theme_use('clam')
        elif 'vista' in available_themes: # Good fallback on Windows
             self.style.theme_use('vista')
        # Fonts
        self.default_font = tkFont.nametofont("TkDefaultFont")
        self.strikethrough_font = tkFont.Font(family=self.default_font.actual("family"),
                                             size=self.default_font.actual("size"),
                                             overstrike=True)
        self.list_font = tkFont.Font(family="Segoe UI", size=11) # Specific font for list

        # --- Apply Initial Theme ---
        self.theme_colors = LIGHT_THEME
        self.apply_theme() # Apply light theme initially

        # --- Configure root window grid ---
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1) # List frame row expands

        # --- Menu Bar ---
        self.menu_bar = Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # File Menu
        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Save Now", command=lambda: save_tasks(self.tasks))
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.on_closing)

        # View Menu
        self.view_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="View", menu=self.view_menu)
        self.theme_menu = Menu(self.view_menu, tearoff=0)
        self.view_menu.add_cascade(label="Theme", menu=self.theme_menu)
        self.theme_menu.add_radiobutton(label="Light", variable=self.current_theme, value="Light", command=self.switch_theme)
        self.theme_menu.add_radiobutton(label="Dark", variable=self.current_theme, value="Dark", command=self.switch_theme)


        # --- UI Elements ---

        # Input Frame
        self.input_frame = ttk.Frame(self.root, padding="10")
        self.input_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10,0))
        self.input_frame.columnconfigure(0, weight=1) # Entry expands

        self.task_entry = ttk.Entry(self.input_frame, width=40, font=(self.list_font.actual("family"), 10))
        self.task_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5), ipady=2)
        self.task_entry.bind("<Return>", self.add_task_event)

        self.priority_var = StringVar(value="Medium") # Default priority for new tasks
        self.priority_dropdown = ttk.OptionMenu(self.input_frame, self.priority_var, "Medium", *PRIORITIES)
        self.priority_dropdown.grid(row=0, column=1, padx=5)

        self.add_button = ttk.Button(self.input_frame, text="Add Task", command=self.add_task, style="Accent.TButton") # Accent style
        self.add_button.grid(row=0, column=2)

        # Filter Frame
        self.filter_frame = ttk.Frame(self.root, padding="10 5 10 5")
        self.filter_frame.grid(row=1, column=0, sticky="ew", padx=10)
        ttk.Label(self.filter_frame, text="Filter:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Radiobutton(self.filter_frame, text="All", variable=self.current_filter, value="All", command=self.filter_tasks).pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(self.filter_frame, text="Active", variable=self.current_filter, value="Active", command=self.filter_tasks).pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(self.filter_frame, text="Completed", variable=self.current_filter, value="Completed", command=self.filter_tasks).pack(side=tk.LEFT, padx=2)

        # List Frame
        self.list_frame = ttk.Frame(self.root, padding="10 0 10 10") # More bottom padding
        self.list_frame.grid(row=2, column=0, sticky="nsew", padx=10)
        self.list_frame.columnconfigure(0, weight=1)
        self.list_frame.rowconfigure(0, weight=1)

        self.task_listbox = Listbox(
            self.list_frame,
            font=self.list_font,
            borderwidth=0,
            highlightthickness=1, # Keep a subtle border
            activestyle='none', # Cleaner selection look
            exportselection=False # Keep selection when focus leaves
        )
        self.task_listbox.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.task_listbox.bind("<Double-Button-1>", self.toggle_complete_event)
        self.task_listbox.bind("<<ListboxSelect>>", self.update_button_states) # Update buttons on selection change

        self.scrollbar = ttk.Scrollbar(
            self.list_frame, orient=tk.VERTICAL, command=self.task_listbox.yview
        )
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.task_listbox.config(yscrollcommand=self.scrollbar.set)

        # Action Frame
        self.action_frame = ttk.Frame(self.root, padding="10 5 10 10")
        self.action_frame.grid(row=3, column=0, sticky="ew", padx=10)
        # Using pack inside for simpler centering/spacing of buttons
        self.toggle_button = ttk.Button(self.action_frame, text="Toggle Complete", command=self.toggle_complete, state=tk.DISABLED)
        self.toggle_button.pack(side=tk.LEFT, padx=5)

        self.edit_button = ttk.Button(self.action_frame, text="Edit Task", command=self.edit_task, state=tk.DISABLED)
        self.edit_button.pack(side=tk.LEFT, padx=5)

        self.delete_button = ttk.Button(self.action_frame, text="Delete Task", command=self.delete_task, state=tk.DISABLED)
        self.delete_button.pack(side=tk.LEFT, padx=5)

        # Spacer to push Clear button to the right
        ttk.Frame(self.action_frame).pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.clear_button = ttk.Button(self.action_frame, text="Clear Completed", command=self.clear_completed_tasks)
        self.clear_button.pack(side=tk.RIGHT, padx=5)

        # Status Bar
        self.status_var = StringVar(value="Ready")
        self.status_bar = Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W, font=("Segoe UI", 8))
        self.status_bar.grid(row=4, column=0, sticky="ew")

        # --- Initial Population & State ---
        self.displayed_tasks_indices = [] # Store original indices of displayed tasks
        self.populate_listbox()
        self.update_status(f"{len(self.tasks)} tasks loaded.")
        self.task_entry.focus_set()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.update_button_states() # Set initial button states


    # --- Theme Management ---
    def switch_theme(self):
        theme_name = self.current_theme.get()
        if theme_name == "Light":
            self.theme_colors = LIGHT_THEME
        else:
            self.theme_colors = DARK_THEME
        self.apply_theme()
        self.populate_listbox() # Repopulate to apply list colors
        self.update_status(f"Switched to {theme_name} theme.")

    def apply_theme(self):
        colors = self.theme_colors
        # Configure root and standard tk widgets
        self.root.config(bg=colors["bg"])
        self.status_bar.config(bg=colors["status_bg"], fg=colors["status_fg"])
        # Configure Listbox explicitly
        self.task_listbox.config(
            bg=colors["list_bg"], fg=colors["list_fg"],
            selectbackground=colors["list_select_bg"], selectforeground=colors["list_select_fg"]
        )

        # Configure ttk styles
        self.style.configure("TFrame", background=colors["bg"])
        self.style.configure("TLabel", background=colors["bg"], foreground=colors["fg"])
        self.style.configure("TButton", background=colors["button_bg"], foreground=colors["button_fg"])
        self.style.map("TButton", background=[('active', colors["list_select_bg"])]) # Hover/active color
        self.style.configure("Accent.TButton", background=colors["list_select_bg"], foreground=colors["list_select_fg"]) # Style for Add button
        self.style.map("Accent.TButton", background=[('active', colors["list_bg"])], foreground=[('active', colors["list_select_bg"])])

        self.style.configure("TEntry", fieldbackground=colors["entry_bg"], foreground=colors["entry_fg"])
        self.style.map("TEntry", foreground=[('focus', colors["fg"])])
        self.style.configure("TRadiobutton", background=colors["bg"], foreground=colors["fg"])
        self.style.map("TRadiobutton", background=[('active', colors["bg"])], indicatorcolor=[('selected', colors["list_select_bg"])])
        self.style.configure("TCombobox", fieldbackground=colors["entry_bg"], foreground=colors["entry_fg"]) # OptionMenu uses Combobox style
        self.style.map("TCombobox", fieldbackground=[('readonly', colors["entry_bg"])], foreground=[('readonly', colors["entry_fg"])])
        self.style.configure("Vertical.TScrollbar", background=colors["button_bg"], troughcolor=colors["bg"])


    # --- Core Functionality ---
    def get_selected_original_index(self):
        """Gets the original index (from self.tasks) of the selected item."""
        selected_list_indices = self.task_listbox.curselection()
        if not selected_list_indices:
            return None
        list_index = selected_list_indices[0]
        if 0 <= list_index < len(self.displayed_tasks_indices):
            return self.displayed_tasks_indices[list_index]
        return None # Should not happen if list and indices are synced

    def filter_tasks(self):
        """Repopulate listbox based on the current filter."""
        self.populate_listbox()
        self.update_status(f"Filter set to: {self.current_filter.get()}")

    def populate_listbox(self):
        """Clears and refills the listbox based on the filter and self.tasks list."""
        current_selection_original_index = self.get_selected_original_index()
        self.task_listbox.delete(0, tk.END)
        self.displayed_tasks_indices = [] # Reset the mapping

        filter_mode = self.current_filter.get()

        new_list_index = -1 # Track the new index for selection restoration

        for original_index, task in enumerate(self.tasks):
            # Apply filter
            if filter_mode == "Active" and task['completed']:
                continue
            if filter_mode == "Completed" and not task['completed']:
                continue

            # Task passes filter, add its original index to our map
            self.displayed_tasks_indices.append(original_index)
            listbox_index = len(self.displayed_tasks_indices) - 1 # The index in the listbox display

            # Format display text
            status = "[X]" if task['completed'] else "[ ]"
            prio_map = {"Low": "[L]", "Medium": "[M]", "High": "[H]"}
            prio_indicator = prio_map.get(task['priority'], "[?]") # Fallback
            display_text = f"{status} {prio_indicator} {task['description']}"
            self.task_listbox.insert(tk.END, display_text)

            # Apply styling based on state and priority
            colors = self.theme_colors
            if task['completed']:
                self.task_listbox.itemconfig(listbox_index, {'fg': colors["completed_fg"]})
                self.task_listbox.itemconfig(listbox_index, {'font': self.strikethrough_font})
                self.task_listbox.itemconfig(listbox_index, {'bg': colors["list_bg"]}) # Ensure default bg for completed
            else:
                prio_bg = {
                    "Low": colors["prio_low_bg"],
                    "Medium": colors["prio_medium_bg"],
                    "High": colors["prio_high_bg"]
                }.get(task['priority'], colors["list_bg"]) # Fallback to default

                self.task_listbox.itemconfig(listbox_index, {'fg': colors["list_fg"]})
                self.task_listbox.itemconfig(listbox_index, {'font': self.list_font}) # Use specific list font
                self.task_listbox.itemconfig(listbox_index, {'bg': prio_bg}) # Set priority background

            # Check if this item was the one previously selected
            if original_index == current_selection_original_index:
                new_list_index = listbox_index

        # Restore selection if possible
        if new_list_index != -1:
            self.task_listbox.selection_set(new_list_index)
            self.task_listbox.activate(new_list_index)
            self.task_listbox.see(new_list_index)

        self.update_button_states()
        self.update_clear_button_state()


    def add_task(self):
        task_description = self.task_entry.get().strip()
        task_priority = self.priority_var.get()
        if task_description:
            new_task = {"description": task_description, "completed": False, "priority": task_priority}
            self.tasks.append(new_task)
            self.populate_listbox() # Will apply filter correctly
            # Select the newly added task if it matches the current filter
            try:
                new_original_index = len(self.tasks) - 1
                if new_original_index in self.displayed_tasks_indices:
                    list_index = self.displayed_tasks_indices.index(new_original_index)
                    self.task_listbox.selection_clear(0, tk.END)
                    self.task_listbox.selection_set(list_index)
                    self.task_listbox.activate(list_index)
                    self.task_listbox.see(list_index)
            except ValueError:
                 pass # Task added doesn't match current filter

            self.task_entry.delete(0, tk.END)
            self.update_status(f"Task '{task_description}' ({task_priority}) added.")
        else:
            messagebox.showwarning("Input Error", "Task description cannot be empty.")
            self.update_status("Add task failed: Description empty.")
        self.task_entry.focus_set()

    def add_task_event(self, event):
        self.add_task()

    def toggle_complete(self):
        original_index = self.get_selected_original_index()
        if original_index is None: return # Button should be disabled anyway

        if 0 <= original_index < len(self.tasks):
            task = self.tasks[original_index]
            task['completed'] = not task['completed']
            status_text = "completed" if task['completed'] else "active"
            self.populate_listbox() # Will update display and potentially filter item out/in
            self.update_status(f"Task marked as {status_text}.")
        else:
             messagebox.showerror("Error", "Invalid task index.")

    def toggle_complete_event(self, event):
        # Check if click is on an actual item
        clicked_index = self.task_listbox.nearest(event.y)
        if clicked_index >= 0 and clicked_index < self.task_listbox.size():
             # Select the item first if not already selected by double click
             if not self.task_listbox.selection_includes(clicked_index):
                 self.task_listbox.selection_clear(0, tk.END)
                 self.task_listbox.selection_set(clicked_index)
                 self.task_listbox.activate(clicked_index)
             self.toggle_complete()


    def edit_task(self):
        """Opens a dialog to edit the selected task's description and priority."""
        original_index = self.get_selected_original_index()
        if original_index is None: return

        task = self.tasks[original_index]

        # --- Create Edit Dialog (Toplevel window) ---
        edit_dialog = Toplevel(self.root)
        edit_dialog.title("Edit Task")
        edit_dialog.transient(self.root) # Keep dialog on top of main window
        edit_dialog.grab_set() # Modal behavior
        edit_dialog.resizable(False, False)
        # Apply theme colors to dialog
        edit_dialog.config(bg=self.theme_colors["bg"], padx=15, pady=10)

        # Description
        ttk.Label(edit_dialog, text="Description:", background=self.theme_colors["bg"], foreground=self.theme_colors["fg"]).grid(row=0, column=0, sticky="w", pady=(0, 2))
        desc_entry = ttk.Entry(edit_dialog, width=40, font=self.default_font)
        desc_entry.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        desc_entry.insert(0, task['description'])
        desc_entry.focus_set()
        desc_entry.selection_range(0, tk.END)

        # Priority
        ttk.Label(edit_dialog, text="Priority:", background=self.theme_colors["bg"], foreground=self.theme_colors["fg"]).grid(row=2, column=0, sticky="w", pady=(0, 2))
        edit_priority_var = StringVar(value=task['priority'])
        edit_prio_menu = ttk.OptionMenu(edit_dialog, edit_priority_var, task['priority'], *PRIORITIES)
        edit_prio_menu.grid(row=3, column=0, columnspan=2, sticky="w", pady=(0, 15))

        # --- Dialog Buttons Frame ---
        btn_frame = ttk.Frame(edit_dialog, style="TFrame") # Use ttk Frame
        btn_frame.grid(row=4, column=0, columnspan=2, sticky="e")

        def save_edit():
            new_desc = desc_entry.get().strip()
            new_prio = edit_priority_var.get()
            if not new_desc:
                messagebox.showwarning("Input Error", "Description cannot be empty.", parent=edit_dialog)
                return

            # Update the task in the main list
            self.tasks[original_index]['description'] = new_desc
            self.tasks[original_index]['priority'] = new_prio
            self.populate_listbox() # Update the main list display
            self.update_status(f"Task '{new_desc}' updated.")
            edit_dialog.destroy()

        def cancel_edit():
            edit_dialog.destroy()

        # Use standard tk Buttons here for simpler background coloring if needed, or styled ttk
        save_btn = ttk.Button(btn_frame, text="Save", command=save_edit, style="Accent.TButton")
        save_btn.pack(side=tk.RIGHT, padx=(5, 0))
        cancel_btn = ttk.Button(btn_frame, text="Cancel", command=cancel_edit)
        cancel_btn.pack(side=tk.RIGHT)

        # Center the dialog
        edit_dialog.update_idletasks() # Ensure window size is calculated
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (edit_dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 3) - (edit_dialog.winfo_height() // 2)
        edit_dialog.geometry(f"+{x}+{y}")

        edit_dialog.wait_window() # Wait until the dialog is closed


    def delete_task(self):
        original_index = self.get_selected_original_index()
        if original_index is None: return

        task_description = self.tasks[original_index]['description']
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to permanently delete this task?\n\n'{task_description}'"
        )
        if confirm:
            if 0 <= original_index < len(self.tasks):
                del self.tasks[original_index]
                self.populate_listbox() # Update display (selection will be lost)
                self.update_status(f"Task '{task_description}' deleted.")
            else:
                 messagebox.showerror("Error", "Invalid task index during deletion.")
        else:
            self.update_status("Deletion cancelled.")

    def clear_completed_tasks(self):
        completed_tasks_exist = any(task['completed'] for task in self.tasks)
        if not completed_tasks_exist:
            messagebox.showinfo("Clear Completed", "There are no completed tasks to clear.")
            self.update_status("No completed tasks to clear.")
            return

        confirm = messagebox.askyesno(
            "Confirm Clear",
            "Are you sure you want to permanently delete all completed tasks?"
        )
        if confirm:
            initial_count = len(self.tasks)
            self.tasks = [task for task in self.tasks if not task['completed']]
            cleared_count = initial_count - len(self.tasks)
            self.populate_listbox()
            self.update_status(f"Cleared {cleared_count} completed task(s).")
        else:
             self.update_status("Clear completed cancelled.")


    # --- UI State Management ---
    def update_status(self, message):
        self.status_var.set(message)

    def update_button_states(self, event=None): # event=None needed for direct calls
        """Enable/disable action buttons based on selection"""
        selected = self.get_selected_original_index() is not None
        state = tk.NORMAL if selected else tk.DISABLED
        self.toggle_button.config(state=state)
        self.edit_button.config(state=state)
        self.delete_button.config(state=state)

    def update_clear_button_state(self):
        """Enable Clear Completed button only if there are completed tasks"""
        completed_tasks_exist = any(task['completed'] for task in self.tasks)
        self.clear_button.config(state=tk.NORMAL if completed_tasks_exist else tk.DISABLED)


    # --- Closing ---
    def on_closing(self):
        self.update_status("Saving tasks...")
        save_tasks(self.tasks)
        print("Tasks saved. Exiting.")
        self.root.destroy()


# --- Main Execution ---
if __name__ == "__main__":
    main_window = tk.Tk()
    app = TodoApp(main_window)
    main_window.mainloop()