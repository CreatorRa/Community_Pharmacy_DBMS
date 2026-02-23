SQL Queries & Relational Algebra

Introduction & Background

This document presents the design and implementation of advanced SQL queries for a Pharmacy Management Relational Database System. The database is designed to model the complete lifecycle of pharmaceutical operations, bridging clinical patient care with business inventory management.

The system captures and interrelates data across three primary domains:

Clinical Operations: Managing relationships between Doctors, Patients, and their Prescriptions.

Inventory & Supply Chain: Tracking drugs from Suppliers through Purchase Orders into Inventory Lots and the Drug Catalogue.

Retail & Finance: Recording the actual Dispensing of medication by Pharmacists and handling financial transactions involving Insurance providers.

Purpose of This Document:

The objective of this report is to demonstrate the retrieval of complex, actionable business insights from this database schema. The queries presented utilize advanced SQL techniques—including multi-table joins, subqueries, aggregation, and grouping—to answer specific operational questions.

Example of Query Structure:

Natural Language

Algebra

SQL

Complex Queries will follow the same structure however; it will omit the Relational Algebra.

QUERY 1 - SIMPLE (JOIN)

Natural Language:
List the names of patients and the prescription IDs they received.

Relational Algebra:

$$\pi_{\text{name, rx\_id}} (\text{PATIENT} \bowtie_{\text{PATIENT.patient\_id} = \text{PRESCRIPTION.patient\_id}} \text{PRESCRIPTION})$$

SQL:

SELECT P.name, PR.rx_id
FROM PATIENT P, PRESCRIPTION PR
WHERE P.patient_id = PR.patient_id;


QUERY 2 - SIMPLE (JOIN WITH 3 RELATIONS)

Natural Language:
List each dispense ID together with the pharmacist's name and total amount.

Relational Algebra:

$$\pi_{\text{dispense\_id, name, total\_amount}} (\text{PHARMACIST} \bowtie_{\text{PHARMACIST.pharmacist\_id} = \text{DISPENSE.pharmacist\_id}} \text{DISPENSE})$$

SQL:

SELECT D.dispense_id, P.name, D.total_amount
FROM DISPENSE D, PHARMACIST P
WHERE D.pharmacist_id = P.pharmacist_id;


QUERY 3 - SIMPLE (SET OPERATION - UNION)

Natural Language:
List all IDs that appear either as patient IDs or pharmacist IDs.

Relational Algebra:

$$\pi_{\text{patient\_id}}(\text{PATIENT}) \cup \pi_{\text{pharmacist\_id}}(\text{PHARMACIST})$$

SQL:

SELECT patient_id AS id
FROM PATIENT
UNION
SELECT pharmacist_id
FROM PHARMACIST;


QUERY 4 - COMPLEX (AGGREGATION + GROUP BY)

Natural Language:
Find the average total_amount of dispenses processed by each pharmacist.

Relational Algebra:

$$\gamma_{\text{pharmacist\_id}, \text{AVG(total\_amount)} \rightarrow \text{avg\_amount}}(\text{DISPENSE})$$

SQL:

SELECT pharmacist_id, AVG(total_amount) AS avg_amount
FROM DISPENSE
GROUP BY pharmacist_id;


QUERY 5 - COMPLEX (JOIN + AGGREGATION + GROUP BY)

Natural Language:
Find the total quantity dispensed for each drug name.

Relational Algebra:

$$\gamma_{\text{drug\_name}, \text{SUM(qty\_dispensed)} \rightarrow \text{total\_quantity}} (\text{DRUG\_CATALOGUE} \bowtie_{\text{drug\_id}} (\text{LOT\_BATCH} \bowtie_{\text{lot\_batch\_id}} \text{DISPENSED\_ITEMS}))$$

SQL:

SELECT DC.drug_name, SUM(DI.qty_dispensed) AS total_quantity
FROM DRUG_CATALOGUE DC, LOT_BATCH LB, DISPENSED_ITEMS DI
WHERE DC.drug_id = LB.drug_id
AND LB.lot_batch_id = DI.lot_batch_id
GROUP BY DC.drug_name;


QUERY 6 - COMPLEX (SUBQUERY + AGGREGATION)

Natural Language:
Find the pharmacists whose salary is higher than the average salary of all pharmacists.

Relational Algebra:

$$\text{AvgSal} \leftarrow \gamma_{\text{AVG(salary)} \rightarrow \text{avg\_salary}}(\text{PHARMACIST})$$

$$\pi_{\text{name}} (\sigma_{\text{salary} > \text{avg\_salary}} (\text{PHARMACIST} \times \text{AvgSal}))$$

