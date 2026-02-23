-- Assigment 5: Create DATABASE SCRIPT

-- 1. INDEPENDENT TABLES (No Forign Keys)
CREATE TABLE DOCTOR (
	Doctor_id INT PRIMARY KEY,
	NAME VARCHAR(50) NOT NULL,
	-- We included a not null here so that there is an Attribute level constraint, this also is consistent with a real life scenario as we don't want the possiblity of there being a Doctor registerd without knowing who they are.
	Licence_Number VARCHAR(50) UNIQUE, 
	CLinic_address VARCHAR(300)
);

CREATE TABLE PATIENT (
    Patient_id INT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Date_of_birth DATE NOT null CHECK (Date_of_birth <= CURRENT_DATE AND Date_of_birth > '1900-01-01')
    -- The check here is to prevent a typos and vampires from being taken into consideration in our
);

CREATE TABLE PHARMACIST (
    Pharmacist_ID INT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Hire_date DATE NOT NULL,
    Salary_PA DECIMAL(10, 2) CHECK (Salary_PA >= 28912.00)
    -- We are stating here that the data in this column can be up to 10 digits with exactly 2 of those digits after the decimal point. 
    -- THIS IS A CHANGE: We are also placing an constraing on the salary so that it can't be less that the minimum wage in Hamburg, Germany.
    -- Minimum wage: 13.90 per hour * 40 hours per week * 52 = 28912.00
);

CREATE TABLE INSURANCE (
    Policy_id INT PRIMARY KEY,
    Company VARCHAR(100) NOT NULL
);

CREATE TABLE SUPPLIER (
    Supplier_ID INT PRIMARY KEY,
    Company_name VARCHAR(100) NOT NULL,
    Contact_person VARCHAR(100),
    Address VARCHAR(255)
);

CREATE TABLE GENERICS (
    Drug_Name VARCHAR(100) PRIMARY KEY,
    Generic_name VARCHAR(100) NOT NULL
);

-- 2. Dependent Tables (The following tables all contain foreign keys)

CREATE TABLE DRUG_CATALOGUE (
    Drug_id INT PRIMARY KEY,
    Drug_Name VARCHAR(100),
    Form VARCHAR(50),
    Strength VARCHAR(50),
    FOREIGN KEY (Drug_Name) REFERENCES GENERICS(Drug_Name)
);

CREATE TABLE INVENTORY_LOT (
    Lot_batch_ID INT PRIMARY KEY,
    Expiry_date DATE NOT NULL,
    Unit_cost DECIMAL(10, 2) CHECK (Unit_cost >= 0),
    -- We are including a check in the above statement to ensure that it is not possible for anyone at the pharmacy to record a negative inventory costs.
    Qty_on_hand INT DEFAULT 0,
    Drug_id INT,
    FOREIGN KEY (Drug_id) REFERENCES DRUG_CATALOGUE(Drug_id)
);

CREATE TABLE PRESCRIPTION (
    Rx_id INT PRIMARY KEY,
    Rx_date DATE NOT NULL,
    -- The below is a change: We are changing how we dispense.
    -- We are standardizing the status of the pescription.
    -- We are doing so to prevent different pharmacists from entering their own version of what they might think is sufficient e.g. "Dispensed", "Done", "waiting", "unfifilled"
    -- By locking what exactly can be entered it will make writing our queries easier later on. Everyone is forced to use the same vocabulary. 
    Status VARCHAR(50) CHECK (Status IN ('Pending', 'Dispensed', 'Cancelled')),
    Urgency VARCHAR(50),
    Patient_id INT,
    Doctor_id INT,
    Pharmacist_ID INT,
    -- Below are multiple foreign keys mapping the relationships between patient, doctor, and pharmacist through the perscription
    FOREIGN KEY (Patient_id) REFERENCES PATIENT(Patient_id),
    FOREIGN KEY (Doctor_id) REFERENCES DOCTOR(Doctor_id),
    FOREIGN KEY (Pharmacist_ID) REFERENCES PHARMACIST(Pharmacist_ID)
);

CREATE TABLE PRESCRIPTION_ITEMS (
    -- We are using a composite Key in this table to uniquely identify a drug within a specific prescription.
    Rx_id INT,
    Drug_id INT,
    Qty_prescribed INT CHECK (Qty_prescribed > 0),
    Dosage_instruc VARCHAR(255),
    Frequency VARCHAR(100),
    Refills_allowed INT DEFAULT 0,
    PRIMARY KEY (Rx_id, Drug_id),
    FOREIGN KEY (Rx_id) REFERENCES PRESCRIPTION(Rx_id),
    FOREIGN KEY (Drug_id) REFERENCES DRUG_CATALOGUE(Drug_id)
);

