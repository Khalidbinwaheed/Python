import tkinter as tk
from tkinter import ttk  # Themed widgets for a better look
from tkinter import messagebox
from tkinter import simpledialog
# Consider using tkcalendar for date entry if installed: pip install tkcalendar
# from tkcalendar import DateEntry # Example if tkcalendar is installed

# --- Placeholder Data (Replace with database interaction later) ---
# Sample room data: Room Number, Type, Status, Price per night
rooms_data = {
    "101": {"type": "Single", "status": "Available", "price": 80},
    "102": {"type": "Single", "status": "Occupied", "price": 80},
    "201": {"type": "Double", "status": "Available", "price": 120},
    "202": {"type": "Double", "status": "Cleaning", "price": 120},
    "301": {"type": "Suite", "status": "Available", "price": 250},
}

# Sample guest data: Guest ID, Name, Contact
guests_data = {
    1: {"name": "Alice Smith", "contact": "555-1234"},
    2: {"name": "Bob Johnson", "contact": "555-5678"},
}
next_guest_id = 3

# Sample booking data: Booking ID, Guest ID, Room Number, Check-in, Check-out
bookings_data = {
    1001: {"guest_id": 1, "room": "102", "check_in": "2023-10-26", "check_out": "2023-10-28"},
}
next_booking_id = 1002
# --- End Placeholder Data ---


class HotelApp(tk.Tk):
    """Main Application Window for the Hotel Management System."""

    def __init__(self):
        super().__init__()  # Initialize the tk.Tk parent class

        self.title("Hotel Management System")
        # Set a reasonable starting size
        self.geometry("900x600")
        # Configure grid to allow content to expand
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Style ---
        # Use a theme for a better look (clam, alt, default, classic)
        self.style = ttk.Style(self)
        try:
            # 'clam' or 'alt' often look better than 'default' on some systems
            self.style.theme_use("clam")
        except tk.TclError:
            print("Clam theme not available, using default.")
            self.style.theme_use("default")

        # Configure styles for specific widgets if needed
        self.style.configure("TLabel", padding=5, font=('Helvetica', 10))
        self.style.configure("TButton", padding=5, font=('Helvetica', 10))
        self.style.configure("Treeview.Heading", font=('Helvetica', 11, 'bold'))
        self.style.configure("TFrame", background='#f0f0f0') # Light grey background for frames

        # --- Menu Bar ---
        self.create_menu()

        # --- Main Content Area ---
        # This frame will hold the different "pages" or views
        self.container = ttk.Frame(self, padding="10 10 10 10")
        self.container.grid(row=1, column=0, sticky="nsew") # Expand to fill space
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Dictionary to store frames (views)
        self.frames = {}

        # Create and store frames for each major section
        for F in (DashboardFrame, RoomManagementFrame, GuestManagementFrame, BookingFrame, CheckInOutFrame):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            # Place each frame in the same grid cell; only the top one will be visible
            frame.grid(row=0, column=0, sticky="nsew")

        # --- Status Bar ---
        self.status_var = tk.StringVar()
        self.status_var.set("Welcome to the Hotel Management System!")
        status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, padding=5)
        status_bar.grid(row=2, column=0, sticky="ew") # Span across the bottom

        # Show the initial frame (Dashboard)
       

    def create_menu(self):
        """Creates the main application menu bar."""
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar) # Attach menu bar to the window

        # --- File Menu ---
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.quit) # Use built-in quit

        # --- View Menu ---
        view_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Dashboard", command=lambda: self.show_frame("DashboardFrame"))
        view_menu.add_command(label="Rooms", command=lambda: self.show_frame("RoomManagementFrame"))
        view_menu.add_command(label="Guests", command=lambda: self.show_frame("GuestManagementFrame"))
        # Add separators for clarity
        view_menu.add_separator()

        # --- Actions Menu ---
        actions_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Actions", menu=actions_menu)
        actions_menu.add_command(label="New Booking", command=lambda: self.show_frame("BookingFrame"))
        actions_menu.add_command(label="Check-in / Check-out", command=lambda: self.show_frame("CheckInOutFrame"))

        # --- Help Menu ---
        help_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def show_frame(self, page_name):
        """Raises the requested frame to the top."""
        frame = self.frames[page_name]
        # Update status bar maybe
        self.status_var.set(f"Viewing {page_name.replace('Frame', '')}")
        frame.tkraise() # Bring the frame to the front
        # Optionally, refresh frame data when shown
        if hasattr(frame, 'refresh_data'):
            frame.refresh_data()

    def show_about(self):
        """Displays a simple About dialog."""
        messagebox.showinfo("About", "Hotel Management System v1.0\nCreated with Python and Tkinter")

    def update_status(self, message):
        """Updates the text in the status bar."""
        self.status_var.set(message)

