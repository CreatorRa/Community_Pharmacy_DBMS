--Transaction 1 – Insert and Trigger Execution
---------------------------------------------------------------------------
--In this transaction, we created a new prescription with high urgency and dispensed medication for it.
-------------------------------------------------------------------------------------

BEGIN;

-- New prescription (High urgency -> should appear in urgent_rx_view)
INSERT INTO prescription (rx_id, rx_date, status, urgency, patient_id, doctor_id, pharmacist_id)
VALUES (4101, CURRENT_DATE, 'Pending', 'High', 601, 701, 801);

-- Item for the prescription (valid drug_id)
INSERT INTO prescription_items (rx_id, drug_id, qty_prescribed, dosage_instruc, frequency, refills_allowed)
VALUES (4101, 2001, 5, 'Take with water', '2x daily', 0);

-- Create a dispense record
INSERT INTO dispense (dispense_id, dispense_date, total_amount, commission, pharmacist_id, rx_id)
VALUES (5101, CURRENT_DATE, 12.00, 1.20, 801, 4101);

-- This INSERT fires triggers:
-- 1) expiry check (BEFORE)
-- 2) stock check (BEFORE)
-- 3) reduce_inventory_stock (AFTER)
INSERT INTO dispensed_items (line_item_id, qty_dispensed, dispense_id, lot_batch_id)
VALUES (6101, 2, 5101, 3001);

COMMIT;

SELECT lot_batch_id, qty_on_hand
FROM inventory_lot
WHERE lot_batch_id = 3001;

SELECT COUNT(*) AS times_used, SUM(qty_dispensed) AS total_dispensed
FROM dispensed_items
WHERE lot_batch_id = 3001;
