-- PIES Description Builder Database Setup

-- Parts table to store automotive parts information
CREATE TABLE IF NOT EXISTS parts (
    id INTEGER PRIMARY KEY,
    part_number VARCHAR(50) NOT NULL,
    product_category VARCHAR(100) NOT NULL,
    brand VARCHAR(100) NOT NULL,
    part_type VARCHAR(100),
    engine_application TEXT,
    material VARCHAR(100),
    fitment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (part_number)
);

-- Descriptions table to store generated descriptions
CREATE TABLE IF NOT EXISTS descriptions (
    id INTEGER PRIMARY KEY,
    part_id INT NOT NULL,
    language_code VARCHAR(5) NOT NULL DEFAULT 'EN',
    maintenance_type CHAR(1) NOT NULL DEFAULT 'A',
    description_code VARCHAR(3) NOT NULL,
    sequence INT NOT NULL,
    description_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (part_id) REFERENCES parts(id) ON DELETE CASCADE,
    UNIQUE (part_id, description_code, sequence, language_code)
);

-- PIES description codes reference table
CREATE TABLE IF NOT EXISTS description_codes (
    code VARCHAR(3) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    max_length INT NOT NULL
);

-- Insert PIES description codes (Dummy Data for Demonstration Purposes)
-- UPDATE THIS TABLE WITH THE LATEST PIES DESCRIPTION CODES FROM THE PIES DESCRIPTION CODES REFERENCE TABLE
INSERT INTO description_codes (code, name, description, max_length) VALUES
('SHORT_DESC','Short Description','A brief label used when only a few characters can be displayed, providing a quick identification of the product. Use this once per part number.',12),
('FIT_SUMMARY','Fitment Summary','A basic summary showing general fitment details like compatible years, makes, and models (e.g., 2010-2015 Chevy Silverado). Do not include detailed fitment data here; that should be shared through ACES. For more than one fitment, repeat this code.',240),
('USER_WARNING','User Warning','Safety alerts or caution messages meant for the product user. These can be bullet points or simple statements. Each warning should be shared individually, with the option to assign a display order if needed. Also aligns with "Caution" qualifier types in ACES® Qdb.',500),
('FULL_DESC','Full Description','A complete description outlining what the product is. Only one description should be provided per part number using this code.',80),
('EXTENDED_DESC','Extended Description','A detailed, extended product description giving a broader overview of the item. Use this code only once per part number.',240),
('FEATURE_BENEFIT','Features and Benefits','Feature and benefit highlights explaining why the product stands out. Includes functional details or value-added characteristics. Each point should be sent separately and can be ordered using a sequence value. Supports the main marketing description.',240),
('IMPORTANT_INFO','Important Information','Important notes for both consumers and technicians about the product. These may be shared as single statements or grouped lists. Each entry should be provided individually. These align with "Informational" qualifier types in ACES® Qdb.',500),
('INSTALL_GUIDE','Install Guide','Helpful guidance or tips for installing the product. Do not use this for full installation instructions. Each suggestion should be sent separately, with optional display sequence. Tied to "Installation" qualifier types in ACES® Qdb.',500),
('INVOICE_DESC','Invoice Description','A description used specifically for invoices to describe the product being sold. This code should only appear once per part number.',40),
('SEARCH_TERMS','Search Terms','Keywords that help improve online search visibility for the product, including slang or common alternative terms. Provide one keyword per entry, repeating the code if needed for multiple words.',80),
('LABEL_TEXT','Label Information','A short label description meant for packaging or shelf/bin identification. Use only once per part number.',80),
('MARKETING_COPY','Marketing Information','A marketing paragraph designed to promote the product on web pages. It highlights key features, benefits, and unique selling points, supported by additional FEATURE_BENEFIT statements. Use this once per part number.',2000),
('CONDENSED_DESC','Condensed Description','A shortened product description intended for use where space is limited. Use only one entry per part number.',20),
('ALT_NAMES','Alternate Names','Alternate names or search-friendly terms for the product. Share one term at a time by repeating this code as needed.',80),
('TITLE_DESC','Title Description','An SEO-focused description combining the product name with key attributes for better online search results. Provide one entry per part number using this code.',200),
('TECH_TIP_INTRO','Technical Tip Introduction','An introductory paragraph for the technical tips section of a product page. Sets the stage for supporting TECH_TIP_DETAIL statements. Use only once per part number.',2000),
('TECH_TIP_DETAIL','Technical Tip Details','Individual technical tips offering advice or best practices for working with the product. Share each tip separately, with optional sequencing. Supports the main TECH_TIP_INTRO description.',240);

-- Sample parts data (Dummy Data for demonstration purposes)
-- UPDATE THIS TABLE WITH YOUR ACTUAL DATA
INSERT INTO parts (part_number, product_category, brand, part_type, engine_application, material, fitment) VALUES
('IC-5501', 'Ignition Coil', 'SparkMaster', 'Pencil Coil', 'V6, 3.5L, 2010-2018 Toyota Camry', 'High-grade copper windings', 'Direct fit for Toyota Camry'),
('OS-3302', 'Oxygen Sensor', 'SensorTech', 'Heated O2 Sensor', '4-cylinder, 2.4L, 2012-2018 Honda Accord', 'Ceramic and platinum', 'Downstream, Post-Catalytic'),
('FP-7701', 'Fuel Pump', 'FlowPro', 'Electric In-Tank', 'V8, 5.7L, 2015-2020 Chevy Silverado', 'Steel and polymer', 'Direct replacement'),
('BC-4401', 'Brake Caliper', 'StopRight', 'Front Caliper', '2014-2019 Ford F-150', 'Cast iron', 'Driver side, front'),
('TPS-6601', 'Throttle Position Sensor', 'ElectroSense', 'Digital TPS', 'V6, 3.6L, 2011-2017 Jeep Grand Cherokee', 'Polymer and metal', 'Direct OE replacement');

-- Create table for storing XML exports history
CREATE TABLE IF NOT EXISTS export_history (
    id INTEGER PRIMARY KEY,
    part_id INT,
    export_type VARCHAR(20) NOT NULL,
    export_content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (part_id) REFERENCES parts(id) ON DELETE SET NULL
);

-- Create users table for authentication (if needed)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (username),
    UNIQUE (email)
); 