SQL:

SELECT name
FROM PHARMACIST
WHERE salary > (
    SELECT AVG(salary)
    FROM PHARMACIST
);


QUERY 7 - SIMPLE (JOIN)

Natural Language:
Show each doctor and the prescriptions they issued (doctor name + rx_id).

Relational Algebra:

$$\pi_{\text{Doctor.name, rx\_id}} (\text{DOCTOR} \bowtie_{\text{DOCTOR.doctor\_id} = \text{PRESCRIPTION.doctor\_id}} \text{PRESCRIPTION})$$

SQL:

SELECT D.name, PR.rx_id
FROM DOCTOR D, PRESCRIPTION PR
WHERE D.doctor_id = PR.doctor_id;


QUERY 8 - SIMPLE (JOIN + RELATIONS)

Natural Language:
For every prescription, display the patient's name and the prescription date.

Relational Algebra:

$$\pi_{\text{rx\_id, Patient.name, rx\_date}} (\text{PRESCRIPTION} \bowtie_{\text{PRESCRIPTION.patient\_id} = \text{PATIENT.patient\_id}} \text{PATIENT})$$

SQL:

SELECT PR.rx_id, PA.name, PR.rx_date
FROM PRESCRIPTION PR, PATIENT PA
WHERE PR.patient_id = PA.patient_id;


QUERY 9 - SIMPLE (UNION)

Natural Language:
Create one combined list of all people names in the system (patients + doctors + pharmacists).

Relational Algebra:

$$\pi_{\text{name}}(\text{PATIENT}) \cup \pi_{\text{name}}(\text{DOCTOR}) \cup \pi_{\text{name}}(\text{PHARMACIST})$$

SQL:

SELECT name FROM PATIENT
UNION
SELECT name FROM DOCTOR
UNION
SELECT name FROM PHARMACIST;


QUERY 10 - COMPLEX (JOIN + AGGREGATION + GROUP BY)

Natural Language:
For each patient, calculate the total quantity of drugs prescribed (sum of qty_prescribed).

SQL:

SELECT PA.patient_id, PA.name, SUM(PI.qty_prescribed) AS total_qty_prescribed
FROM PATIENT PA, PRESCRIPTION PR, PRESCRIPTION_ITEMS PI
WHERE PA.patient_id = PR.patient_id
AND PR.rx_id = PI.rx_id
GROUP BY PA.patient_id, PA.name;


QUERY 11 - COMPLEX (SUBQUERY + GROUP BY + COUNT DISTINCT)

Natural Language:
Find patients who were treated by more different doctors than the average patient.

SQL:

SELECT PR.patient_id, COUNT(DISTINCT PR.doctor_id) AS doctor_count
FROM PRESCRIPTION PR
GROUP BY PR.patient_id
HAVING COUNT(DISTINCT PR.doctor_id) > (
    SELECT AVG(sub.doctor_count)
    FROM (
        SELECT COUNT(DISTINCT doctor_id) AS doctor_count
        FROM PRESCRIPTION
        GROUP BY patient_id
    ) sub
);


QUERY 12 - COMPLEX (JOIN + GROUP BY + HAVING + SUBQUERY + COUNT DISTINCT)

Natural Language:
Find patients who received prescriptions from more doctors than the average patient and show their name with the number of doctors.

SQL:

SELECT PA.patient_id, PA.name, COUNT(DISTINCT PR.doctor_id) AS doctor_count
FROM PATIENT PA, PRESCRIPTION PR
WHERE PA.patient_id = PR.patient_id
GROUP BY PA.patient_id, PA.name
HAVING COUNT(DISTINCT PR.doctor_id) > (
    SELECT AVG(sub.doctor_count)
    FROM (
        SELECT COUNT(DISTINCT doctor_id) AS doctor_count
        FROM PRESCRIPTION
        GROUP BY patient_id
    ) sub
);


QUERY 13 - COMPLEX (MAX + JOIN + GROUP BY + SUBQUERY + ORDER BY DESC)

Natural Language:
Find the doctors with the max total prescribed quantity and show them with patient name, issue date, and total quantity, ordered in descending by quantity.

SQL:

SELECT D.Doctor_id, D.Name AS doctor_name,
       PR.rx_id, PA.name AS patient_name,
       PR.Issue_date,
       rxTotals.rx_total_qty
FROM Doctor D, Prescription PR, Patient PA,
     (
         SELECT PI.rx_id, SUM(PI.qty_prescribed) AS rx_total_qty
         FROM Prescription_Items PI
         GROUP BY PI.rx_id
     ) rxTotals
