#hello anh em 
import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error

class LoginPage:
    def __init__(self, root):
        self.root = root
        self.root.title("Login Page")

        self.create_widgets()

    def create_widgets(self):
        # Username Label and Entry
        username_label = tk.Label(self.root, text="Username:")
        username_label.pack(pady=10)
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack(pady=10)

        # Password Label and Entry (assuming a simple password for this example)
        password_label = tk.Label(self.root, text="Password:")
        password_label.pack(pady=10)
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack(pady=10)

        # Login Button
        login_button = ttk.Button(self.root, text="Login", command=self.login)
        login_button.pack(pady=10)

        # New User Button
        new_user_button = ttk.Button(self.root, text="New User", command=self.new_user)
        new_user_button.pack(pady=10)

    def login(self):
        # Perform authentication against the 'users' table
        username = self.username_entry.get()
        password = self.password_entry.get()

        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="root",
                database="logi"
            )
            if connection.is_connected():
                cursor = connection.cursor(dictionary=True)
                query = "SELECT * FROM users WHERE username = %s AND passwords = %s"
                cursor.execute(query, (username, password))
                user = cursor.fetchone()

                if user:
                    self.root.destroy()  # Close the login window

                    if user['roles'] == 'admin':
                        admin_root = tk.Tk()
                        admin_page = AdminPage(admin_root, username)
                        admin_root.mainloop()
                    elif user['roles'] == 'customer':
                        customer_root = tk.Tk()
                        customer_page = CustomerPage(customer_root, username)
                        customer_root.mainloop()
                else:
                    messagebox.showerror("Login Failed", "Invalid username or password")

        except Error as e:
            print("Error connecting to MySQL database:", e)
            messagebox.showerror("Error", "Error connecting to the database")

    def new_user(self):
        # Open the NewUserPage to create a new user
        new_user_root = tk.Tk()
        new_user_page = NewUserPage(new_user_root)
        new_user_root.mainloop()

class AdminPage:
    def __init__(self, root, username):
        self.root = root
        self.root.title("Admin Page")
        self.username = username

        # Connect to MySQL database
        self.connection = self.connect_to_database()

        # Create GUI components
        self.action_var = tk.StringVar()  # Define action_var as an instance variable
        self.create_widgets()

    def connect_to_database(self):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="root",
                database="logi"
            )
            if connection.is_connected():
                print("Connected to MySQL database")
                return connection
        except Error as e:
            print("Error connecting to MySQL database:", e)

    def create_widgets(self):
        # Display Table Button
        display_button = ttk.Button(self.root, text="Display Tables", command=self.display_tables)
        display_button.pack(pady=10)

        # Update Database Button
        update_button = ttk.Button(self.root, text="Update Database", command=self.update_database)
        update_button.pack(pady=10)

        # Display welcome message
        welcome_label = tk.Label(self.root, text=f"Welcome, {self.username} (Admin)")
        welcome_label.pack(pady=10)

    def display_tables(self):
        # Create a new window for displaying tables
        display_window = tk.Toplevel(self.root)
        display_window.title("Display Tables")

        # Create a notebook (tabs)
        notebook = ttk.Notebook(display_window)

        # Tab for user1 table
        user1_tab = ttk.Frame(notebook)
        notebook.add(user1_tab, text="User1 Table")
        self.display_table(user1_tab, "user1", ["ID", "Username", "Phone Number", "Email", "Age"])

        # Tab for parking_data table
        parking_data_tab = ttk.Frame(notebook)
        notebook.add(parking_data_tab, text="Parking Data Table")
        self.display_table(parking_data_tab, "parking_data", ["ID", "Vehicle Type", "Vehicle No", "Company Name", "Location", "Time Slot", "Duration", "Total Amount", "Payment Method"])

        notebook.pack(expand=True, fill="both")

    def display_table(self, tab, table_name, columns):
        # Treeview for displaying the table
        tree = ttk.Treeview(tab)
        tree["columns"] = columns

        # Configure columns
        for col in tree["columns"]:
            tree.column(col, anchor=tk.CENTER, width=100)

        # Add headings
        for col in tree["columns"]:
            tree.heading(col, text=col)

        # Fetch data from the table
        query = f"SELECT * FROM {table_name}"
        rows = self.execute_query(query)

        if rows is not None:
            # Insert data into the Treeview
            for row in rows:
                tree.insert("", "end", values=row)

            tree.pack(expand=True, fill="both")

    def execute_query(self, query):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            cursor.close()
            return rows
        except Error as e:
            print("Error executing query:", e)
            messagebox.showerror("Error", "Error executing query")
            return None

    def update_database(self):
        # Create a new window for updating the database
        update_window = tk.Toplevel(self.root)
        update_window.title("Update Database")

        # Combo box for choosing the table to update
        update_table_option = tk.StringVar(update_window)
        update_table_option.set("Choose Table to Update")
        update_table_option_menu = tk.OptionMenu(update_window, update_table_option, "user1", "parking_data")
        update_table_option_menu.grid(row=0, column=0, columnspan=2, pady=10)

        # Button to proceed to update ID, column, and new data
        proceed_button = ttk.Button(update_window, text="Proceed", command=lambda: self.update_data(update_window, update_table_option.get()))
        proceed_button.grid(row=1, column=0, columnspan=2, pady=10)

    def update_data(self, update_window, table_name):
        update_window.destroy()  # Close the current window

        # Create a new window for updating data
        update_data_window = tk.Toplevel(self.root)
        update_data_window.title("Update Data")

        # Get the column names for the selected table
        columns = self.get_columns(table_name)

        # Combo box for choosing the ID
        id_label = tk.Label(update_data_window, text="Choose ID:")
        id_label.grid(row=0, column=0)
        id_var = tk.IntVar()
        id_combo = ttk.Combobox(update_data_window, textvariable=id_var)
        id_combo["values"] = self.get_ids(table_name)
        id_combo.grid(row=0, column=1)

        # Combo box for choosing the column
        column_label = tk.Label(update_data_window, text="Choose Column:")
        column_label.grid(row=1, column=0)
        column_var = tk.StringVar()
        column_combo = ttk.Combobox(update_data_window, textvariable=column_var)
        column_combo["values"] = columns
        column_combo.grid(row=1, column=1)

        # Entry widget for new data
        new_data_label = tk.Label(update_data_window, text="New Data:")
        new_data_label.grid(row=2, column=0)
        new_data_entry = tk.Entry(update_data_window)
        new_data_entry.grid(row=2, column=1)

        # Button to perform the update action
        action_button = ttk.Button(update_data_window, text="Perform Update",
                                   command=lambda: self.perform_action("update", table_name, id_var.get(), column_var.get(), new_data_entry.get()))
        action_button.grid(row=3, column=0, columnspan=2, pady=10)

    def get_columns(self, table_name):
        # Function to get the column names of a table
        cursor = self.connection.cursor()
        cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        columns = [column[0] for column in cursor.fetchall()]
        cursor.close()
        return columns

    def get_ids(self, table_name):
        # Function to get the IDs of a table
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT id FROM {table_name}")
        ids = [id[0] for id in cursor.fetchall()]
        cursor.close()
        return ids

    def perform_action(self, action, table_name, data_id, column, new_data):
        # Function to perform the chosen action (Insert, Delete, or Update)
        cursor = self.connection.cursor()

        try:
            if action == "update":
                # Update data in the specified column
                query = f"UPDATE {table_name} SET {column} = %s WHERE id = %s"
                cursor.execute(query, (new_data, data_id))
                self.connection.commit()
                print("Data updated successfully.")
            else:
                print("Invalid action selected.")
                messagebox.showerror("Error", "Invalid action selected.")
        except Error as e:
            print("Error updating data:", e)
            messagebox.showerror("Error", "Error updating data.")

