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
DeLETE FROM dispensed_items WHERE line_item_id = 6101;
DELETE FROM dispense WHERE dispense_id = 5101;
DELETE FROM prescription_items WHERE rx_id = 4101;
DELETE FROM prescription WHERE rx_id = 4101;

COMMIT;

--Final Verification to show inventory is back to normal
SELECT lot_batch_id, qty_on_hand FROM inventory_lot WHERE lot_batch_id = 3001;