WHERE D.Doctor_id = PR.Doctor_id
  AND PR.Patient_id = PA.Patient_id
  AND PR.rx_id = rxTotals.rx_id
  AND D.Doctor_id IN
      (
          SELECT docTotals.Doctor_id
          FROM (
                   SELECT PR2.Doctor_id,
                          SUM(PI2.qty_prescribed) AS doctor_total_qty
                   FROM Prescription PR2, Prescription_Items PI2
                   WHERE PR2.rx_id = PI2.rx_id
                   GROUP BY PR2.Doctor_id
               ) docTotals
          WHERE docTotals.doctor_total_qty =
                (
                    SELECT MAX(sub.doctor_total_qty)
                    FROM (
                             SELECT PR3.Doctor_id,
                                    SUM(PI3.qty_prescribed) AS doctor_total_qty
                             FROM Prescription PR3, Prescription_Items PI3
                             WHERE PR3.rx_id = PI3.rx_id
                             GROUP BY PR3.Doctor_id
                         ) sub
                )
      )
ORDER BY rxTotals.rx_total_qty DESC;


QUERY 14 - Line-items for PENDING orders (3-table join)

Natural Language:
List all purchase order line items for orders whose Status = 'PENDING', and show the supplier name with each line item.

Relational Algebra:

$$\pi_{\text{Order\_id, Company\_name, Drug\_id, qty\_ordered, Unit\_cost}} (\sigma_{\text{Status='PENDING'}} (\text{PURCHASE\_ORDER}) \bowtie_{\text{Supplier\_ID}} \text{SUPPLIER} \bowtie_{\text{Order\_id=Product\_id}} \text{PURCHASE\_ORDER\_ITEM})$$

SQL:

SELECT po.Order_id, s.Company_name, poi.Drug_id, poi.qty_ordered, poi.Unit_cost
FROM PURCHASE_ORDER po
JOIN SUPPLIER s ON s.Supplier_ID = po.Supplier_ID
JOIN PURCHASE_ORDER_ITEM poi ON poi.Product_id = po.Order_id
WHERE po.Status = 'PENDING';


QUERY 15 - Overdue orders (expected date passed, not delivered)

Natural Language:
List orders whose expected delivery date has passed but status is not 'DELIVERED', with supplier name.

Relational Algebra:

$$\pi_{\text{Order\_id, Company\_name, Expected\_delivery\_date, Status}} (\sigma_{\text{Expected\_delivery\_date} < \text{today} \land \text{Status} \neq \text{'DELIVERED'}} (\text{PURCHASE\_ORDER} \bowtie_{\text{Supplier\_ID}} \text{SUPPLIER}))$$

SQL:

SELECT po.Order_id, s.Company_name, po.Expected_delivery_date, po.Status
FROM PURCHASE_ORDER po
JOIN SUPPLIER s ON s.Supplier_ID = po.Supplier_ID
WHERE po.Expected_delivery_date < CURRENT_DATE
  AND po.Status <> 'DELIVERED'
ORDER BY po.Expected_delivery_date ASC;


QUERY 16 - Average unit cost per supplier per drug (AVG, GROUP BY)

Natural Language:
For each supplier and each drug, compute average unit_cost they charged.

SQL:

SELECT s.Supplier_ID, s.Company_name, poi.Drug_id,
       AVG(poi.Unit_cost) AS avg_unit_cost
FROM SUPPLIER s
JOIN PURCHASE_ORDER po ON po.Supplier_ID = s.Supplier_ID
JOIN PURCHASE_ORDER_ITEM poi ON poi.Product_id = po.Order_id
GROUP BY s.Supplier_ID, s.Company_name, poi.Drug_id;


QUERY 17 - Pending OR Overdue Suppliers (UNION)

Natural Language:
List suppliers who have at least one pending order OR at least one overdue (not delivered) order.

SQL:

SELECT DISTINCT s.Supplier_ID, s.Company_name
FROM SUPPLIER s
JOIN PURCHASE_ORDER po ON po.Supplier_ID = s.Supplier_ID
WHERE po.Status = 'PENDING'
UNION
SELECT DISTINCT s.Supplier_ID, s.Company_name
FROM SUPPLIER s
JOIN PURCHASE_ORDER po ON po.Supplier_ID = s.Supplier_ID
WHERE po.Expected_delivery_date < CURRENT_DATE
  AND po.Status <> 'DELIVERED';


QUERY 18 - Pending Orders with Stock Info (JOIN + WHERE)

Natural Language:
Show drugs from pending orders and their current stock level.

SQL:

