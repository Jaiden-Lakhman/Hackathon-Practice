BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "bills" (
	"bills_id"	INTEGER,
	"house_id"	INTEGER NOT NULL,
	"utility_type"	TEXT NOT NULL,
	"amount_due"	REAL NOT NULL,
	"due_date"	TEXT NOT NULL,
	"payment_status"	TEXT NOT NULL,
	"latest_reading"	REAL,
	PRIMARY KEY("bills_id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "customer" (
	"customer_id"	INTEGER NOT NULL,
	"first_name"	TEXT NOT NULL,
	"surname"	TEXT NOT NULL,
	"password"	TEXT NOT NULL,
	PRIMARY KEY("customer_id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "house" (
	"house_id"	INTEGER,
	"customer_id"	INTEGER,
	"postcode"	TEXT NOT NULL,
	"move_date"	TEXT,
	"is_moving"	TEXT,
	PRIMARY KEY("house_id" AUTOINCREMENT)
);
INSERT INTO "bills" VALUES (1,1,'gas',110.9,'29/09/2026','unpaid',298.5);
INSERT INTO "customer" VALUES (1,'test','user','password');
INSERT INTO "house" VALUES (1,1,'LE7 XXX',NULL,NULL);
COMMIT;
