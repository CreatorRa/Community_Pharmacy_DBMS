--Transaction 1 – Insert and Trigger Execution
---------------------------------------------------------------------------
--In this transaction, we created a new prescription with high urgency and dispensed medication for it.
-------------------------------------------------------------------------------------

BEGIN;

-- 1. New prescription (High urgency -> should appear in urgent_rx_view)
INSERT INTO prescription (rx_id, rx_date, status, urgency, patient_id, doctor_id, pharmacist_id)
VALUES (4101, CURRENT_DATE, 'Dispensed', 'High', 601, 701, 801); -- Changed from 'Pending' to 'Dispensed' to reflect the status after dispensing.

-- 2. Item for the prescription (valid drug_id)
INSERT INTO prescription_items (rx_id, drug_id, qty_prescribed, dosage_instruc, frequency, refills_allowed)
VALUES (4101, 2001, 5, 'Take with water', '2x daily', 0);

-- 3. Create a dispense record
INSERT INTO dispense (dispense_id, dispense_date, total_amount, commission, pharmacist_id, rx_id)
VALUES (5101, CURRENT_DATE, 12.00, 1.20, 801, 4101);

-- 4. This INSERT fires triggers: 1) expiry check (BEFORE), 2) stock check (BEFORE), 3) reduce_inventory_stock (AFTER)
INSERT INTO dispensed_items (line_item_id, qty_dispensed, dispense_id, lot_batch_id)
VALUES (6101, 2, 5101, 3001);

COMMIT;

-- Verification Queries to illustrate the effects of the transaction and triggers:
SELECT lot_batch_id, qty_on_hand FROM inventory_lot WHERE lot_batch_id = 3001;

-- Transaction 2 – Safe Reversal
----------------------------------------------------------------------------
-- Reversing the previous transaction safely by restoring inventory first.
----------------------------------------------------------------------------
BEGIN;

UPDATE inventory_lot
SET qty_on_hand = qty_on_hand + 2
WHERE lot_batch_id = 3001;

-- Now we can safely delete from the bottom to the top (Child to Parent)
DELETE FROM dispensed_items WHERE line_item_id = 6101;
DELETE FROM dispense WHERE dispense_id = 5101;
DELETE FROM prescription_items WHERE rx_id = 4101;
DELETE FROM prescription WHERE rx_id = 4101;

COMMIT;

--Final Verification to show inventory is back to normal
SELECT lot_batch_id, qty_on_hand FROM inventory_lot WHERE lot_batch_id = 3001;

-- Transaction 3: Creating a Multi-Item Purchase Order
---------------------------------------------------------------------------
-- Scenario: The pharmacy is ordering new stock. 
-- The Order Header and the Order Items must be created in the exact same transaction. 
-- If the items fail to save, the header should be rolled back automatically.
---------------------------------------------------------------------------
BEGIN;

-- Step 1: Create the Order Header
-- We are using today's date (Feb 21, 2026) and expecting delivery in 5 days.
-- This satisfies the constraint: Expected_delivery_date >= Order_date!
INSERT INTO PURCHASE_ORDER (Order_id, Order_date, Expected_delivery_date, Status, Supplier_ID)
VALUES (6101, '2026-02-21', '2026-02-26', 'PENDING', 1001);

-- Step 2: Add the first drug to the order (Amoxicillin - Drug_id 2001)
-- We order 100 units. 
--Satisfies the CHECK (Qty_ordered > 0) constraint.
INSERT INTO PURCHASE_ORDER_ITEM (Product_id, Drug_id, Qty_ordered, Unit_cost)
VALUES (6101, 2001, 100, 1.90);

-- Step 3: Add the second drug to the order (Ibuprofen - Drug_id 2002)
INSERT INTO PURCHASE_ORDER_ITEM (Product_id, Drug_id, Qty_ordered, Unit_cost)
VALUES (6101, 2002, 250, 0.80);

COMMIT;

-- Verification Query to show the professor that the join works perfectly
SELECT po.Order_id, s.Company_name, po.Status, poi.Qty_ordered, dc.Drug_Name
FROM PURCHASE_ORDER po
JOIN PURCHASE_ORDER_ITEM poi ON po.Order_id = poi.Product_id
JOIN SUPPLIER s ON po.Supplier_ID = s.Supplier_ID
JOIN DRUG_CATALOGUE dc ON poi.Drug_id = dc.Drug_id
WHERE po.Order_id = 6101;