SELECT po.Order_id, poi.Drug_id, poi.qty_ordered, il.qty_on_hand
FROM PURCHASE_ORDER po
JOIN PURCHASE_ORDER_ITEM poi ON poi.Product_id = po.Order_id
JOIN INVENTORY_LOT il ON il.Drug_id = poi.Drug_id
WHERE po.Status = 'PENDING';


QUERY 19 - Suppliers Who Have More Orders Than Average (SUBQUERY + COUNT + GROUP BY)

Natural Language:
Show suppliers whose number of orders is greater than the average number of orders per supplier.

SQL:

SELECT s.Supplier_ID, s.Company_name, COUNT(po.Order_id) AS order_count
FROM SUPPLIER s
JOIN PURCHASE_ORDER po ON po.Supplier_ID = s.Supplier_ID
GROUP BY s.Supplier_ID, s.Company_name
HAVING COUNT(po.Order_id) > (
    SELECT AVG(order_count)
    FROM (
        SELECT COUNT(Order_id) AS order_count
        FROM PURCHASE_ORDER
        GROUP BY Supplier_ID
    ) AS sub
);


QUERY 20 - SIMPLE (JOIN)

Natural Language:
List the Generic name associated with the specific drug 'Amoxicillin'.

Relational Algebra:

$$\pi_{\text{Generic\_name}} (\sigma_{\text{Drug\_Name='Amoxicillin'}} (\text{GENERICS} \bowtie_{\text{GENERICS.Drug\_Name} = \text{DRUG\_CATALOGUE.Drug\_Name}} \text{DRUG\_CATALOGUE}))$$

SQL:

SELECT G.Generic_name
FROM GENERICS G, DRUG_CATALOGUE DC
WHERE G.Drug_Name = DC.Drug_Name
  AND DC.Drug_Name = 'Amoxicillin';


Query 21 - Simple (Selection and Projection)

Natural Language:
List the Lot Batch IDs for all inventory items that have a unit cost greater than $50.00.

Relational Algebra:

$$\pi_{\text{LOT\_BATCH}} (\sigma_{\text{Unit\_cost} > 50} (\text{INVENTORY\_LOT}))$$

SQL:

SELECT Lot_batch_ID
FROM INVENTORY_LOT
WHERE Unit_cost > 50.00;


Query 22 - Simple (Join with 3 Relations)

Natural Language:
List the Insurance Company Name for every Dispense ID, ensuring that only dispenses that were covered by Insurance companies are displayed.

Relational Algebra:

$$\pi_{\text{Dispense\_id, Company}} (\text{DISPENSE} \bowtie_{\text{DISPENSE.Dispense\_id} = \text{PAYS.Dispense\_id}} (\text{PAYS} \bowtie_{\text{PAYS.Policy\_id} = \text{INSURANCE.Policy\_id}} \text{INSURANCE}))$$

SQL:

SELECT D.Dispense_id, I.Company
FROM DISPENSE D, PAYS P, INSURANCE I
WHERE D.Dispense_id = P.Dispense_id
  AND P.Policy_id = I.Policy_id;


Query 23 - Complex (Aggregation + Group by + Order by)

Natural Language:
Calculate the total inventory value for each Drug ID, and list them by highest to lowest value.

SQL:

SELECT Drug_id, SUM(qty_on_hand * Unit_cost) AS total_inventory_value
FROM INVENTORY_LOT
GROUP BY Drug_id
ORDER BY total_inventory_value DESC;


Query 24 - Complex (Subquery + Join)

Natural Language:
List the names of all patients who have had a prescription paid for by "X" Insurance company (X can be replaced by any insurance company name).

SQL:

SELECT name
FROM PATIENT
WHERE Patient_id IN (
    SELECT P.Patient_id
    FROM PRESCRIPTION PR
    JOIN DISPENSE D ON PR.rx_id = D.rx_id
    JOIN PAYS PY ON D.Dispense_id = PY.Dispense_id
    JOIN INSURANCE I ON PY.Policy_id = I.Policy_id
    WHERE I.Company = 'X'
);


Query 25 - Complex (SUBQUERY + AGGREGATION + GROUP BY)

Natural Language:
Find the drug forms (e.g., Tablet, Capsule) that have an average unit cost higher than the average unit cost of the entire inventory.

SQL:

SELECT Form, AVG(Unit_cost) AS Avg_Cost
FROM DRUG_CATALOGUE DC
JOIN INVENTORY_LOT IL ON DC.Drug_id = IL.Drug_id
GROUP BY Form
HAVING AVG(Unit_cost) > (
    SELECT AVG(Unit_cost)
    FROM INVENTORY_LOT
);