# --- Frame Classes (Representing different views/pages) ---

class DashboardFrame(ttk.Frame):
    """The initial view shown when the application starts."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller # To access main app methods like update_status

        # Configure grid layout for this frame
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Title Label
        label = ttk.Label(self, text="Dashboard", font=('Helvetica', 16, 'bold'))
        label.grid(row=0, column=0, columnspan=2, pady=10, sticky="n")

        # --- Quick Stats Area (Example) ---
        stats_frame = ttk.LabelFrame(self, text="Quick Stats", padding=10)
        stats_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        stats_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(stats_frame, text="Available Rooms:").grid(row=0, column=0, sticky="w", pady=2)
        self.available_rooms_var = tk.StringVar(value="...") # Placeholder
        ttk.Label(stats_frame, textvariable=self.available_rooms_var).grid(row=0, column=1, sticky="w", pady=2)

        ttk.Label(stats_frame, text="Occupied Rooms:").grid(row=1, column=0, sticky="w", pady=2)
        self.occupied_rooms_var = tk.StringVar(value="...") # Placeholder
        ttk.Label(stats_frame, textvariable=self.occupied_rooms_var).grid(row=1, column=1, sticky="w", pady=2)

        # --- Quick Actions Area ---
        actions_frame = ttk.LabelFrame(self, text="Quick Actions", padding=10)
        actions_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        actions_frame.grid_columnconfigure(0, weight=1) # Make button expand

        book_btn = ttk.Button(actions_frame, text="New Booking",
                              command=lambda: controller.show_frame("BookingFrame"))
        book_btn.grid(row=0, column=0, pady=5, sticky="ew")

        checkin_btn = ttk.Button(actions_frame, text="Check-in / Check-out",
                                 command=lambda: controller.show_frame("CheckInOutFrame"))
        checkin_btn.grid(row=1, column=0, pady=5, sticky="ew")

        rooms_btn = ttk.Button(actions_frame, text="View Rooms",
                               command=lambda: controller.show_frame("RoomManagementFrame"))
        rooms_btn.grid(row=2, column=0, pady=5, sticky="ew")

        guests_btn = ttk.Button(actions_frame, text="View Guests",
                                command=lambda: controller.show_frame("GuestManagementFrame"))
        guests_btn.grid(row=3, column=0, pady=5, sticky="ew")


    def refresh_data(self):
        """Update dashboard stats when shown."""
        # In a real app, fetch this from the database/backend
        available = sum(1 for room in rooms_data.values() if room['status'] == 'Available')
        occupied = sum(1 for room in rooms_data.values() if room['status'] == 'Occupied')
        self.available_rooms_var.set(str(available))
        self.occupied_rooms_var.set(str(occupied))
        self.controller.update_status("Dashboard refreshed.")


class RoomManagementFrame(ttk.Frame):
    """Frame for viewing and managing hotel rooms."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = ttk.Label(self, text="Room Management", font=('Helvetica', 16, 'bold'))
        label.pack(pady=10)

        # --- Treeview for Room Data ---
        columns = ("room_no", "type", "status", "price")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")

        # Define headings
        self.tree.heading("room_no", text="Room No.")
        self.tree.heading("type", text="Type")
        self.tree.heading("status", text="Status")
        self.tree.heading("price", text="Price/Night ($)")

        # Configure column widths (adjust as needed)
        self.tree.column("room_no", width=80, anchor=tk.CENTER)
        self.tree.column("type", width=120, anchor=tk.W)
        self.tree.column("status", width=100, anchor=tk.W)
        self.tree.column("price", width=100, anchor=tk.E) # Align price to the right

        # Add a scrollbar
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Pack the treeview and scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)

        # --- Buttons for Room Actions ---
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        # In a real app, these buttons would do more (e.g., open edit dialogs)
        refresh_btn = ttk.Button(button_frame, text="Refresh List", command=self.refresh_data)
        refresh_btn.pack(side=tk.LEFT, padx=5)

        clean_btn = ttk.Button(button_frame, text="Mark as Cleaning", command=self.mark_cleaning)
        clean_btn.pack(side=tk.LEFT, padx=5)

        available_btn = ttk.Button(button_frame, text="Mark as Available", command=self.mark_available)
        available_btn.pack(side=tk.LEFT, padx=5)

        # Populate the treeview initially
        self.refresh_data()

    def refresh_data(self):
        """Clears and reloads the room data into the treeview."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Load data from placeholder (replace with DB query)
        for room_no, data in sorted(rooms_data.items()):
            values = (room_no, data['type'], data['status'], f"{data['price']:.2f}")
            self.tree.insert("", tk.END, values=values) # Insert as top-level item
        self.controller.update_status("Room list refreshed.")

    def get_selected_room(self):
        """Gets the room number of the currently selected item in the tree."""
        selected_item = self.tree.focus() # Get the ID of the selected item
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a room from the list first.")
            return None
        item_values = self.tree.item(selected_item, "values")
        return item_values[0] # The first value is the room number

    def mark_cleaning(self):
        """Placeholder: Marks the selected room as 'Cleaning'."""
        room_no = self.get_selected_room()
        if room_no:
            # --- Actual Logic Placeholder ---
            if rooms_data[room_no]['status'] == 'Occupied':
                 messagebox.showerror("Error", f"Room {room_no} is occupied. Cannot mark for cleaning.")
                 return
            print(f"Marking room {room_no} as Cleaning (Placeholder)")
            rooms_data[room_no]['status'] = 'Cleaning'
            self.controller.update_status(f"Room {room_no} marked as Cleaning.")
            # --- End Placeholder ---
            self.refresh_data() # Update the view

    def mark_available(self):
        """Placeholder: Marks the selected room as 'Available'."""
        room_no = self.get_selected_room()
        if room_no:
             # --- Actual Logic Placeholder ---
            if rooms_data[room_no]['status'] == 'Occupied':
                 messagebox.showerror("Error", f"Room {room_no} is occupied. Cannot mark as available directly.")
                 return
            print(f"Marking room {room_no} as Available (Placeholder)")
            rooms_data[room_no]['status'] = 'Available'
            self.controller.update_status(f"Room {room_no} marked as Available.")
            # --- End Placeholder ---
            self.refresh_data() # Update the view


class GuestManagementFrame(ttk.Frame):
    """Frame for viewing and managing hotel guests."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = ttk.Label(self, text="Guest Management", font=('Helvetica', 16, 'bold'))
        label.pack(pady=10)

        # --- Treeview for Guest Data ---
        columns = ("guest_id", "name", "contact")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("guest_id", text="Guest ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("contact", text="Contact Info")

        self.tree.column("guest_id", width=80, anchor=tk.CENTER)
        self.tree.column("name", width=200, anchor=tk.W)
        self.tree.column("contact", width=150, anchor=tk.W)

        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)

        # --- Buttons for Guest Actions ---
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        refresh_btn = ttk.Button(button_frame, text="Refresh List", command=self.refresh_data)
        refresh_btn.pack(side=tk.LEFT, padx=5)

        add_btn = ttk.Button(button_frame, text="Add New Guest", command=self.add_guest)
        add_btn.pack(side=tk.LEFT, padx=5)

        # In a real app, add Edit/Delete buttons that work on selection
        # edit_btn = ttk.Button(button_frame, text="Edit Selected", command=self.edit_guest)
        # edit_btn.pack(side=tk.LEFT, padx=5)

        self.refresh_data()

    def refresh_data(self):
        """Clears and reloads guest data."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        for guest_id, data in sorted(guests_data.items()):
            values = (guest_id, data['name'], data['contact'])
            self.tree.insert("", tk.END, values=values)
        self.controller.update_status("Guest list refreshed.")

    def add_guest(self):
        """Placeholder: Opens dialogs to add a new guest."""
        global next_guest_id # Allow modification of the global counter

        name = simpledialog.askstring("New Guest", "Enter Guest Name:", parent=self)
        if not name: return # User cancelled

        contact = simpledialog.askstring("New Guest", f"Enter Contact Info for {name}:", parent=self)
        if not contact: return # User cancelled

        # --- Actual Logic Placeholder ---
        new_id = next_guest_id
        guests_data[new_id] = {"name": name, "contact": contact}
        next_guest_id += 1
        print(f"Adding guest {new_id}: {name}, {contact} (Placeholder)")
        self.controller.update_status(f"Added new guest: {name}")
        # --- End Placeholder ---

        self.refresh_data() # Update the view


class BookingFrame(ttk.Frame):
    """Frame for creating a new booking."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = ttk.Label(self, text="New Booking", font=('Helvetica', 16, 'bold'))
        label.grid(row=0, column=0, columnspan=2, pady=10, padx=10)

        # --- Booking Form ---
        form_frame = ttk.Frame(self, padding=10)
        form_frame.grid(row=1, column=0, columnspan=2, padx=10, sticky='ew')
        form_frame.columnconfigure(1, weight=1) # Make entry fields expand

        # Guest Name (or ID - could use a Combobox linked to guests_data)
        ttk.Label(form_frame, text="Guest Name:").grid(row=0, column=0, sticky="w", pady=5)
        self.guest_name_var = tk.StringVar()
        guest_entry = ttk.Entry(form_frame, textvariable=self.guest_name_var, width=40)
        guest_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=5)

        # Room Number (Could use a Combobox with available rooms)
        ttk.Label(form_frame, text="Room Number:").grid(row=1, column=0, sticky="w", pady=5)
        self.room_no_var = tk.StringVar()
        room_entry = ttk.Entry(form_frame, textvariable=self.room_no_var, width=15)
        room_entry.grid(row=1, column=1, sticky="w", pady=5, padx=5) # Use sticky 'w'

        # Check-in Date
        ttk.Label(form_frame, text="Check-in Date:").grid(row=2, column=0, sticky="w", pady=5)
        self.checkin_var = tk.StringVar()
        # If tkcalendar is available, use DateEntry for a better experience
        # checkin_entry = DateEntry(form_frame, textvariable=self.checkin_var, date_pattern='yyyy-mm-dd', width=12)
        checkin_entry = ttk.Entry(form_frame, textvariable=self.checkin_var, width=15)
        checkin_entry.grid(row=2, column=1, sticky="w", pady=5, padx=5)
        checkin_entry.insert(0, "YYYY-MM-DD") # Placeholder format

        # Check-out Date
        ttk.Label(form_frame, text="Check-out Date:").grid(row=3, column=0, sticky="w", pady=5)
        self.checkout_var = tk.StringVar()
        # checkout_entry = DateEntry(form_frame, textvariable=self.checkout_var, date_pattern='yyyy-mm-dd', width=12)
        checkout_entry = ttk.Entry(form_frame, textvariable=self.checkout_var, width=15)
        checkout_entry.grid(row=3, column=1, sticky="w", pady=5, padx=5)
        checkout_entry.insert(0, "YYYY-MM-DD") # Placeholder format

        # Submit Button
        submit_button = ttk.Button(self, text="Create Booking", command=self.create_booking)
        submit_button.grid(row=2, column=0, columnspan=2, pady=20)

    def create_booking(self):
        """Placeholder: 'Creates' a booking with the entered data."""
        global next_booking_id # Allow modification

        guest_name = self.guest_name_var.get()
        room_no = self.room_no_var.get()
        check_in = self.checkin_var.get()
        check_out = self.checkout_var.get()

        # --- Basic Validation ---
        if not all([guest_name, room_no, check_in, check_out]) or "YYYY-MM-DD" in [check_in, check_out]:
            messagebox.showerror("Input Error", "Please fill in all fields correctly.")
            return

        if room_no not in rooms_data:
            messagebox.showerror("Input Error", f"Room {room_no} does not exist.")
            return

        if rooms_data[room_no]['status'] != 'Available':
             messagebox.showerror("Booking Error", f"Room {room_no} is not available for booking.")
             return

        # Find guest ID (simple search, real app needs better linking)
        guest_id = None
        for gid, gdata in guests_data.items():
            if gdata['name'].lower() == guest_name.lower():
                guest_id = gid
                break
        if guest_id is None:
            # Optionally, auto-add guest or show error/guest selection
            if messagebox.askyesno("New Guest?", f"Guest '{guest_name}' not found. Add as new guest?"):
                 # For simplicity, just add guest here. Real app: go to guest management or more robust flow.
                 global next_guest_id
                 contact = simpledialog.askstring("New Guest Contact", f"Enter contact info for {guest_name}:", parent=self)
                 if contact:
                     guest_id = next_guest_id
                     guests_data[guest_id] = {"name": guest_name, "contact": contact}
                     next_guest_id += 1
                     self.controller.update_status(f"Added new guest: {guest_name}")
                 else:
                     messagebox.showerror("Booking Error", "Cannot create booking without guest contact.")
                     return
            else:
                 messagebox.showerror("Booking Error", f"Guest '{guest_name}' not found. Booking cancelled.")
                 return


        # --- Actual Logic Placeholder ---
        booking_id = next_booking_id
        bookings_data[booking_id] = {
            "guest_id": guest_id,
            "room": room_no,
            "check_in": check_in,
            "check_out": check_out
        }
        # Mark room as occupied (simplistic, real app needs check-in step)
        # rooms_data[room_no]['status'] = 'Occupied' # Usually happens at check-in
        next_booking_id += 1
        print(f"Booking {booking_id} created: Guest {guest_id}, Room {room_no}, {check_in} to {check_out} (Placeholder)")
        # --- End Placeholder ---

        messagebox.showinfo("Booking Confirmed", f"Booking created successfully!\nID: {booking_id}\nGuest: {guest_name}\nRoom: {room_no}")
        self.controller.update_status(f"Booking {booking_id} created for room {room_no}.")

        # Clear form
        self.guest_name_var.set("")
        self.room_no_var.set("")
        self.checkin_var.set("YYYY-MM-DD")
        self.checkout_var.set("YYYY-MM-DD")

        # Optionally switch view or refresh lists
        # self.controller.show_frame("DashboardFrame")


