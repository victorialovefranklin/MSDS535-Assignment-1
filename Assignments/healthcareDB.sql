DROP DATABASE IF EXISTS healthcareDB;
CREATE DATABASE healthcareDB;
USE healthcareDB;
CREATE TABLE EHR (
    patient_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    dob DATE,
    gender ENUM('Male', 'Female', 'Other'),
    contact_info VARCHAR(15),
    address TEXT,
    date_of_visit DATE,
    diagnosis TEXT,
    prescription TEXT,
    doctor_id INT,
    medical_history TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO EHR (first_name, last_name, dob, gender, contact_info, address, date_of_visit, diagnosis, prescription, doctor_id, medical_history)
VALUES
    ('John', 'Doe', '1985-10-22', 'Male', '123-456-7890', '123 Elm St, Springfield', '2024-11-06', 'Hypertension', 'Lisinopril 10mg daily', 1, 'No significant past medical history'),
    ('Jane', 'Smith', '1990-07-15', 'Female', '987-654-3210', '456 Oak St, Springfield', '2024-11-05', 'Type 2 Diabetes', 'Metformin 500mg twice daily', 2, 'Family history of diabetes');

SELECT * FROM EHR;