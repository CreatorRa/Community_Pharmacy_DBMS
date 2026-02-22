# Community Pharmacy Database Management System (DBMS)

## Project Overview

The Community Pharmacy Database Management System (DBMS) is a comprehensive relational database application designed to support pharmacy operations. This system facilitates the management of patient prescriptions, lot-level inventory, medication dispensing, and supply chain purchase orders.

Developed as an academic capstone project, the system evolved from a conceptual business scenario into a fully normalized PostgreSQL database integrated with an interactive Python (Streamlit) frontend. The project demonstrates the practical application of advanced database concepts, including Boyce-Codd Normal Form (BCNF) normalization, ACID-compliant transactions, concurrency control (Two-Phase Locking), views, indexing, and soft deletion methodologies.

---

## Project Evolution and Methodology

### Phase 1: Scenario Characterization and Requirements Gathering

The project was initiated based on a core business scenario requiring the tracking of Patients, Doctors, Drugs, Prescriptions, Dispensing Records, and Purchase Orders. The primary requirement was to ensure that dispensed prescriptions are strictly linked to specific drug lots, thereby preventing the distribution of expired products and maintaining accurate inventory deduction. Initial operations defined standard CRUD (Create, Read, Update, Delete) capabilities alongside specific exclusion protocols, such as order cancellations and dispense record voiding.

### Phase 2: Conceptual and Logical Design

Business requirements were translated into an Entity-Relationship (ER) model. This phase involved identifying 14 distinct entities and over 50 attributes. Complex relationships were mapped, including one-to-many dependencies between Prescriptions and Prescription Items, and many-to-many interactions resolved through associative entities such as Purchase Order Items.

### Phase 3: Relational Mapping and Normalization

To eliminate data redundancy and prevent insertion, update, and deletion anomalies, the database schema was rigorously normalized to the Boyce-Codd Normal Form (BCNF). For instance, the initial Drug entity, which contained generic and brand data alongside dosage strength, was decomposed into separate Generics and Drug Catalogue tables to resolve transitive dependencies and strictly adhere to BCNF standards.

### Phase 4: Physical Implementation

Data Definition Language (DDL) scripts were authored to construct the database in PostgreSQL. Referential integrity was enforced utilizing Primary and Foreign Keys. Check constraints were implemented to validate logical conditions (e.g., ensuring delivery dates occur after order dates). Furthermore, views were created to streamline complex, frequently executed queries, and indexes were applied to optimize data retrieval performance.

### Phase 5: Application Development and Transaction Management

A web-based frontend interface was developed using Streamlit to facilitate secure and atomic data entry.

* **Soft Deletion Implementation:** Initial requirements dictated the removal of canceled orders. To preserve financial audit trails and referential integrity, this was modified to a soft-deletion approach, utilizing an `UPDATE` statement to alter the order status to 'CANCELLED' rather than executing a hard `DELETE`.
* **ACID Transactions:** Complex operations, such as revising a purchase order, were encapsulated within atomic transaction blocks using `BEGIN`, `COMMIT`, and `ROLLBACK` commands. This ensures that multi-step processes involving inserts, updates, and deletes are executed safely and rolled back entirely if a database or logical failure occurs.

---

## Key System Features

1. **System Monitoring Dashboard:**
* A read-only executive interface featuring live Key Performance Indicator (KPI) metrics.
* Integration of interactive Plotly visualizations (gauge and pie charts) to display real-time system health, purchase order statuses, and low-stock alerts.
* Data tables utilizing Pandas Styler for conditional formatting, specifically highlighting expired inventory lots for immediate operational awareness.


2. **Purchase Order Management (Supply Chain Module):**
* **Order Creation:** Batched data entry that fetches live Foreign Keys via dropdown menus to guarantee referential integrity during the insertion process.
* **Order Revision:** Secure atomic transactions facilitating the modification of pending orders.
* **Order Cancellation:** Soft-deletion logic applied to abort orders while maintaining regulatory compliance and historical audit trails.


3. **Dispensing Module:**
* Processes patient prescriptions by automatically deducting inventory from specific lot records, enforcing First-Expire, First-Out (FIFO) inventory logic to minimize waste and ensure patient safety.



---

## Technology Stack

* **Database Management System:** PostgreSQL
* **Backend / Database Adapter:** Python 3.x, `psycopg2`
* **Frontend Framework:** Streamlit
* **Data Visualization and Processing:** Pandas, Plotly Express, Plotly Graph Objects
* **Styling:** Custom CSS, Google Material Symbols

---

## Installation and Setup Guide

To evaluate and run this project locally, please follow the steps below.

### Prerequisites

Ensure you have the following installed on your local machine:

* **Python 3.8+**
* **PostgreSQL** (Ensure the PostgreSQL service is running)
* **Git**

### Step 1: Clone the Repository

Open your terminal or command prompt and clone the project repository using Git:

```bash
git clone https://github.com/YourUsername/YourRepositoryName.git
cd YourRepositoryName

```

*(Note: Replace the URL above with your actual repository link).*

### Step 2: Set Up the Database

Before running the application, the PostgreSQL database must be initialized.

1. Open pgAdmin or your preferred PostgreSQL command-line tool.
2. Create a new, empty database named `pharmacy_db` (or your chosen name).
3. Execute the provided DDL script (e.g., `schema.sql`) to generate the tables, constraints, and views.
4. Execute the provided DML script (e.g., `seed_data.sql`) to insert the initial sample records required for the application to function.

### Step 3: Configure Database Credentials

The Python application needs to securely connect to your PostgreSQL database.

1. Locate the database connection file (e.g., `db.py` or `.env` depending on your setup).
2. Update the connection parameters (`host`, `database`, `user`, `password`, `port`) to match your local PostgreSQL credentials.

### Step 4: Create a Virtual Environment (Recommended)

To prevent dependency conflicts, it is highly recommended to run the application within a virtual environment.
**For macOS and Linux:**

```bash
python3 -m venv venv
source venv/bin/activate

```

**For Windows:**

```cmd
python -m venv venv
venv\Scripts\activate

```

### Step 5: Install Dependencies

With your virtual environment activated, install the required Python libraries using the `requirements.txt` file:

```bash
pip install -r requirements.txt

```

### Step 6: Run the Application

Once the database is configured and dependencies are installed, you can launch the Streamlit frontend. Execute the following command in your terminal:

```bash
streamlit run app.py

```

A new tab will automatically open in your default web browser displaying the Community Pharmacy DBMS portal. If it does not open automatically, navigate to `http://localhost:8501` in your browser.

---

## Academic Context

This system was developed for the Database Management Systems curriculum at KLU University. It demonstrates the complete lifecycle of database development, from translating business requirements into a Relational Algebra model to executing physical SQL implementation and managing transaction concurrency control.