class CustomerPage:
    def __init__(self, root, username):
        self.root = root
        self.root.title("Customer Page")
        self.username = username

        # Create GUI components for customer page
        self.create_widgets()

    def create_widgets(self):
        # Display welcome message for customer
        welcome_label = tk.Label(self.root, text=f"Welcome, {self.username} (Customer)")
        welcome_label.pack(pady=10)

        # Add customer-specific widgets as needed

class NewUserPage:
    def __init__(self, root):
        self.root = root
        self.root.title("New User Page")

        self.create_widgets()

    def create_widgets(self):
        # Username Label and Entry
        username_label = tk.Label(self.root, text="Username:")
        username_label.pack(pady=10)
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack(pady=10)

        # Password Label and Entry (assuming a simple password for this example)
        password_label = tk.Label(self.root, text="Password:")
        password_label.pack(pady=10)
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack(pady=10)

        # Role Label and ComboBox
        role_label = tk.Label(self.root, text="Role:")
        role_label.pack(pady=10)
        self.role_var = tk.StringVar()
        role_combobox = ttk.Combobox(self.root, textvariable=self.role_var, values=["admin", "customer"])
        role_combobox.pack(pady=10)

        # Create User Button
        create_user_button = ttk.Button(self.root, text="Create User", command=self.create_user)
        create_user_button.pack(pady=10)

    def create_user(self):
        # Get user data from the form
        username = self.username_entry.get()
        password = self.password_entry.get()
        role = self.role_var.get()

        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Gaurav@24",
                database="logi"
            )
            if connection.is_connected():
                cursor = connection.cursor()
                query = "INSERT INTO users (username, passwords, roles) VALUES (%s, %s, %s)"
                cursor.execute(query, (username, password, role))
                connection.commit()
                messagebox.showinfo("User Created", "User created successfully.")
                self.root.destroy()  # Close the new user window
        except Error as e:
            print("Error connecting to MySQL database:", e)
            messagebox.showerror("Error", "Error connecting to the database")

def main():
    root = tk.Tk()
    login_page = LoginPage(root)
    root.mainloop()

if __name__ == "__main__":
    main()
