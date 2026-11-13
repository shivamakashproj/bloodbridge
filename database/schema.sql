-- ====================================================================
-- BloodBridge Database Schema Blueprint (MySQL 8.0+ / MariaDB)
-- File: database/schema.sql
-- Designed for BloodBridge Healthcare & LifeFlow Network
-- ====================================================================

-- 1. DATABASE CREATION AND INITIALIZATION
CREATE DATABASE IF NOT EXISTS `bloodbridge`
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE `bloodbridge`;

-- --------------------------------------------------------------------
-- 2. DROP TABLES IN REVERSE ORDER OF FOREIGN KEY DEPENDENCY
-- --------------------------------------------------------------------
DROP TABLE IF EXISTS `campaign_registration`;
DROP TABLE IF EXISTS `campaign`;
DROP TABLE IF EXISTS `blood_request`;
DROP TABLE IF EXISTS `donor`;
DROP TABLE IF EXISTS `contact_message`;
DROP TABLE IF EXISTS `newsletter_subscriber`;
DROP TABLE IF EXISTS `user`;

-- --------------------------------------------------------------------
-- 3. TABLE DEFINITIONS (DDL MATCHING MODELS.PY)
-- --------------------------------------------------------------------

-- Table: user (Authentication & Role Access Control)
CREATE TABLE `user` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `username` VARCHAR(80) NOT NULL UNIQUE,
  `email` VARCHAR(120) NOT NULL UNIQUE,
  `password_hash` VARCHAR(256) NOT NULL,
  `role` VARCHAR(20) NOT NULL DEFAULT 'customer', -- 'customer', 'hoster', 'admin'
  `is_admin` TINYINT(1) NOT NULL DEFAULT 0,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX `idx_user_role` (`role`),
  INDEX `idx_user_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: donor (Voluntary Blood Donors Registry)
CREATE TABLE `donor` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NULL,
  `full_name` VARCHAR(100) NOT NULL,
  `blood_group` VARCHAR(5) NOT NULL, -- 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'
  `phone` VARCHAR(20) NOT NULL,
  `city` VARCHAR(50) NOT NULL,
  `last_donated` DATE NULL,
  `is_available` TINYINT(1) NOT NULL DEFAULT 1,
  CONSTRAINT `fk_donor_user`
    FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
    ON DELETE SET NULL ON UPDATE CASCADE,
  INDEX `idx_donor_blood_city` (`blood_group`, `city`),
  INDEX `idx_donor_available` (`is_available`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: blood_request (Emergency Patient Requisitions)
CREATE TABLE `blood_request` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NULL,
  `patient_name` VARCHAR(100) NOT NULL,
  `blood_group_required` VARCHAR(5) NOT NULL,
  `units_required` INT NOT NULL DEFAULT 1,
  `hospital_name` VARCHAR(150) NOT NULL,
  `city` VARCHAR(50) NOT NULL,
  `contact_phone` VARCHAR(20) NOT NULL,
  `status` VARCHAR(20) NOT NULL DEFAULT 'Pending', -- 'Pending', 'Approved', 'Rejected', 'Fulfilled'
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `fk_bloodreq_user`
    FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
    ON DELETE SET NULL ON UPDATE CASCADE,
  INDEX `idx_req_status` (`status`),
  INDEX `idx_req_blood_city` (`blood_group_required`, `city`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: campaign (Community Blood Donation Camps / Drives)
CREATE TABLE `campaign` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NULL,
  `title` VARCHAR(200) NOT NULL,
  `host_name` VARCHAR(200) NULL, -- College / Hospital / NGO Organizer
  `host_type` VARCHAR(50) NULL,  -- 'College', 'Hospital', 'NGO', 'Corporate'
  `contact_email` VARCHAR(120) NULL,
  `contact_phone` VARCHAR(20) NULL,
  `date` DATE NOT NULL,
  `time_start` TIME NOT NULL,
  `time_end` TIME NOT NULL,
  `location` VARCHAR(200) NOT NULL,
  `city` VARCHAR(50) NOT NULL,
  `description` TEXT NULL,
  `status` VARCHAR(20) NOT NULL DEFAULT 'Pending', -- 'Pending', 'Approved', 'Rejected'
  CONSTRAINT `fk_campaign_user`
    FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
    ON DELETE SET NULL ON UPDATE CASCADE,
  INDEX `idx_campaign_date` (`date`),
  INDEX `idx_campaign_status` (`status`),
  INDEX `idx_campaign_city` (`city`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: campaign_registration (Donor RSVPs for Drives)
CREATE TABLE `campaign_registration` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `campaign_id` INT NOT NULL,
  `user_id` INT NOT NULL,
  `donor_name` VARCHAR(100) NOT NULL,
  `phone` VARCHAR(20) NOT NULL,
  `age` INT NOT NULL,
  `blood_group` VARCHAR(10) NOT NULL,
  `address` VARCHAR(255) NULL,
  `city` VARCHAR(50) NOT NULL,
  `medical_notes` TEXT NULL,
  `registration_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `fk_reg_campaign`
    FOREIGN KEY (`campaign_id`) REFERENCES `campaign` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_reg_user`
    FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  INDEX `idx_reg_camp` (`campaign_id`),
  INDEX `idx_reg_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: contact_message (Public Inquiries & Volunteer Messages)
CREATE TABLE `contact_message` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(100) NOT NULL,
  `email` VARCHAR(120) NOT NULL,
  `phone` VARCHAR(20) NULL,
  `blood_group` VARCHAR(10) NULL,
  `city` VARCHAR(50) NULL,
  `message` TEXT NOT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: newsletter_subscriber (Emergency Broadcast Alert Subscriptions)
CREATE TABLE `newsletter_subscriber` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `email` VARCHAR(120) NOT NULL UNIQUE,
  `subscribed_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 4. OPTIONAL: CREATE ADMIN USER INSTRUCTIONS / EXAMPLE
-- --------------------------------------------------------------------
-- To create an admin account, you have two options:
--
-- OPTION A (Recommended):
-- Configure ADMIN_USERNAME and ADMIN_PASSWORD in your .env file, then run:
--   python scripts/init_db.py
--
-- OPTION B (Manual SQL):
-- Generate a secure password hash using Python:
--   python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('your_password_here'))"
-- Then run the following query with your username, email, and generated hash:
--
-- INSERT INTO `user` (`username`, `email`, `password_hash`, `role`, `is_admin`, `created_at`)
-- VALUES ('admin', 'admin@example.com', '<generated_password_hash>', 'admin', 1, NOW());
-- --------------------------------------------------------------------
