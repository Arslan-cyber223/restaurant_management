"""
Restaurant Management System - Spice Haven
A complete desktop application for restaurant management
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import mysql.connector
from mysql.connector import Error
import datetime
from PIL import Image, ImageTk
import json
import os

class DatabaseManager:
    """Handles all database operations"""
    
    def __init__(self):
        self.host = "localhost"
        self.user = "root"
        self.password = "password"  # Set your MySQL password
        self.database = "spice_haven_db"
        self.connection = None
        
    def create_database(self):
        """Automatically creates database and tables if they don't exist"""
        try:
            # Connect without database
            conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            cursor = conn.cursor()
            
            # Create database
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            print(f"Database '{self.database}' created successfully!")
            
            # Use the database
            cursor.execute(f"USE {self.database}")
            
            # Create tables
            tables = {
                'menu_items': """
                    CREATE TABLE IF NOT EXISTS menu_items (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        category VARCHAR(50) NOT NULL,
                        price DECIMAL(10, 2) NOT NULL,
                        description TEXT,
                        spice_level VARCHAR(20),
                        food_type VARCHAR(20),
                        image_path VARCHAR(255),
                        available BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """,
                'orders': """
                    CREATE TABLE IF NOT EXISTS orders (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        customer_name VARCHAR(100) NOT NULL,
                        customer_phone VARCHAR(15) NOT NULL,
                        table_number INT,
                        order_type VARCHAR(20),
                        total_amount DECIMAL(10, 2) NOT NULL,
                        status VARCHAR(20) DEFAULT 'Pending',
                        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        special_instructions TEXT
                    )
                """,
                'order_items': """
                    CREATE TABLE IF NOT EXISTS order_items (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        order_id INT NOT NULL,
                        menu_item_id INT NOT NULL,
                        quantity INT NOT NULL,
                        price DECIMAL(10, 2) NOT NULL,
                        FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
                        FOREIGN KEY (menu_item_id) REFERENCES menu_items(id)
                    )
                """,
                'reservations': """
                    CREATE TABLE IF NOT EXISTS reservations (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        customer_name VARCHAR(100) NOT NULL,
                        customer_phone VARCHAR(15) NOT NULL,
                        customer_email VARCHAR(100),
                        reservation_date DATE NOT NULL,
                        reservation_time TIME NOT NULL,
                        num_guests INT NOT NULL,
                        table_number INT,
                        status VARCHAR(20) DEFAULT 'Confirmed',
                        special_requests TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """,
                'staff': """
                    CREATE TABLE IF NOT EXISTS staff (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        role VARCHAR(50) NOT NULL,
                        phone VARCHAR(15),
                        email VARCHAR(100),
                        salary DECIMAL(10, 2),
                        join_date DATE,
                        photo_path VARCHAR(255)
                    )
                """,
                'customers': """
                    CREATE TABLE IF NOT EXISTS customers (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        phone VARCHAR(15) UNIQUE NOT NULL,
                        email VARCHAR(100),
                        address TEXT,
                        total_orders INT DEFAULT 0,
                        total_spent DECIMAL(10, 2) DEFAULT 0.00,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """,
                'feedback': """
                    CREATE TABLE IF NOT EXISTS feedback (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        customer_name VARCHAR(100) NOT NULL,
                        rating INT CHECK (rating BETWEEN 1 AND 5),
                        comment TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
            }
            
            for table_name, table_sql in tables.items():
                cursor.execute(table_sql)
                print(f"Table '{table_name}' created successfully!")
            
            # Insert sample data
            self.insert_sample_data(cursor)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return True
            
        except Error as e:
            print(f"Error creating database: {e}")
            return False
    
    def insert_sample_data(self, cursor):
        """Insert sample menu items and staff"""
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM menu_items")
        if cursor.fetchone()[0] > 0:
            return
        
        # Sample menu items
        menu_items = [
            ('Litti Chokha', 'Starters', 120.00, 'Traditional Bihari roasted wheat balls with mashed vegetables', 'Medium', 'Veg'),
            ('Sattu Paratha', 'Starters', 80.00, 'Stuffed flatbread with roasted gram flour', 'Mild', 'Veg'),
            ('Chicken Biryani', 'Biryanis', 280.00, 'Aromatic basmati rice with tender chicken', 'Hot', 'Non-Veg'),
            ('Veg Biryani', 'Biryanis', 200.00, 'Fragrant rice with mixed vegetables', 'Medium', 'Veg'),
            ('Paneer Tikka', 'Starters', 220.00, 'Grilled cottage cheese with spices', 'Medium', 'Veg'),
            ('Mutton Curry', 'Mains', 350.00, 'Slow-cooked mutton in rich gravy', 'Hot', 'Non-Veg'),
            ('Dal Panchmel', 'Mains', 150.00, 'Five lentil curry with aromatic spices', 'Mild', 'Veg'),
            ('Fish Curry', 'Mains', 300.00, 'Fresh fish in tangy mustard gravy', 'Hot', 'Non-Veg'),
            ('Gulab Jamun', 'Desserts', 80.00, 'Sweet milk dumplings in sugar syrup', 'Mild', 'Veg'),
            ('Rasmalai', 'Desserts', 100.00, 'Cottage cheese patties in sweet milk', 'Mild', 'Veg'),
            ('Mango Lassi', 'Drinks', 60.00, 'Refreshing yogurt drink with mango', 'Mild', 'Veg'),
            ('Masala Chai', 'Drinks', 30.00, 'Spiced Indian tea', 'Mild', 'Veg'),
            ('Tandoori Chicken', 'Starters', 320.00, 'Chicken marinated in yogurt and spices', 'Hot', 'Non-Veg'),
            ('Samosa', 'Starters', 40.00, 'Crispy pastry with potato filling', 'Medium', 'Veg'),
            ('Butter Chicken', 'Mains', 320.00, 'Creamy tomato-based chicken curry', 'Medium', 'Non-Veg')
        ]
        
        cursor.executemany(
            """INSERT INTO menu_items (name, category, price, description, spice_level, food_type) 
               VALUES (%s, %s, %s, %s, %s, %s)""",
            menu_items
        )
        
        # Sample staff
        staff_members = [
            ('Rajesh Kumar', 'Head Chef', '9876543210', 'rajesh@spicehaven.com', 45000.00, '2020-01-15'),
            ('Priya Singh', 'Manager', '9876543211', 'priya@spicehaven.com', 40000.00, '2020-03-01'),
            ('Amit Patel', 'Sous Chef', '9876543212', 'amit@spicehaven.com', 35000.00, '2021-06-10'),
            ('Sneha Sharma', 'Waiter', '9876543213', 'sneha@spicehaven.com', 20000.00, '2022-01-05')
        ]
        
        cursor.executemany(
            """INSERT INTO staff (name, role, phone, email, salary, join_date) 
               VALUES (%s, %s, %s, %s, %s, %s)""",
            staff_members
        )
        
        print("Sample data inserted successfully!")
    
    def connect(self):
        """Connect to the database"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            return self.connection
        except Error as e:
            messagebox.showerror("Connection Error", f"Error connecting to database: {e}")
            return None
    
    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()


class RestaurantManagementSystem:
    """Main application class"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Spice Haven - Restaurant Management System")
        self.root.geometry("1400x800")
        self.root.state('zoomed')  # Maximize window
        
        # Color scheme - Warm Indian restaurant theme
        self.colors = {
            'primary': '#D84315',      # Deep Orange
            'secondary': '#FFA726',    # Light Orange
            'accent': '#FFD54F',       # Gold
            'bg': '#FFF8E1',          # Cream
            'card_bg': '#FFFFFF',     # White
            'text': '#37474F',        # Dark Blue Grey
            'success': '#66BB6A',     # Green
            'danger': '#EF5350'       # Red
        }
        
        # Configure root background
        self.root.configure(bg=self.colors['bg'])
        
        # Initialize database
        self.db = DatabaseManager()
        if not self.db.create_database():
            messagebox.showerror("Error", "Failed to initialize database!")
            return
        
        # Cart for current order
        self.cart = []
        self.cart_total = 0.0
        
        # Create UI
        self.create_styles()
        self.create_header()
        self.create_sidebar()
        self.create_main_content()
        
        # Show dashboard by default
        self.show_dashboard()
    
    def create_styles(self):
        """Create custom ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('TFrame', background=self.colors['bg'])
        style.configure('Card.TFrame', background=self.colors['card_bg'], relief='raised')
        
        style.configure('TLabel', 
                       background=self.colors['bg'], 
                       foreground=self.colors['text'],
                       font=('Poppins', 10))
        
        style.configure('Header.TLabel',
                       font=('Poppins', 24, 'bold'),
                       foreground=self.colors['primary'])
        
        style.configure('Subheader.TLabel',
                       font=('Poppins', 14, 'bold'),
                       foreground=self.colors['text'])
        
        style.configure('TButton',
                       font=('Poppins', 10),
                       padding=10)
        
        style.map('TButton',
                 background=[('active', self.colors['secondary'])])
        
        # Primary button
        style.configure('Primary.TButton',
                       background=self.colors['primary'],
                       foreground='white',
                       font=('Poppins', 10, 'bold'))
        
        style.map('Primary.TButton',
                 background=[('active', self.colors['secondary'])])
    
    def create_header(self):
        """Create top header bar"""
        header = tk.Frame(self.root, bg=self.colors['primary'], height=80)
        header.pack(fill='x', side='top')
        header.pack_propagate(False)
        
        # Logo and title
        title_frame = tk.Frame(header, bg=self.colors['primary'])
        title_frame.pack(side='left', padx=30, pady=20)
        
        logo_label = tk.Label(title_frame,
                             text="🍛",
                             font=('Arial', 30),
                             bg=self.colors['primary'])
        logo_label.pack(side='left')
        
        title_label = tk.Label(title_frame,
                              text="SPICE HAVEN",
                              font=('Poppins', 24, 'bold'),
                              fg='white',
                              bg=self.colors['primary'])
        title_label.pack(side='left', padx=10)
        
        subtitle = tk.Label(title_frame,
                           text="Restaurant Management System",
                           font=('Open Sans', 10),
                           fg=self.colors['accent'],
                           bg=self.colors['primary'])
        subtitle.pack(side='left', padx=10)
        
        # Current time
        self.time_label = tk.Label(header,
                                   font=('Poppins', 12),
                                   fg='white',
                                   bg=self.colors['primary'])
        self.time_label.pack(side='right', padx=30)
        self.update_time()
    
    def update_time(self):
        """Update current time display"""
        current_time = datetime.datetime.now().strftime("%I:%M:%S %p | %d-%b-%Y")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)
    
    def create_sidebar(self):
        """Create left sidebar with navigation"""
        sidebar = tk.Frame(self.root, bg=self.colors['text'], width=250)
        sidebar.pack(fill='y', side='left')
        sidebar.pack_propagate(False)
        
        # Navigation buttons
        nav_items = [
            ("📊 Dashboard", self.show_dashboard),
            ("🍽️ Menu Management", self.show_menu_management),
            ("🛒 New Order", self.show_new_order),
            ("📋 Orders", self.show_orders),
            ("📅 Reservations", self.show_reservations),
            ("👥 Customers", self.show_customers),
            ("👨‍🍳 Staff", self.show_staff),
            ("💬 Feedback", self.show_feedback),
            ("📈 Reports", self.show_reports)
        ]
        
        for text, command in nav_items:
            btn = tk.Button(sidebar,
                           text=text,
                           font=('Poppins', 11),
                           bg=self.colors['text'],
                           fg='white',
                           activebackground=self.colors['primary'],
                           activeforeground='white',
                           bd=0,
                           pady=15,
                           cursor='hand2',
                           anchor='w',
                           padx=20,
                           command=command)
            btn.pack(fill='x', pady=2)
            
            # Hover effect
            btn.bind('<Enter>', lambda e, b=btn: b.config(bg=self.colors['primary']))
            btn.bind('<Leave>', lambda e, b=btn: b.config(bg=self.colors['text']))
    
    def create_main_content(self):
        """Create main content area"""
        self.main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        self.main_frame.pack(fill='both', expand=True, side='right')
    
    def clear_main_frame(self):
        """Clear all widgets from main frame"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def show_dashboard(self):
        """Display dashboard with statistics"""
        self.clear_main_frame()
        
        # Title
        title = tk.Label(self.main_frame,
                        text="Dashboard",
                        font=('Poppins', 24, 'bold'),
                        fg=self.colors['primary'],
                        bg=self.colors['bg'])
        title.pack(pady=20, padx=30, anchor='w')
        
        # Stats cards frame
        stats_frame = tk.Frame(self.main_frame, bg=self.colors['bg'])
        stats_frame.pack(fill='x', padx=30, pady=10)
        
        # Get statistics from database
        conn = self.db.connect()
        if conn:
            cursor = conn.cursor()
            
            # Total menu items
            cursor.execute("SELECT COUNT(*) FROM menu_items WHERE available = TRUE")
            total_dishes = cursor.fetchone()[0]
            
            # Today's orders
            cursor.execute("""SELECT COUNT(*) FROM orders 
                            WHERE DATE(order_date) = CURDATE()""")
            today_orders = cursor.fetchone()[0]
            
            # Total customers
            cursor.execute("SELECT COUNT(*) FROM customers")
            total_customers = cursor.fetchone()[0]
            
            # Today's revenue
            cursor.execute("""SELECT COALESCE(SUM(total_amount), 0) FROM orders 
                            WHERE DATE(order_date) = CURDATE()""")
            today_revenue = cursor.fetchone()[0]
            
            cursor.close()
            self.db.disconnect()
            
            # Create stat cards
            stats = [
                ("Total Dishes", total_dishes, "🍽️", self.colors['primary']),
                ("Today's Orders", today_orders, "📋", self.colors['secondary']),
                ("Total Customers", total_customers, "👥", self.colors['success']),
                ("Today's Revenue", f"₹{today_revenue:.2f}", "💰", self.colors['accent'])
            ]
            
            for i, (label, value, icon, color) in enumerate(stats):
                self.create_stat_card(stats_frame, label, value, icon, color, i)
        
        # Recent activity
        activity_frame = tk.Frame(self.main_frame, bg=self.colors['card_bg'], relief='raised', bd=1)
        activity_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        activity_title = tk.Label(activity_frame,
                                 text="Recent Orders",
                                 font=('Poppins', 16, 'bold'),
                                 bg=self.colors['card_bg'],
                                 fg=self.colors['text'])
        activity_title.pack(pady=15, padx=20, anchor='w')
        
        # Recent orders list
        self.show_recent_orders(activity_frame)
    
    def create_stat_card(self, parent, label, value, icon, color, index):
        """Create a statistics card"""
        card = tk.Frame(parent, bg=self.colors['card_bg'], relief='raised', bd=2)
        card.grid(row=0, column=index, padx=10, pady=10, sticky='nsew')
        parent.grid_columnconfigure(index, weight=1)
        
        # Icon
        icon_label = tk.Label(card,
                             text=icon,
                             font=('Arial', 40),
                             bg=self.colors['card_bg'])
        icon_label.pack(pady=(20, 10))
        
        # Value
        value_label = tk.Label(card,
                              text=str(value),
                              font=('Poppins', 24, 'bold'),
                              fg=color,
                              bg=self.colors['card_bg'])
        value_label.pack()
        
        # Label
        text_label = tk.Label(card,
                             text=label,
                             font=('Open Sans', 11),
                             fg=self.colors['text'],
                             bg=self.colors['card_bg'])
        text_label.pack(pady=(5, 20))
    
    def show_recent_orders(self, parent):
        """Show recent orders in a treeview"""
        # Create Treeview
        columns = ('Order ID', 'Customer', 'Amount', 'Status', 'Date')
        tree = ttk.Treeview(parent, columns=columns, show='headings', height=10)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(parent, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Fetch recent orders
        conn = self.db.connect()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""SELECT id, customer_name, total_amount, status, order_date 
                            FROM orders ORDER BY order_date DESC LIMIT 10""")
            
            for row in cursor.fetchall():
                order_id, name, amount, status, date = row
                tree.insert('', 'end', values=(
                    f'#{order_id}',
                    name,
                    f'₹{amount:.2f}',
                    status,
                    date.strftime('%d-%m-%Y %I:%M %p')
                ))
            
            cursor.close()
            self.db.disconnect()
        
        tree.pack(side='left', fill='both', expand=True, padx=20, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10, padx=(0, 20))
    
    def show_menu_management(self):
        """Show menu management interface"""
        self.clear_main_frame()
        
        title = tk.Label(self.main_frame,
                        text="Menu Management",
                        font=('Poppins', 24, 'bold'),
                        fg=self.colors['primary'],
                        bg=self.colors['bg'])
        title.pack(pady=20, padx=30, anchor='w')
        
        # Action buttons
        btn_frame = tk.Frame(self.main_frame, bg=self.colors['bg'])
        btn_frame.pack(fill='x', padx=30, pady=10)
        
        add_btn = tk.Button(btn_frame,
                           text="➕ Add New Dish",
                           font=('Poppins', 11, 'bold'),
                           bg=self.colors['primary'],
                           fg='white',
                           cursor='hand2',
                           padx=20,
                           pady=10,
                           command=self.add_menu_item_dialog)
        add_btn.pack(side='left', padx=5)
        
        # Menu items list
        list_frame = tk.Frame(self.main_frame, bg=self.colors['card_bg'], relief='raised', bd=1)
        list_frame.pack(fill='both', expand=True, padx=30, pady=10)
        
        # Treeview
        columns = ('ID', 'Name', 'Category', 'Price', 'Spice', 'Type', 'Available')
        tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Fetch menu items
        conn = self.db.connect()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""SELECT id, name, category, price, spice_level, food_type, available 
                            FROM menu_items ORDER BY category, name""")
            
            for row in cursor.fetchall():
                item_id, name, cat, price, spice, ftype, avail = row
                tree.insert('', 'end', values=(
                    item_id,
                    name,
                    cat,
                    f'₹{price:.2f}',
                    spice or '-',
                    ftype or '-',
                    '✓ Yes' if avail else '✗ No'
                ))
            
            cursor.close()
            self.db.disconnect()
        
        tree.pack(side='left', fill='both', expand=True, padx=20, pady=20)
        scrollbar.pack(side='right', fill='y', pady=20, padx=(0, 20))
        
        # Store tree reference for later use
        self.menu_tree = tree
    
    def add_menu_item_dialog(self):
        """Dialog to add new menu item"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Menu Item")
        dialog.geometry("500x600")
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Form fields
        fields = [
            ("Name:", "name"),
            ("Category:", "category"),
            ("Price (₹):", "price"),
            ("Description:", "description"),
            ("Spice Level:", "spice"),
            ("Food Type:", "food_type")
        ]
        
        entries = {}
        
        for i, (label_text, field_name) in enumerate(fields):
            tk.Label(dialog, text=label_text, font=('Poppins', 11),
                    bg=self.colors['bg']).grid(row=i, column=0, padx=20, pady=10, sticky='w')
            
            if field_name == "category":
                entry = ttk.Combobox(dialog, values=['Starters', 'Mains', 'Biryanis', 'Desserts', 'Drinks'],
                                    font=('Open Sans', 10), width=30)
            elif field_name == "spice":
                entry = ttk.Combobox(dialog, values=['Mild', 'Medium', 'Hot'],
                                    font=('Open Sans', 10), width=30)
            elif field_name == "food_type":
                entry = ttk.Combobox(dialog, values=['Veg', 'Non-Veg', 'Vegan'],
                                    font=('Open Sans', 10), width=30)
            elif field_name == "description":
                entry = tk.Text(dialog, height=4, width=32, font=('Open Sans', 10))
            else:
                entry = tk.Entry(dialog, font=('Open Sans', 10), width=32)
            
            entry.grid(row=i, column=1, padx=20, pady=10)
            entries[field_name] = entry
        
        def save_item():
            # Get values
            name = entries['name'].get().strip()
            category = entries['category'].get().strip()
            price = entries['price'].get().strip()
            spice = entries['spice'].get().strip()
            food_type = entries['food_type'].get().strip()
            desc = entries['description'].get('1.0', 'end').strip()
            
            # Validate
            if not name or not category or not price:
                messagebox.showerror("Error", "Please fill all required fields!")
                return
            
            try:
                price = float(price)
            except ValueError:
                messagebox.showerror("Error", "Invalid price!")
                return
            
            # Insert into database
            conn = self.db.connect()
            if conn:
                cursor = conn.cursor()
                cursor.execute("""INSERT INTO menu_items 
                                (name, category, price, description, spice_level, food_type) 
                                VALUES (%s, %s, %s, %s, %s, %s)""",
                             (name, category, price, desc, spice, food_type))
                conn.commit()
                cursor.close()
                self.db.disconnect()
                
                messagebox.showinfo("Success", "Menu item added successfully!")
                dialog.destroy()
                self.show_menu_management()  # Refresh
        
        # Save button
        save_btn = tk.Button(dialog,
                            text="💾 Save Item",
                            font=('Poppins', 11, 'bold'),
                            bg=self.colors['primary'],
                            fg='white',
                            cursor='hand2',
                            padx=20,
                            pady=10,
                            command=save_item)
        save_btn.grid(row=len(fields), column=0, columnspan=2, pady=30)
    
    def show_new_order(self):
        """Show new order interface with menu and cart"""
        self.clear_main_frame()
        self.cart = []
        self.cart_total = 0.0
        
        title = tk.Label(self.main_frame,
                        text="New Order",
                        font=('Poppins', 24, 'bold'),
                        fg=self.colors['primary'],
                        bg=self.colors['bg'])
        title.pack(pady=20, padx=30, anchor='w')
        
        # Main container
        container = tk.Frame(self.main_frame, bg=self.colors['bg'])
        container.pack(fill='both', expand=True, padx=30)
        
        # Left: Menu items
        menu_frame = tk.Frame(container, bg=self.colors['card_bg'], relief='raised', bd=1)
        menu_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        tk.Label(menu_frame, text="Menu Items", font=('Poppins', 16, 'bold'),
                bg=self.colors['card_bg']).pack(pady=15, padx=20, anchor='w')
        
        # Category filter
        filter_frame = tk.Frame(menu_frame, bg=self.colors['card_bg'])
        filter_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(filter_frame, text="Filter:", font=('Poppins', 10),
                bg=self.colors['card_bg']).pack(side='left', padx=5)
        
        self.category_filter = ttk.Combobox(filter_frame, 
                                           values=['All', 'Starters', 'Mains', 'Biryanis', 'Desserts', 'Drinks'],
                                           

# Continuation of show_new_order method:
                                           width=20)
        self.category_filter.set('All')
        self.category_filter.pack(side='left', padx=5)
        self.category_filter.bind('<<ComboboxSelected>>', lambda e: self.load_menu_items())
        
        # Scrollable menu items
        menu_canvas = tk.Canvas(menu_frame, bg=self.colors['card_bg'], highlightthickness=0)
        menu_scrollbar = ttk.Scrollbar(menu_frame, orient='vertical', command=menu_canvas.yview)
        self.menu_items_frame = tk.Frame(menu_canvas, bg=self.colors['card_bg'])
        
        self.menu_items_frame.bind(
            '<Configure>',
            lambda e: menu_canvas.configure(scrollregion=menu_canvas.bbox('all'))
        )
        
        menu_canvas.create_window((0, 0), window=self.menu_items_frame, anchor='nw')
        menu_canvas.configure(yscrollcommand=menu_scrollbar.set)
        
        menu_canvas.pack(side='left', fill='both', expand=True, padx=20, pady=10)
        menu_scrollbar.pack(side='right', fill='y', pady=10, padx=(0, 20))
        
        # Right: Cart
        cart_frame = tk.Frame(container, bg=self.colors['card_bg'], relief='raised', bd=1, width=400)
        cart_frame.pack(side='right', fill='both', padx=(10, 0))
        cart_frame.pack_propagate(False)
        
        tk.Label(cart_frame, text="Cart", font=('Poppins', 16, 'bold'),
                bg=self.colors['card_bg']).pack(pady=15, padx=20, anchor='w')
        
        # Cart items
        self.cart_items_frame = tk.Frame(cart_frame, bg=self.colors['card_bg'])
        self.cart_items_frame.pack(fill='both', expand=True, padx=20)
        
        # Total
        self.total_label = tk.Label(cart_frame,
                                    text="Total: ₹0.00",
                                    font=('Poppins', 18, 'bold'),
                                    fg=self.colors['primary'],
                                    bg=self.colors['card_bg'])
        self.total_label.pack(pady=15)
        
        # Checkout button
        checkout_btn = tk.Button(cart_frame,
                                text="🛒 Checkout",
                                font=('Poppins', 12, 'bold'),
                                bg=self.colors['success'],
                                fg='white',
                                cursor='hand2',
                                padx=20,
                                pady=15,
                                command=self.checkout_order)
        checkout_btn.pack(fill='x', padx=20, pady=(0, 20))
        
        # Load menu items
        self.load_menu_items()
    
    def load_menu_items(self):
        """Load menu items based on filter"""
        # Clear existing items
        for widget in self.menu_items_frame.winfo_children():
            widget.destroy()
        
        # Get filter
        category = self.category_filter.get()
        
        # Fetch from database
        conn = self.db.connect()
        if conn:
            cursor = conn.cursor(dictionary=True)
            
            if category == 'All':
                cursor.execute("""SELECT * FROM menu_items WHERE available = TRUE 
                                ORDER BY category, name""")
            else:
                cursor.execute("""SELECT * FROM menu_items WHERE available = TRUE 
                                AND category = %s ORDER BY name""", (category,))
            
            items = cursor.fetchall()
            
            for item in items:
                self.create_menu_item_card(item)
            
            cursor.close()
            self.db.disconnect()
    
    def create_menu_item_card(self, item):
        """Create a menu item card"""
        card = tk.Frame(self.menu_items_frame, bg='white', relief='solid', bd=1)
        card.pack(fill='x', pady=5)
        
        # Item name
        name_label = tk.Label(card,
                             text=item['name'],
                             font=('Poppins', 12, 'bold'),
                             bg='white',
                             fg=self.colors['text'])
        name_label.pack(anchor='w', padx=10, pady=(10, 5))
        
        # Price and category
        info_frame = tk.Frame(card, bg='white')
        info_frame.pack(fill='x', padx=10)
        
        price_label = tk.Label(info_frame,
                              text=f"₹{item['price']:.2f}",
                              font=('Poppins', 11, 'bold'),
                              bg='white',
                              fg=self.colors['primary'])
        price_label.pack(side='left')
        
        category_label = tk.Label(info_frame,
                                 text=f"• {item['category']}",
                                 font=('Open Sans', 9),
                                 bg='white',
                                 fg=self.colors['text'])
        category_label.pack(side='left', padx=5)
        
        if item['spice_level']:
            spice_label = tk.Label(info_frame,
                                  text=f"🌶️ {item['spice_level']}",
                                  font=('Open Sans', 9),
                                  bg='white')
            spice_label.pack(side='left', padx=5)
        
        # Add to cart button
        add_btn = tk.Button(card,
                           text="+ Add",
                           font=('Poppins', 9, 'bold'),
                           bg=self.colors['secondary'],
                           fg='white',
                           cursor='hand2',
                           padx=15,
                           pady=5,
                           bd=0,
                           command=lambda: self.add_to_cart(item))
        add_btn.pack(anchor='e', padx=10, pady=10)
    
    def add_to_cart(self, item):
        """Add item to cart"""
        # Check if item already in cart
        for cart_item in self.cart:
            if cart_item['id'] == item['id']:
                cart_item['quantity'] += 1
                self.update_cart_display()
                return
        
        # Add new item
        self.cart.append({
            'id': item['id'],
            'name': item['name'],
            'price': float(item['price']),
            'quantity': 1
        })
        
        self.update_cart_display()
    
    def update_cart_display(self):
        """Update cart display"""
        # Clear cart items
        for widget in self.cart_items_frame.winfo_children():
            widget.destroy()
        
        # Calculate total
        self.cart_total = sum(item['price'] * item['quantity'] for item in self.cart)
        
        if not self.cart:
            empty_label = tk.Label(self.cart_items_frame,
                                  text="Cart is empty",
                                  font=('Open Sans', 11),
                                  fg='gray',
                                  bg=self.colors['card_bg'])
            empty_label.pack(pady=50)
        else:
            for item in self.cart:
                self.create_cart_item(item)
        
        # Update total
        self.total_label.config(text=f"Total: ₹{self.cart_total:.2f}")
    
    def create_cart_item(self, item):
        """Create cart item display"""
        item_frame = tk.Frame(self.cart_items_frame, bg='white', relief='solid', bd=1)
        item_frame.pack(fill='x', pady=5)
        
        # Name
        name_label = tk.Label(item_frame,
                             text=item['name'],
                             font=('Poppins', 10, 'bold'),
                             bg='white')
        name_label.pack(anchor='w', padx=10, pady=5)
        
        # Quantity and price
        bottom_frame = tk.Frame(item_frame, bg='white')
        bottom_frame.pack(fill='x', padx=10, pady=5)
        
        # Quantity controls
        qty_frame = tk.Frame(bottom_frame, bg='white')
        qty_frame.pack(side='left')
        
        dec_btn = tk.Button(qty_frame, text="-", font=('Poppins', 10, 'bold'),
                           bg=self.colors['bg'], width=2,
                           command=lambda: self.update_quantity(item, -1))
        dec_btn.pack(side='left', padx=2)
        
        qty_label = tk.Label(qty_frame, text=str(item['quantity']),
                            font=('Poppins', 10), bg='white', width=3)
        qty_label.pack(side='left', padx=5)
        
        inc_btn = tk.Button(qty_frame, text="+", font=('Poppins', 10, 'bold'),
                           bg=self.colors['bg'], width=2,
                           command=lambda: self.update_quantity(item, 1))
        inc_btn.pack(side='left', padx=2)
        
        # Price
        price_label = tk.Label(bottom_frame,
                              text=f"₹{item['price'] * item['quantity']:.2f}",
                              font=('Poppins', 10, 'bold'),
                              fg=self.colors['primary'],
                              bg='white')
        price_label.pack(side='right')
        
        # Remove button
        remove_btn = tk.Button(bottom_frame, text="🗑️",
                              font=('Arial', 10),
                              bg='white',
                              fg=self.colors['danger'],
                              bd=0,
                              cursor='hand2',
                              command=lambda: self.remove_from_cart(item))
        remove_btn.pack(side='right', padx=10)
    
    def update_quantity(self, item, change):
        """Update item quantity"""
        item['quantity'] += change
        if item['quantity'] <= 0:
            self.cart.remove(item)
        self.update_cart_display()
    
    def remove_from_cart(self, item):
        """Remove item from cart"""
        self.cart.remove(item)
        self.update_cart_display()
    
    def checkout_order(self):
        """Checkout current order"""
        if not self.cart:
            messagebox.showwarning("Empty Cart", "Please add items to cart first!")
            return
        
        # Create checkout dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Checkout")
        dialog.geometry("400x400")
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Customer Details", font=('Poppins', 16, 'bold'),
                bg=self.colors['bg']).pack(pady=20)
        
        # Form
        form_frame = tk.Frame(dialog, bg=self.colors['bg'])
        form_frame.pack(pady=10)
        
        tk.Label(form_frame, text="Name:", font=('Poppins', 11),
                bg=self.colors['bg']).grid(row=0, column=0, padx=20, pady=10, sticky='w')
        name_entry = tk.Entry(form_frame, font=('Open Sans', 10), width=25)
        name_entry.grid(row=0, column=1, padx=20, pady=10)
        
        tk.Label(form_frame, text="Phone:", font=('Poppins', 11),
                bg=self.colors['bg']).grid(row=1, column=0, padx=20, pady=10, sticky='w')
        phone_entry = tk.Entry(form_frame, font=('Open Sans', 10), width=25)
        phone_entry.grid(row=1, column=1, padx=20, pady=10)
        
        tk.Label(form_frame, text="Table:", font=('Poppins', 11),
                bg=self.colors['bg']).grid(row=2, column=0, padx=20, pady=10, sticky='w')
        table_entry = tk.Entry(form_frame, font=('Open Sans', 10), width=25)
        table_entry.grid(row=2, column=1, padx=20, pady=10)
        
        tk.Label(form_frame, text="Type:", font=('Poppins', 11),
                bg=self.colors['bg']).grid(row=3, column=0, padx=20, pady=10, sticky='w')
        type_combo = ttk.Combobox(form_frame, values=['Dine-in', 'Takeaway', 'Delivery'], width=23)
        type_combo.set('Dine-in')
        type_combo.grid(row=3, column=1, padx=20, pady=10)
        
        def place_order():
            name = name_entry.get().strip()
            phone = phone_entry.get().strip()
            table = table_entry.get().strip()
            order_type = type_combo.get()
            
            if not name or not phone:
                messagebox.showerror("Error", "Name and phone are required!")
                return
            
            # Insert order
            conn = self.db.connect()
            if conn:
                cursor = conn.cursor()
                
                # Insert order
                cursor.execute("""INSERT INTO orders 
                                (customer_name, customer_phone, table_number, order_type, total_amount, status) 
                                VALUES (%s, %s, %s, %s, %s, %s)""",
                             (name, phone, int(table) if table else None, order_type, self.cart_total, 'Pending'))
                
                order_id = cursor.lastrowid
                
                # Insert order items
                for item in self.cart:
                    cursor.execute("""INSERT INTO order_items 
                                    (order_id, menu_item_id, quantity, price) 
                                    VALUES (%s, %s, %s, %s)""",
                                 (order_id, item['id'], item['quantity'], item['price']))
                
                conn.commit()
                cursor.close()
                self.db.disconnect()
                
                messagebox.showinfo("Success", f"Order #{order_id} placed successfully!\nTotal: ₹{self.cart_total:.2f}")
                dialog.destroy()
                self.show_new_order()  # Reset
        
        place_btn = tk.Button(dialog,
                             text="Place Order",
                             font=('Poppins', 12, 'bold'),
                             bg=self.colors['success'],
                             fg='white',
                             cursor='hand2',
                             padx=30,
                             pady=10,
                             command=place_order)
        place_btn.pack(pady=30)
    
    def show_orders(self):
        """Show all orders"""
        self.clear_main_frame()
        
        title = tk.Label(self.main_frame,
                        text="Orders Management",
                        font=('Poppins', 24, 'bold'),
                        fg=self.colors['primary'],
                        bg=self.colors['bg'])
        title.pack(pady=20, padx=30, anchor='w')
        
        # Filter
        filter_frame = tk.Frame(self.main_frame, bg=self.colors['bg'])
        filter_frame.pack(fill='x', padx=30, pady=10)
        
        tk.Label(filter_frame, text="Status:", font=('Poppins', 10),
                bg=self.colors['bg']).pack(side='left', padx=5)
        
        status_filter = ttk.Combobox(filter_frame, 
                                    values=['All', 'Pending', 'Preparing', 'Ready', 'Completed', 'Cancelled'],
                                    width=15)
        status_filter.set('All')
        status_filter.pack(side='left', padx=5)
        
        # Orders list
        list_frame = tk.Frame(self.main_frame, bg=self.colors['card_bg'], relief='raised', bd=1)
        list_frame.pack(fill='both', expand=True, padx=30, pady=10)
        
        columns = ('Order ID', 'Customer', 'Phone', 'Table', 'Type', 'Amount', 'Status', 'Date')
        tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Fetch orders
        conn = self.db.connect()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""SELECT id, customer_name, customer_phone, table_number, 
                            order_type, total_amount, status, order_date 
                            FROM orders ORDER BY order_date DESC""")
            
            for row in cursor.fetchall():
                order_id, name, phone, table, otype, amount, status, date = row
                tree.insert('', 'end', values=(
                    f'#{order_id}',
                    name,
                    phone,
                    table or '-',
                    otype,
                    f'₹{amount:.2f}',
                    status,
                    date.strftime('%d-%m-%Y %I:%M %p')
                ))
            
            cursor.close()
            self.db.disconnect()
        
        tree.pack(side='left', fill='both', expand=True, padx=20, pady=20)
        scrollbar.pack(side='right', fill='y', pady=20, padx=(0, 20))
    
    def show_reservations(self):
        """Show reservations management"""
        self.clear_main_frame()
        
        title = tk.Label(self.main_frame,
                        text="Reservations",
                        font=('Poppins', 24, 'bold'),
                        fg=self.colors['primary'],
                        bg=self.colors['bg'])
        title.pack(pady=20, padx=30, anchor='w')
        
        # Add reservation button
        btn_frame = tk.Frame(self.main_frame, bg=self.colors['bg'])
        btn_frame.pack(fill='x', padx=30, pady=10)
        
        add_btn = tk.Button(btn_frame,
                           text="➕ New Reservation",
                           font=('Poppins', 11, 'bold'),
                           bg=self.colors['primary'],
                           fg='white',
                           cursor='hand2',
                           padx=20,
                           pady=10,
                           command=self.add_reservation_dialog)
        add_btn.pack(side='left', padx=5)
        
        # Reservations list
        list_frame = tk.Frame(self.main_frame, bg=self.colors['card_bg'], relief='raised', bd=1)
        list_frame.pack(fill='both', expand=True, padx=30, pady=10)
        
        columns = ('ID', 'Customer', 'Phone', 'Date', 'Time', 'Guests', 'Table', 'Status')
        tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Fetch reservations
        conn = self.db.connect()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""SELECT id, customer_name, customer_phone, reservation_date, 
                            reservation_time, num_guests, table_number, status 
                            FROM reservations ORDER BY reservation_date DESC, reservation_time DESC""")
            
            for row in cursor.fetchall():
                res_id, name, phone, date, time, guests, table, status = row
                tree.insert('', 'end', values=(
                    f'#{res_id}',
                    name,
                    phone,
                    date.strftime('%d-%m-%Y'),
                    time.strftime('%I:%M %p'),
                    guests,
                    table or '-',
                    status
                ))
            
            cursor.close()
            self.db.disconnect()
        
        tree.pack(side='left', fill='both', expand=True, padx=20, pady=20)
        scrollbar.pack(side='right', fill='y', pady=20, padx=(0, 20))
    
    def add_reservation_dialog(self):
        """Dialog to add new reservation"""
        dialog = tk.Toplevel(self.root)
        dialog.title("New Reservation")
        dialog.geometry("450x550")
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Reservation Details", font=('Poppins', 16, 'bold'),
                bg=self.colors['bg']).pack(pady=20)
        
        form_frame = tk.Frame(dialog, bg=self.colors['bg'])
        form_frame.pack(pady=10)
        
        fields = [
            ("Name:", "name"),
            ("Phone:", "phone"),
            ("Email:", "email"),
            ("Date (YYYY-MM-DD):", "date"),
            ("Time (HH:MM):", "time"),
            ("Guests:", "guests"),
            ("Table Number:", "table")
        ]
        
        entries = {}
        
        for i, (label_text, field_name) in enumerate(fields):
            tk.Label(form_frame, text=label_text, font=('Poppins', 10),
                    bg=self.colors['bg']).grid(row=i, column=0, padx=20, pady=10, sticky='w')
            
            entry = tk.Entry(form_frame, font=('Open Sans', 10), width=25)
            entry.grid(row=i, column=1, padx=20, pady=10)
            entries[field_name] = entry
        
        def save_reservation():
            name = entries['name'].get().strip()
            phone = entries['phone'].get().strip()
            email = entries['email'].get().strip()
            date = entries['date'].get().strip()
            time = entries['time'].get().strip()
            guests = entries['guests'].get().strip()
            table = entries['table'].get().strip()
            
            if not name or not phone or not date or not time or not guests:
                messagebox.showerror("Error", "Please fill required fields!")
                return
            
            conn = self.db.connect()
            if conn:
                cursor = conn.cursor()
                cursor.execute("""INSERT INTO reservations 
                                (customer_name, customer_phone, customer_email, reservation_date, 
                                reservation_time, num_guests, table_number) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                             (name, phone, email, date, time, int(guests), int(table) if table else None))
                conn.commit()
                cursor.close()
                self.db.disconnect()
                
                messagebox.showinfo("Success", "Reservation created successfully!")
                dialog.destroy()
                self.show_reservations()
        
        save_btn = tk.Button(dialog,
                            text="💾 Save Reservation",
                            font=('Poppins', 11, 'bold'),
                            bg=self.colors['primary'],
                            fg='white',
                            cursor='hand2',
                            padx=20,
                            pady=10,
                            command=save_reservation)
        save_btn.pack(pady=30)
    
    def show_customers(self):
        """Show customer management"""
        self.clear_main_frame()
        
        title = tk.Label(self.main_frame,
                        text="Customers",
                        font=('Poppins', 24, 'bold'),
                        fg=self.colors['primary'],
                        bg=self.colors['bg'])
        title.pack(pady=20, padx=30, anchor='w')
        
        list_frame = tk.Frame(self.main_frame, bg=self.colors['card_bg'], relief='raised', bd=1)
        list_frame.pack(fill='both', expand=True, padx=30, pady=10)
        
        columns = ('ID', 'Name', 'Phone', 'Email', 'Orders', 'Total Spent', 'Joined')
        tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        conn = self.db.connect()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""SELECT id, name, phone, email, total_orders, total_spent, created_at 
                            FROM customers ORDER BY total_spent DESC""")
            
            for row in cursor.fetchall():
                cust_id, name, phone, email, orders, spent, joined = row
                tree.insert('', 'end', values=(
                    cust_id,
                    name,
                    phone,
                    email or '-',
                    orders,
                    f'₹{spent:.2f}',
                    joined.strftime('%d-%m-%Y')
                ))
            
            cursor.close()
            self.db.disconnect()
        
        tree.pack(side='left', fill='both', expand=True, padx=20, pady=20)
        scrollbar.pack(side='right', fill='y', pady=20, padx=(0, 20))
    
    def show_staff(self):
        """Show staff management"""
        self.clear_main_frame()
        
        title = tk.Label(self.main_frame,
                        text="Staff Management",
                        font=('Poppins', 24, 'bold'),
                        fg=self.colors['primary'],
                        bg=self.colors['bg'])
        title.pack(pady=20, padx=30, anchor='w')
        
        list_frame = tk.Frame(self.main_frame, bg=self.colors['card_bg'], relief='raised', bd=1)
        list_frame.pack(fill='both', expand=True, padx=30, pady=10)
        
        columns = ('ID', 'Name', 'Role', 'Phone', 'Email', 'Salary', 'Join Date')
        tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        conn = self.db.connect()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""SELECT id, name, role, phone, email, salary, join_date 
                            FROM staff ORDER BY join_date DESC""")
            
            for row in cursor.fetchall():
                staff_id, name, role, phone, email, salary, join_date = row
                tree.insert('', 'end', values=(
                    staff_id,
                    name,
                    role,
                    phone or '-',
                    email or '-',
                    f'₹{salary:.2f}' if salary else '-',
                    join_date.strftime('%d-%m-%Y') if join_date else '-'
                ))
            
            cursor.close()
            self.db.disconnect()
        
        tree.pack(side='left', fill='both', expand=True, padx=20, pady=20)
        scrollbar.pack(side='right', fill='y', pady=20, padx=(0, 20))
    
    def show_feedback(self):
        """Show customer feedback"""
        self.clear_main_frame()
        
        title = tk.Label(self.main_frame,
                        text="Customer Feedback",
                        font=('Poppins', 24, 'bold'),
                        fg=self.colors['primary'],
                        bg=self.colors['bg'])
        title.pack(pady=20, padx=30, anchor='w')
        
        list_frame = tk.Frame(self.main_frame, bg=self.colors['card_bg'], relief='raised', bd=1)
        list_frame.pack(fill='both', expand=True, padx=30, pady=10)
        
        columns = ('ID', 'Customer', 'Rating', 'Comment', 'Date')
        tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=20)
        
        tree.column('ID', width=50)
        tree.column('Customer', width=150)
        tree.column('Rating', width=80)
        tree.column('Comment', width=400)
        tree.column('Date', width=150)
        
        for col in columns:
            tree.heading(col, text=col)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        conn = self.db.connect()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""SELECT id, customer_name, rating, comment, created_at 
                            FROM feedback ORDER BY created_at DESC""")
            
            for row in cursor.fetchall():
                fb_id, name, rating, comment, date = row
                stars = '⭐' * rating
                tree.insert('', 'end', values=(
                    fb_id,
                    name,
                    stars,
                    comment or '-',
                    date.strftime('%d-%m-%Y %I:%M %p')
                ))
            
            cursor.close()
            self.db.disconnect()
        
        """
Restaurant Management System - Part 3 (Final part)
Add this code to complete the application
"""