CREATE TABLE DISPENSE (
    Dispense_id INT PRIMARY KEY,
    Dispense_date DATE NOT NULL,
    Total_amount DECIMAL(10, 2) CHECK(Total_amount > 0),
    Commission  DECIMAL(10, 2) check (Commission > 0),
    -- We have two checks in the above statements to ensure that there can be no accidental negative entries recorded
    Pharmacist_ID INT,
    Rx_id INT,
    FOREIGN KEY (Pharmacist_ID) REFERENCES PHARMACIST(Pharmacist_ID),
    FOREIGN KEY (Rx_id) REFERENCES PRESCRIPTION(Rx_id)
);

CREATE TABLE DISPENSED_ITEMS (
    Line_item_id INT PRIMARY KEY,
    Qty_dispensed INT CHECK (Qty_dispensed > 0),
    -- Again a check to ensure some amount is actually given or dispensed.
    Dispense_id INT,
    Lot_batch_ID INT,
    FOREIGN KEY (Dispense_id) REFERENCES DISPENSE(Dispense_id),
    FOREIGN KEY (Lot_batch_ID) REFERENCES INVENTORY_LOT(Lot_batch_ID)
);


CREATE TABLE PURCHASE_ORDER (
    Order_id INT PRIMARY KEY,
    Order_date DATE NOT NULL,
    Expected_delivery_date DATE,
    Status VARCHAR(50) CHECK (Status IN ('PENDING', 'DELIVERED', 'CANCELLED')),
    -- Standardizing the status of our orders to make queries in the future easier.
    Supplier_ID INT,
    FOREIGN KEY (Supplier_ID) REFERENCES SUPPLIER(Supplier_ID),
    CONSTRAINT check_delivery_date CHECK (Expected_delivery_date >= Order_date)
    -- The above is a tuple level constraint, as mentioned in class this a constraint where the database  needs to look at two or more cells in the exact same row and compare them to each other to see if the data makes logical sense.
    -- This constraint is essentially here to ensure that our expected delivery date is greater than (after) or equal (same day delivery) as the day we order the medications. 
    -- We are including this constraint, so that no one in the pharmacy can accidental invert the dates or makes a mistake. 
    -- If user accidentally enters the wrong date, the database will send a pop-up saying "Violated Constraint:Check_delivery_date"
);

CREATE TABLE PURCHASE_ORDER_ITEM (
    Product_id INT,
    Drug_id INT,
    Qty_ordered INT CHECK (Qty_ordered > 0),
    Unit_cost DECIMAL(10, 2),
    PRIMARY KEY (Product_id, Drug_id),
    FOREIGN KEY (Product_id) REFERENCES PURCHASE_ORDER(Order_id),
    FOREIGN KEY (Drug_id) REFERENCES DRUG_CATALOGUE(Drug_id)
);

CREATE TABLE PAYS (
    Dispense_id INT,
    Policy_id INT,
    Amount_covered DECIMAL(10, 2),
    PRIMARY KEY (Dispense_id, Policy_id),
    FOREIGN KEY (Dispense_id) REFERENCES DISPENSE(Dispense_id),
    FOREIGN KEY (Policy_id) REFERENCES INSURANCE(Policy_id)
);

-- 3. Indexes, Views, and Triggers

CREATE INDEX idx_patient_name ON PATIENT(Name);
-- We are creating an index on patient's name so that we can speed up the retrival times for pharmacists. 
-- This means that when a patient comes into a pharmacy the pharmacist can very quickly ask for their name and quickly retrive a patient's profile in the database
-- Our reasoning here is that most people are unlikely to remember their patient_id, but they will remember their names. So it should be something that is quickly used to search a database. 

CREATE VIEW URGENT_RX_VIEW AS
SELECT 
    p.Name AS Patient_Name, 
    d.Name AS Doctor_Name, 
    rx.Rx_date, 
    rx.Status
FROM PRESCRIPTION rx
JOIN PATIENT p ON rx.Patient_id = p.Patient_id
JOIN DOCTOR d ON rx.Doctor_id = d.Doctor_id
WHERE rx.Urgency = 'High';
-- During the ER phase we identified that some conditions are worse that others. We are creating this virtual table so that these complex joins are already completed.
-- This allows pharmacists to instantly see which prescriptions are high urgency without writing the JOIN manually.




/*=================
 * 1st Trigger: Inventory Managment - Explanation in a real world context:
 ==================
Imagine the pharmacy has 73 boxes of Amoxicillin (Batch #777) in 
the INVENTORY_LOT table.

1. A pharmacist fills a prescription and inserts a record into the 
   DISPENSED_ITEMS table, for instantce dispensing 3 boxes from Batch #777).
2. THE TRIGGER immediately notices this new insert and fires the function.
3. THE FUNCTION grabs the NEW.Qty_dispensed (3) and 
   the NEW.Lot_batch_ID (777). 
4. It goes to the inventory table, finds Batch #777, and automatically 
   updates the Qty_on_hand count from 73 boxes down to 70 boxes.

By writing this, we guarantee that the physical inventory and the database are never out of sync. 
It becomes mathematically impossible to dispense a drug without the inventory updating automatically.
=======================
 */

