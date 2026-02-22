-- 1st Part No foreign Key COMPLETED
-- DOCTOR
INSERT INTO doctor VALUES
(701,'Dr. Lara Weiss','LIC-701','Main Street 10'),
(702,'Dr. Omar Khan','LIC-702','Park Avenue 22'),
(703,'Dr. Sofia Bauer','LIC-703','Clinic Road 3'),
(704,'Dr. Nils Fischer','LIC-704','River Lane 15'),
(705,'Dr. Mia Schmidt','LIC-705','Old Town 8'),
(706,'Dr. Jonas Meyer','LIC-706','Harbor View 5'),
(707,'Dr. Lina Novak','LIC-707','West End 19'),
(708,'Dr. David Stein','LIC-708','East Gate 6'),
(709,'Dr. Hana Yilmaz','LIC-709','South Street 40'),
(710,'Dr. Eric Vogel','LIC-710','North Square 11');

-- PATIENT
INSERT INTO patient VALUES
(601,'Amir Hassan','1992-05-12'),
(602,'Julia Klein','1988-11-03'),
(603,'Noah Becker','2001-02-18'),
(604,'Sara Ibrahim','1997-09-27'),
(605,'Lea Wagner','1979-04-09'),
(606,'Paul Schneider','1983-07-21'),
(607,'Mila Hartmann','1990-12-30'),
(608,'Tariq Ali','2004-06-14'),
(609,'Elena Rossi','1995-01-25'),
(610,'Hugo Martin','1986-03-08');

-- PHARMACIST
INSERT INTO pharmacist VALUES
(801,'Nora Brandt','2020-01-10',32000),
(802,'Felix Braun','2019-06-01',35000),
(803,'Aylin Demir','2021-03-15',30000),
(804,'Daniel Weber','2018-09-20',42000),
(805,'Zoe Krause','2022-02-05',28912),
(806,'Mehmet Kaya','2017-11-11',48000),
(807,'Hanna Koch','2016-07-07',52000),
(808,'Leon Richter','2023-05-02',29500),
(809,'Fatima Saad','2020-10-18',31000),
(810,'Marco Conti','2015-04-30',56000);

-- INSURANCE
INSERT INTO insurance VALUES
(901,'AOK'),
(902,'TK'),
(903,'Barmer'),
(904,'DAK'),
(905,'IKK'),
(906,'HEK'),
(907,'KKH'),
(908,'SBK'),
(909,'BKK'),
(910,'HanseMerkur');

-- SUPPLIER
INSERT INTO supplier VALUES
(1001,'MediSupply','Anna Wolf','Hamburg'),
(1002,'PharmaLogistics','Ben Adler','Hamburg'),
(1003,'HealthSource','Carla Stein','Hamburg'),
(1004,'Nordic Med','David Noor','Hamburg'),
(1005,'EuroPharm','Eva Lang','Hamburg'),
(1006,'CareChain','Fritz Hahn','Hamburg'),
(1007,'MedNext','Gina Koch','Hamburg'),
(1008,'VitaStock','Hakan Demir','Hamburg'),
(1009,'CityPharma','Iris Klein','Hamburg'),
(1010,'RapidRx','Jonas Ulm','Hamburg');

-- GENERICS
INSERT INTO generics VALUES
('Amoxicillin','Amoxicillin'),
('Ibuprofen','Ibuprofen'),
('Paracetamol','Acetaminophen'),
('Metformin','Metformin'),
('Atorvastatin','Atorvastatin'),
('Omeprazole','Omeprazole'),
('Amlodipine','Amlodipine'),
('Cetirizine','Cetirizine'),
('Salbutamol','Albuterol'),
('Azithromycin','Azithromycin');

--2nd PART: Drug and Inventory
-- DRUG_CATALOGUE
INSERT INTO drug_catalogue VALUES
(2001,'Amoxicillin','Capsule','500mg'),
(2002,'Ibuprofen','Tablet','400mg'),
(2003,'Paracetamol','Tablet','500mg'),
(2004,'Metformin','Tablet','1000mg'),
(2005,'Atorvastatin','Tablet','20mg'),
(2006,'Omeprazole','Capsule','20mg'),
(2007,'Amlodipine','Tablet','5mg'),
(2008,'Cetirizine','Tablet','10mg'),
(2009,'Salbutamol','Inhaler','100mcg'),
(2010,'Azithromycin','Tablet','500mg');

