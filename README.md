# 🍛 Spice Haven – Restaurant Management System

A desktop application for running a restaurant end to end: manage the menu, take orders, track reservations, view customers and staff, read feedback, and check sales reports. Built with **Python, Tkinter and MySQL**.

> The database and all tables are created automatically on first launch, with sample menu items and staff so you can explore the app right away.

## ✨ Features

| Module | What it does |
|---|---|
| 📊 **Dashboard** | Live clock, available menu items, today's orders, total customers, today's revenue, and recent orders |
| 🍽️ **Menu Management** | View the full menu and add new items (name, category, price, description, spice level, veg / non-veg) |
| 🛒 **New Order** | Browse menu cards, build a cart, adjust quantities, and place an order (Dine-in / Takeaway / Delivery) with table number and customer details |
| 📋 **Orders** | Order history with a status filter (Pending, Preparing, Ready, Completed, Cancelled) |
| 📅 **Reservations** | View and add table reservations with date, time, guest count and special requests |
| 👥 **Customers** | Customer list with total orders and total spend |
| 👨‍🍳 **Staff** | Staff directory with role, contact details and salary |
| 💬 **Feedback** | Customer ratings (1–5 stars) and comments |
| 📈 **Reports** | Sales summary for today / this week / this month / all time, plus top 10 selling items |

## 🛠️ Tech Stack

- **Language:** Python 3.8+
- **GUI:** Tkinter / ttk (ships with Python)
- **Database:** MySQL, via `mysql-connector-python`
- **Config:** `python-dotenv` (optional, for reading a `.env` file)

## 📁 Project Structure

```
spice-haven-restaurant-management/
├── restaurant_management.py   # Application (database layer + Tkinter UI)
├── database/
│   ├── schema.sql             # Table definitions (reference copy)
│   └── sample_data.sql        # Sample menu and staff (reference copy)
├── docs/
│   └── screenshots/           # Add your app screenshots here
├── .env.example               # Template for database credentials
├── .gitignore
├── requirements.txt
├── LICENSE
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher (with Tkinter, included in the standard Windows/macOS installers)
- MySQL Server 5.7+ / 8.x running locally

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/<your-username>/spice-haven-restaurant-management.git
   cd spice-haven-restaurant-management
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the database connection**

   Copy `.env.example` to `.env` and enter your MySQL credentials:
   ```
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_NAME=spice_haven_db
   ```
   Your `.env` file is git-ignored, so your password is never committed.

4. **Run the app**
   ```bash
   python restaurant_management.py
   ```

On first run the app creates the `spice_haven_db` database, all tables, and the sample data automatically. You don't need to run the SQL files yourself.

> **Linux users:** if Tkinter is missing, install it with `sudo apt install python3-tk`.

## 🗄️ Database Schema

| Table | Purpose |
|---|---|
| `menu_items` | Dishes with category, price, spice level, veg / non-veg, availability |
| `orders` | Order header: customer, table, type, total, status, timestamp |
| `order_items` | Line items linked to `orders` and `menu_items` |
| `reservations` | Table bookings with date, time and guests |
| `staff` | Employee records |
| `customers` | Customer profiles with order count and total spend |
| `feedback` | Ratings and comments |

Full definitions are in [`database/schema.sql`](database/schema.sql).

## 🖼️ Screenshots

Add screenshots of the app to `docs/screenshots/` and reference them here:

```markdown
![Dashboard](docs/screenshots/dashboard.png)
![New Order](docs/screenshots/new-order.png)
```

## ⚠️ Current Limitations

- Customers, staff and feedback screens are **view-only** for now (no add/edit forms yet).
- Order status can be filtered but not yet updated from the UI.
- No user login or role-based access.

## 🔮 Roadmap

- [ ] Add/edit forms for customers, staff and feedback
- [ ] Update order status from the Orders screen
- [ ] Printable bills / invoices
- [ ] Staff login with roles
- [ ] Edit and delete menu items, with image support

## 🤝 Contributing

Contributions are welcome. Fork the repo, create a feature branch, and open a pull request.

## 📄 License

Released under the [MIT License](LICENSE).
