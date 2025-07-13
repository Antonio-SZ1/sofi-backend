CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    rfc VARCHAR(13) UNIQUE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE loans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    amount NUMERIC(15, 2) NOT NULL CHECK (amount > 0),
    interest_rate NUMERIC(5, 4) NOT NULL CHECK (interest_rate >= 0),
    term_months INT NOT NULL CHECK (term_months > 0),
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE', -- e.g., ACTIVE, PAID_OFF, DEFAULTED
    granted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    current_balance NUMERIC(15, 2) NOT NULL
);

CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    loan_id UUID NOT NULL REFERENCES loans(id) ON DELETE CASCADE,
    amount NUMERIC(15, 2) NOT NULL CHECK (amount > 0),
    payment_date TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_clients_email ON clients(email);
CREATE INDEX idx_clients_rfc ON clients(rfc);
CREATE INDEX idx_loans_client_id ON loans(client_id);
CREATE INDEX idx_loans_status ON loans(status);
CREATE INDEX idx_payments_loan_id ON payments(loan_id);

CREATE ROLE replica_user WITH REPLICATION PASSWORD 'replicapassword' LOGIN;