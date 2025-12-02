# **Capgemini Assessment: Simple Expense Tracker**

A lightweight expense tracking application built for the Capgemini technical assessment.  
The app allows users to enter expenses (category, amount, description) and provides key analytics including:

- **Total expense**
- **Total expense by category**
- **Expense trends**
- **Highest and lowest spend category**

The project operates under these assumptions:  
Data is stored in a **CSV file**  
No database required  
Built in **Python** using **Streamlit**  
Includes **seed data** and **hosted version**  

---

# **Live Hosted Version (Streamlit)**

**Hosted App:** *kd-capgemini-app.streamlit.app*  

The hosted app persists changes during runtime but does **not** write back to GitHub (expected behavior on Streamlit Cloud).

---

# **Project Structure**
.
├── app.py # Main Streamlit application
├── expense_data.csv # Seed data (file based storage)
├── requirements.txt # Project dependencies
└── README.md # Documentation


### **Key Files**

- **app.py**  
  Contains the full Streamlit UI, navigation, and analytics functions.
- **expense_data.csv**  
  File-based storage containing:
  - `category`
  - `amount`
  - `data` (description)
  - `time_id` (unique timestamp, could be used as primary key or partial key)
- **requirements.txt**  
  Dependencies used both locally and on Streamlit Cloud.

---

# **Approach & Design**

### **1. Storage Layer (CSV)**
The prompt states that data may be kept *in memory or in a file* and that a database is *not necessary*.  
Therefore, this project uses:
- **`expense_data.csv`** as the storage backend  
- **pandas** for all read/write operations  

This keeps the application simple while still supporting all required analytics.

---

### **2. UI Layer (Streamlit)**

Although the prompt allows a command-line app, a lightweight UI provides clearer visibility and better testing.  
The app includes three main pages:

#### ** View Expenses**
- Full table of all expenses
- Total expense
- Total expense by category
- Highest and lowest spend category

#### ** Add Expense**
- Dropdown category selection  
- Ability to add new categories via an additional form  
- Automatically redirects back to the main page after saving

#### ** Expense Trends**
- Box plot of expense distribution by category  
- Daily expense trend line  
- Simple prediction curve using linear regression (`numpy.polyfit`)  

---

# **Test Data & Seed Data**

`expense_data.csv` includes realistic sample data for hardware store expenses such as labor, rent, inventory, shipping, equipment, and supplies.

This seed data enables immediate testing of:
- analytics,
- trends,
- category computations,
- and predictions.

---

# **Running the App Locally**

### **1. Clone the repository**
```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>

### **2. Install dependencies**
pip install -r requirements.txt

### **3. Run the application**
streamlit run app.py

Your default browser will automatically open the app.
```

---

# **How to Test & Verify Functionality**

### **1. Add a new expense**
- Navigate to “Add Expense”
- Fill out the form
- After submitting, the app auto-returns to View Expenses

### **2. Verify analytics**
- Confirm the total expense changes
- Totals by category update
- Highest/lowest categories recompute
- New categories appear in dropdowns

### **3. Explore trends**
- View box plots by category
- View daily trends
- Observe prediction line

---

# **requirements.txt**
streamlit
pandas
numpy
altair

---

# **Future Improvements (Beyond Assessment Requirements)**
If scaled into a production system, natural next steps include:
Replacing CSV with a persistent database (PostgreSQL or SQLite)
Adding multi-user authentication
Date-range filtering & advanced reporting
Export options (CSV/Excel)

---

# **Notes About Storage & Hosting**
Streamlit Cloud runs the app inside a temporary container.
Therefore:
CSV changes persist while the container is active
They do not sync back to GitHub (normal behavior)
expense_data.csv in the GitHub repo acts as seed/demo data
This aligns with the assignment requirement that data may be stored in a file rather than a database.