-- INVENTORY_LOT
INSERT INTO inventory_lot VALUES
(3001,'2027-12-31',2.5,200,2001),
(3002,'2027-11-30',1.1,300,2002),
(3003,'2028-01-31',0.9,250,2003),
(3004,'2027-10-31',3.2,150,2004),
(3005,'2027-09-30',4.1,180,2005),
(3006,'2027-08-31',2.0,220,2006),
(3007,'2027-07-31',1.7,190,2007),
(3008,'2027-06-30',0.8,260,2008),
(3009,'2027-05-31',5.5,120,2009),
(3010,'2027-04-30',6.0,140,2010);

--3rd Part: Perscription + Items
-- PRESCRIPTION  
INSERT INTO prescription VALUES 
(4001,'2026-02-01','Pending','High',601,701,801), 
(4002,'2026-02-02','Pending','Low',602,702,802),(4003,'2026-02-03','Pending','Medium',603,703,803),(4004,'2026-02-04','Pending','High',604,704,804), 
(4005,'2026-02-05','Pending','Low',605,705,805),(4006,'2026-02-06','Pending','Medium',606,706,806),(4007,'2026-02-07','Pending','High',607,707,807), 
(4008,'2026-02-08','Pending','Low',608,708,808),(4009,'2026-02-09','Pending','Medium',609,709,809),(4010,'2026-02-10','Pending','High',610,710,810); 

-- PRESCRIPTION_ITEMS 
INSERT INTO prescription_items VALUES 
(4001,2001,10,'Take with water','2x daily',1), 
(4002,2002,20,'After food','3x daily',0), 
(4003,2003,15,'Do not exceed','2x daily',1), 
(4004,2004,30,'With meals','2x daily',2), 
(4005,2005,30,'Evening','1x daily',3), 
(4006,2006,14,'Before breakfast','1x daily',1), 
(4007,2007,28,'Same time daily','1x daily',2), 
(4008,2008,10,'If allergy','1x daily',0), 
(4009,2009,1,'When needed','PRN',0), 
(4010,2010,3,'Full course','1x daily',0); 

-- 4th Part: Dispense + Item
-- DISPENSE
INSERT INTO dispense VALUES 
(5001,'2026-02-11',25,2.5,801,4001), 
(5002,'2026-02-11',22,2.2,802,4002), 
(5003,'2026-02-12',18,1.8,803,4003), 
(5004,'2026-02-12',30,3.0,804,4004), 
(5005,'2026-02-13',40,4.0,805,4005), 
(5006,'2026-02-13',28,2.8,806,4006), 
(5007,'2026-02-14',35,3.5,807,4007), 
(5008,'2026-02-14',15,1.5,808,4008), 
(5009,'2026-02-15',50,5.0,809,4009), 
(5010,'2026-02-15',60,6.0,810,4010); 

-- DISPENSED_ITEMS 
INSERT INTO dispensed_items VALUES 
(6001,3,5001,3001), 
(6002,5,5002,3002), 
(6003,4,5003,3003), 
(6004,6,5004,3004), 
(6005,2,5005,3005), 
(6006,2,5006,3006), 
(6007,1,5007,3007), 
(6008,1,5008,3008), 
(6009,1,5009,3009), 
(6010,1,5010,3010); 

-- 5th Part: Purchase + Pays
-- PURCHASE_ORDER 
INSERT INTO purchase_order VALUES 
(7001,'2026-01-05','2026-01-10','DELIVERED',1001), 
(7002,'2026-01-06','2026-01-12','DELIVERED',1002),(7003,'2026-01-10','2026-01-18','DELIVERED',1003),(7004,'2026-01-12','2026-01-20','DELIVERED',1004),(7005,'2026-01-15','2026-01-22','DELIVERED',1005),(7006,'2026-01-18','2026-01-25','PENDING',1006), 
(7007,'2026-01-20','2026-01-27','PENDING',1007), 
(7008,'2026-01-22','2026-01-30','PENDING',1008),(7009,'2026-01-24','2026-02-01','CANCELLED',1009),(7010,'2026-01-26','2026-02-03','PENDING',1010); 

-- PURCHASE_ORDER_ITEM 
INSERT INTO purchase_order_item VALUES 
(7001,2001,100,2.4), 
(7002,2002,150,1.0), 
(7003,2003,120,0.85), 
(7004,2004,80,3.1), 
(7005,2005,90,4.0), 
(7006,2006,110,1.95), 
(7007,2007,100,1.6), 
(7008,2008,140,0.75), 
(7009,2009,60,5.3), 
(7010,2010,70,5.8); 

-- PAYS 
INSERT INTO pays VALUES 
(5001,901,10), 
(5002,902,8), 
(5003,903,5), 
(5004,904,12), 
(5005,905,15), 
(5006,906,7), 
(5007,907,10), 
(5008,908,4), 
(5009,909,20), 
(5010,910,25); 