# Continuation of show_feedback method:
        tree.pack(side='left', fill='both', expand=True, padx=20, pady=20)
        scrollbar.pack(side='right', fill='y', pady=20, padx=(0, 20))
    
    def show_reports(self):
        """Show reports and analytics"""
        self.clear_main_frame()
        
        title = tk.Label(self.main_frame,
                        text="Reports & Analytics",
                        font=('Poppins', 24, 'bold'),
                        fg=self.colors['primary'],
                        bg=self.colors['bg'])
        title.pack(pady=20, padx=30, anchor='w')
        
        # Reports container
        reports_container = tk.Frame(self.main_frame, bg=self.colors['bg'])
        reports_container.pack(fill='both', expand=True, padx=30)
        
        # Sales report
        sales_frame = tk.Frame(reports_container, bg=self.colors['card_bg'], relief='raised', bd=1)
        sales_frame.pack(fill='both', expand=True, pady=10)
        
        tk.Label(sales_frame, text="Sales Summary", font=('Poppins', 16, 'bold'),
                bg=self.colors['card_bg']).pack(pady=15, padx=20, anchor='w')
        
        conn = self.db.connect()
        if conn:
            cursor = conn.cursor()
            
            # Today's sales
            cursor.execute("""SELECT COUNT(*), COALESCE(SUM(total_amount), 0) 
                            FROM orders WHERE DATE(order_date) = CURDATE()""")
            today_orders, today_sales = cursor.fetchone()
            
            # This week's sales
            cursor.execute("""SELECT COUNT(*), COALESCE(SUM(total_amount), 0) 
                            FROM orders WHERE YEARWEEK(order_date) = YEARWEEK(CURDATE())""")
            week_orders, week_sales = cursor.fetchone()
            
            # This month's sales
            cursor.execute("""SELECT COUNT(*), COALESCE(SUM(total_amount), 0) 
                            FROM orders WHERE YEAR(order_date) = YEAR(CURDATE()) 
                            AND MONTH(order_date) = MONTH(CURDATE())""")
            month_orders, month_sales = cursor.fetchone()
            
            # All time
            cursor.execute("""SELECT COUNT(*), COALESCE(SUM(total_amount), 0) FROM orders""")
            total_orders, total_sales = cursor.fetchone()
            
            cursor.close()
            self.db.disconnect()
            
            # Display stats
            stats_grid = tk.Frame(sales_frame, bg=self.colors['card_bg'])
            stats_grid.pack(fill='x', padx=20, pady=20)
            
            periods = [
                ("Today", today_orders, today_sales),
                ("This Week", week_orders, week_sales),
                ("This Month", month_orders, month_sales),
                ("All Time", total_orders, total_sales)
            ]
            
            for i, (period, orders, sales) in enumerate(periods):
                period_frame = tk.Frame(stats_grid, bg='white', relief='solid', bd=1)
                period_frame.grid(row=i//2, column=i%2, padx=10, pady=10, sticky='nsew')
                
                tk.Label(period_frame, text=period, font=('Poppins', 12, 'bold'),
                        bg='white').pack(pady=10)
                
                tk.Label(period_frame, text=f"{orders} Orders",
                        font=('Open Sans', 11), bg='white').pack(pady=5)
                
                tk.Label(period_frame, text=f"₹{sales:.2f}",
                        font=('Poppins', 16, 'bold'), fg=self.colors['primary'],
                        bg='white').pack(pady=10)
                
                stats_grid.grid_rowconfigure(i//2, weight=1)
                stats_grid.grid_columnconfigure(i%2, weight=1)
        
        # Top selling items
        top_items_frame = tk.Frame(reports_container, bg=self.colors['card_bg'], relief='raised', bd=1)
        top_items_frame.pack(fill='both', expand=True, pady=10)
        
        tk.Label(top_items_frame, text="Top Selling Items", font=('Poppins', 16, 'bold'),
                bg=self.colors['card_bg']).pack(pady=15, padx=20, anchor='w')
        
        conn = self.db.connect()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT m.name, m.category, SUM(oi.quantity) as total_qty, 
                       SUM(oi.quantity * oi.price) as total_revenue
                FROM order_items oi
                JOIN menu_items m ON oi.menu_item_id = m.id
                GROUP BY m.id
                ORDER BY total_qty DESC
                LIMIT 10
            """)
            
            columns = ('Rank', 'Item Name', 'Category', 'Quantity Sold', 'Revenue')
            tree = ttk.Treeview(top_items_frame, columns=columns, show='headings', height=10)
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=120)
            
            rank = 1
            for row in cursor.fetchall():
                name, category, qty, revenue = row
                tree.insert('', 'end', values=(
                    f"#{rank}",
                    name,
                    category,
                    qty,
                    f'₹{revenue:.2f}'
                ))
                rank += 1
            
            cursor.close()
            self.db.disconnect()
            
            tree.pack(fill='both', expand=True, padx=20, pady=10)


# Main execution
if __name__ == "__main__":
    root = tk.Tk()
    app = RestaurantManagementSystem(root)
    root.mainloop()