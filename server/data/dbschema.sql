-- Databse schema, use on new instance creation

PRAGMA foreign_keys = ON;

-- USERS: People who own cards
CREATE TABLE users (
    user_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name      VARCHAR(100) NOT NULL,
    phone_number   VARCHAR(15) UNIQUE NOT NULL,
    email          VARCHAR(100) UNIQUE NOT NULL,
    password       TEXT NOT NULL,  -- store hashed password
    role           TEXT NOT NULL CHECK (role IN ('admin', 'user')) NOT NULL DEFAULT 'user',
    registered_on  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- BUSINESSES: Merchants enrolled in the system
CREATE TABLE businesses (
    business_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    business_name  VARCHAR(150) NOT NULL,
    category       VARCHAR(100),
    contact_email  VARCHAR(100),
    contact_phone  VARCHAR(15),
    joined_on      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CARDS: The universal card that links to multiple memberships
CREATE TABLE cards (
    card_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    card_number    VARCHAR(50) UNIQUE NOT NULL,  -- Can be NFC ID, barcode, etc.
    user_id        INTEGER NOT NULL,
    issued_on      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- MEMBERSHIPS: Link between card & a specific business
CREATE TABLE memberships (
    membership_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id         INTEGER NOT NULL,
    business_id     INTEGER NOT NULL,
    membership_tier VARCHAR(50),  -- e.g., Gold, Silver, VIP
    joined_on       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    points_balance  INTEGER DEFAULT 0,
    UNIQUE (card_id, business_id),
    FOREIGN KEY (card_id) REFERENCES cards(card_id) ON DELETE CASCADE,
    FOREIGN KEY (business_id) REFERENCES businesses(business_id) ON DELETE CASCADE
);

-- TRANSACTIONS: When a membership is used for rewards or purchases
CREATE TABLE transactions (
    transaction_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    membership_id   INTEGER NOT NULL,
    txn_date        DATE NOT NULL,
    txn_time        TIME NOT NULL,
    amount          DECIMAL(10,2),
    points_earned   INTEGER DEFAULT 0,
    points_redeemed INTEGER DEFAULT 0,
    description     VARCHAR(255),
    FOREIGN KEY (membership_id) REFERENCES memberships(membership_id) ON DELETE CASCADE
);
