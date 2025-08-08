-- Migration inicial para el sistema de RRHH
CREATE TABLE workers (
    id SERIAL PRIMARY KEY,
    employee_number VARCHAR(20) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    curp VARCHAR(18) UNIQUE NOT NULL,
    rfc VARCHAR(13) UNIQUE NOT NULL,
    address VARCHAR(200),
    phone VARCHAR(20),
    hire_date DATE,
    position VARCHAR(100),
    contract_type VARCHAR(50),
    area_project VARCHAR(100),
    daily_salary NUMERIC(10,2) DEFAULT 0,
    photo_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    role VARCHAR(20) NOT NULL,
    worker_id INTEGER REFERENCES workers(id)
);

CREATE TABLE worker_documents (
    id SERIAL PRIMARY KEY,
    worker_id INTEGER NOT NULL REFERENCES workers(id),
    doc_type VARCHAR(20) NOT NULL,
    file_path VARCHAR(255) NOT NULL
);

CREATE TABLE worker_cardex (
    id SERIAL PRIMARY KEY,
    worker_id INTEGER NOT NULL REFERENCES workers(id),
    event_type VARCHAR(50) NOT NULL,
    description TEXT,
    event_date DATE DEFAULT CURRENT_DATE
);

CREATE TABLE attendance_records (
    id SERIAL PRIMARY KEY,
    worker_id INTEGER NOT NULL REFERENCES workers(id),
    check_in TIMESTAMP NOT NULL,
    check_out TIMESTAMP,
    incidence VARCHAR(20) DEFAULT 'none',
    notes TEXT
);

CREATE TABLE permits (
    id SERIAL PRIMARY KEY,
    worker_id INTEGER NOT NULL REFERENCES workers(id),
    permit_type VARCHAR(20) NOT NULL,
    start TIMESTAMP NOT NULL,
    "end" TIMESTAMP NOT NULL,
    justification TEXT,
    evidence_path VARCHAR(255),
    status VARCHAR(20) DEFAULT 'pending',
    approved_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE incidents (
    id SERIAL PRIMARY KEY,
    worker_id INTEGER NOT NULL REFERENCES workers(id),
    incident_type VARCHAR(50) NOT NULL,
    description TEXT,
    evidence_path VARCHAR(255),
    status VARCHAR(20) DEFAULT 'open',
    responsible_id INTEGER REFERENCES users(id),
    comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE payrolls (
    id SERIAL PRIMARY KEY,
    worker_id INTEGER NOT NULL REFERENCES workers(id),
    week_start DATE NOT NULL,
    base_salary NUMERIC(10,2) NOT NULL,
    days_worked INTEGER DEFAULT 0,
    overtime_hours NUMERIC(5,2) DEFAULT 0,
    overtime_rate NUMERIC(5,2) DEFAULT 1.5,
    bonuses NUMERIC(10,2) DEFAULT 0,
    deductions NUMERIC(10,2) DEFAULT 0,
    permit_unpaid_hours NUMERIC(5,2) DEFAULT 0,
    total_pay NUMERIC(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
