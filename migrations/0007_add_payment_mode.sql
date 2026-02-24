ALTER TABLE client_payment ADD COLUMN IF NOT EXISTS payment_mode VARCHAR(50) DEFAULT 'neft';
