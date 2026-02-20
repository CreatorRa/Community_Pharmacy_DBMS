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