CREATE OR REPLACE FUNCTION reduce_inventory_stock()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE INVENTORY_LOT
    SET Qty_on_hand = Qty_on_hand - NEW.Qty_dispensed
	-- This part defines the actual action of our trigger. We are telling the database to take the current inventory count, and subtract the quantity that was dispensed in this new transaction.
    WHERE Lot_batch_ID = NEW.Lot_batch_ID;
	-- The Lot_batch_ID is important here becuase we want to only subtract stock from the exact specific batch of drugs we dispensed from, not from a different batch or the DB reducing the stock for every single drug in the pharmacy.
    RETURN NEW;
END;
$$ LANGUAGE plpgsql; 

CREATE TRIGGER trg_reduce_stock
AFTER INSERT ON DISPENSED_ITEMS
FOR EACH row
-- It is important that we state for each row here because as we identified in the ER stage, a perscription can contain multiple perscription iteams. 
-- If a pharmacist dispense multiple different drugs in one 'dispense' then this ensures that the DB runs the subtraction 5 separate times, once for each drug. 
EXECUTE FUNCTION reduce_inventory_stock();


/*=======================
 * 2nd Trigger: Prevent Over-Dispensing - Explanation
 =======================
 Imagine a pharmacist tries to dispense 50 boxes of a drug, but the shelf only has 30 boxes left. 
 This trigger checks the INVENTORY_LOT before allowing the transaction. 
 If stock is too low, it blocks the insert and alerts the pharmacist.
 This would prevent the pharmacist from creating a negative number in our inventory. 
 This trigger works in tandem with our 1st trigger
 =====================
 */

CREATE OR REPLACE FUNCTION check_sufficient_stock()
RETURNS TRIGGER AS $$
DECLARE
    current_stock INT;
BEGIN
    -- 1. Find out how much stock we currently have for this specific batch
    SELECT Qty_on_hand INTO current_stock
    FROM INVENTORY_LOT
    WHERE Lot_batch_ID = NEW.Lot_batch_ID;
    -- 2. Check if the pharmacist is asking for more than we have
    IF NEW.Qty_dispensed > current_stock THEN
        RAISE EXCEPTION 'Insufficient stock! You tried to dispense %, but only % are available in Batch %.', 
        NEW.Qty_dispensed, current_stock, NEW.Lot_batch_ID;
    END IF;
    -- 3. If everything is fine, allow the dispense to proceed
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach it to run BEFORE the insert happens
CREATE TRIGGER trg_check_stock
BEFORE INSERT ON DISPENSED_ITEMS
FOR EACH row
-- Important that it is done for every drug that the pharmacist might be dispensing at once.
EXECUTE FUNCTION check_sufficient_stock();

/*=======================
 * 3rd Trigger: Expired Medication Blocker
 =======================
 Imagine a pharmacist accidentally scans a box of medication that expired last month. 
 Before the database allows the dispense to happen, it checks the INVENTORY_LOT expiry date. 
 If it is past the current date,it completely blocks the transaction for patient safety.
 It also prevents the pharmacy from any liability
 =====================
 */

CREATE OR REPLACE FUNCTION prevent_expired_dispense()
RETURNS TRIGGER AS $$
DECLARE
    batch_expiry DATE;
BEGIN
    -- 1. Get the expiry date of the specific batch being dispensed
    SELECT Expiry_date INTO batch_expiry
    FROM INVENTORY_LOT
    WHERE Lot_batch_ID = NEW.Lot_batch_ID;

    -- 2. Check if that date is in the past
    IF batch_expiry < CURRENT_DATE THEN
        RAISE EXCEPTION 'CRITICAL ERROR: Cannot dispense Lot_batch_ID %. This medication expired on %!', 
        NEW.Lot_batch_ID, batch_expiry;
    END IF;

    -- 3. If it is not expired, allow it
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_expiry
BEFORE INSERT ON DISPENSED_ITEMS
FOR EACH ROW
EXECUTE FUNCTION prevent_expired_dispense();


/*=======================
 * 4th Trigger: Cancelled Perscription
 =======================
 You cannot INSERT a dispense record for a prescription with status = 'Cancelled' 

 =====================
 */

CREATE OR REPLACE FUNCTION assert_no_dispense_for_cancelled_rx()
RETURNS TRIGGER AS $$
DECLARE
    rx_status VARCHAR(50);
BEGIN
    SELECT status INTO rx_status
    FROM prescription
    WHERE rx_id = NEW.rx_id;

    IF rx_status = 'Cancelled' THEN
        RAISE EXCEPTION
        'ASSERTION FAILED: Cannot dispense a cancelled prescription (rx_id=%).',
        NEW.rx_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_assert_no_dispense_cancelled ON dispense;

CREATE TRIGGER trg_assert_no_dispense_cancelled
BEFORE INSERT OR UPDATE ON dispense
FOR EACH ROW
EXECUTE FUNCTION assert_no_dispense_for_cancelled_rx();




