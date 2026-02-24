DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'client_payment' AND column_name = 'payment_stage') THEN
        ALTER TABLE client_payment ADD COLUMN payment_stage VARCHAR(50) DEFAULT 'other';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'client_payment' AND column_name = 'notes') THEN
        ALTER TABLE client_payment ADD COLUMN notes TEXT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'client_payment' AND column_name = 'is_tds_deducted') THEN
        ALTER TABLE client_payment ADD COLUMN is_tds_deducted BOOLEAN DEFAULT FALSE;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'client_payment' AND column_name = 'tds_amount') THEN
        ALTER TABLE client_payment ADD COLUMN tds_amount NUMERIC(15, 2) DEFAULT 0;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'client_payment' AND column_name = 'received_by_account') THEN
        ALTER TABLE client_payment ADD COLUMN received_by_account VARCHAR(100);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'client_payment' AND column_name = 'transaction_type') THEN
        ALTER TABLE client_payment ADD COLUMN transaction_type VARCHAR(20) DEFAULT 'credit';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'client_payment' AND column_name = 'reference_number') THEN
        ALTER TABLE client_payment ADD COLUMN reference_number VARCHAR(100);
    END IF;
END $$;