class CheckInOutFrame(ttk.Frame):
    """Frame for handling Check-in and Check-out."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = ttk.Label(self, text="Check-in / Check-out", font=('Helvetica', 16, 'bold'))
        label.grid(row=0, column=0, columnspan=2, pady=10, padx=10)

        # --- Input Area ---
        input_frame = ttk.Frame(self, padding=10)
        input_frame.grid(row=1, column=0, columnspan=2, padx=10, sticky='ew')
        input_frame.columnconfigure(1, weight=1)

        ttk.Label(input_frame, text="Booking ID / Room No:").grid(row=0, column=0, sticky="w", pady=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(input_frame, textvariable=self.search_var, width=30)
        search_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=5)

        # --- Action Buttons ---
        button_frame = ttk.Frame(self)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)

        checkin_btn = ttk.Button(button_frame, text="Perform Check-in", command=self.perform_checkin)
        checkin_btn.pack(side=tk.LEFT, padx=10)

        checkout_btn = ttk.Button(button_frame, text="Perform Check-out", command=self.perform_checkout)
        checkout_btn.pack(side=tk.LEFT, padx=10)

    def perform_checkin(self):
        """Placeholder: Performs check-in based on Booking ID or Room No."""
        search_key = self.search_var.get()
        if not search_key:
            messagebox.showerror("Input Error", "Please enter a Booking ID or Room Number.")
            return

        # --- Actual Logic Placeholder ---
        # Find booking (could be by ID or guest name/room assigned if pre-booked)
        # Here, we assume search_key is a room number that has a booking *today*
        # or a booking ID. This logic needs to be much more robust.
        found_booking = None
        booking_id = None
        room_to_checkin = None

        try: # Check if it's a booking ID
            bid = int(search_key)
            if bid in bookings_data:
                 found_booking = bookings_data[bid]
                 booking_id = bid
                 room_to_checkin = found_booking['room']
        except ValueError: # Assume it's a room number
            room_to_checkin = search_key
            # Find booking associated with this room for today (complex logic needed)
            # Simple check: if room exists and is available, maybe allow walk-in?
            if room_to_checkin in rooms_data and rooms_data[room_to_checkin]['status'] == 'Available':
                 if messagebox.askyesno("Walk-in?", f"Room {room_to_checkin} is available. Proceed with walk-in check-in?"):
                     # Trigger booking process or a simplified walk-in form
                     self.controller.update_status("Walk-in selected. Redirecting to booking...")
                     self.controller.show_frame("BookingFrame") # Example redirect
                     return
                 else:
                     return # Cancelled walk-in
            else:
                 # Find if there's a booking for this room to check in today
                 # This requires date comparison - skipping for simplicity
                 messagebox.showinfo("Info", f"Check-in logic for room {room_to_checkin} needs implementing (checking bookings).")
                 return


        if room_to_checkin and room_to_checkin in rooms_data:
            if rooms_data[room_to_checkin]['status'] == 'Occupied':
                messagebox.showerror("Check-in Error", f"Room {room_to_checkin} is already occupied.")
                return
            if rooms_data[room_to_checkin]['status'] == 'Cleaning':
                messagebox.showwarning("Check-in Warning", f"Room {room_to_checkin} is marked for cleaning. Check status before proceeding.")
                # Optionally ask if user wants to proceed anyway

            print(f"Checking in Room {room_to_checkin} (Booking ID: {booking_id}) (Placeholder)")
            rooms_data[room_to_checkin]['status'] = 'Occupied'
            guest_name = guests_data[found_booking['guest_id']]['name'] if found_booking else "Unknown"
            messagebox.showinfo("Check-in Complete", f"Guest {guest_name} checked into Room {room_to_checkin}.")
            self.controller.update_status(f"Room {room_to_checkin} checked in.")
            self.search_var.set("") # Clear search
        else:
            messagebox.showerror("Check-in Error", f"Could not find booking or room for: {search_key}")
        # --- End Placeholder ---
        # Refresh relevant views if needed (e.g., room list)
        if self.controller.frames.get("RoomManagementFrame"):
            self.controller.frames["RoomManagementFrame"].refresh_data()


    def perform_checkout(self):
        """Placeholder: Performs check-out based on Room Number."""
        room_no = self.search_var.get()
        if not room_no:
            messagebox.showerror("Input Error", "Please enter the Room Number to check out.")
            return

        # --- Actual Logic Placeholder ---
        if room_no in rooms_data:
            if rooms_data[room_no]['status'] != 'Occupied':
                messagebox.showerror("Check-out Error", f"Room {room_no} is not currently occupied.")
                return

            # Find associated booking (needed for billing, guest info)
            # Simple approach: find last booking ending recently for this room
            booking_info = "Unknown Booking" # Placeholder
            guest_name = "Unknown Guest"
            for bid, bdata in bookings_data.items():
                if bdata['room'] == room_no: # Simplistic matching
                    booking_info = f"Booking ID {bid}"
                    guest_name = guests_data[bdata['guest_id']]['name']
                    # In reality, you'd check if *this* booking corresponds to the current occupancy

            print(f"Checking out Room {room_no} ({booking_info}) (Placeholder)")
            # Typically, mark room for cleaning after checkout
            rooms_data[room_no]['status'] = 'Cleaning'
            messagebox.showinfo("Check-out Complete", f"Room {room_no} ({guest_name}) checked out.\nRoom status set to Cleaning.")
            self.controller.update_status(f"Room {room_no} checked out.")
            self.search_var.set("") # Clear search
        else:
            messagebox.showerror("Check-out Error", f"Room {room_no} not found.")
        # --- End Placeholder ---
        # Refresh relevant views if needed
        if self.controller.frames.get("RoomManagementFrame"):
            self.controller.frames["RoomManagementFrame"].refresh_data()


# --- Main Execution ---
if __name__ == "__main__":
    app = HotelApp()
    app.mainloop()