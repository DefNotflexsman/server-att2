-- Create the core database if it doesn't exist
CREATE DATABASE IF NOT EXISTS server_network;
USE server_network;

-- 1. PLAYERS TABLE: Stores core identifiers and metadata
-- Uses BINARY(16) for UUIDs because string formats like CHAR(36) waste 20 bytes per row!
CREATE TABLE IF NOT EXISTS players (
    player_id INT AUTO_INCREMENT PRIMARY KEY,
    uuid BINARY(16) NOT NULL UNIQUE,
    username VARCHAR(16) NOT NULL,
    first_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_uuid (uuid),
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. ECONOMY TABLE: Keeps track of player balances
-- Uses DECIMAL instead of FLOAT or DOUBLE to completely avoid rounding errors with money fields
CREATE TABLE IF NOT EXISTS player_economy (
    player_id INT PRIMARY KEY,
    coins DECIMAL(15, 2) DEFAULT 0.00,
    gems INT DEFAULT 0,
    tokens INT DEFAULT 0,
    FOREIGN KEY (player_id) REFERENCES players(player_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 3. STATS TABLE: Tracks game metrics for leaderboards
CREATE TABLE IF NOT EXISTS player_stats (
    player_id INT PRIMARY KEY,
    kills INT DEFAULT 0,
    deaths INT DEFAULT 0,
    blocks_broken INT DEFAULT 0,
    playtime_seconds INT DEFAULT 0,
    FOREIGN KEY (player_id) REFERENCES players(player_id) ON DELETE CASCADE,
    INDEX idx_kills (kills DESC) -- Pre-sorted index optimizes live leaderboard queries instantly
) ENGINE=InnoDB;

-- 4. COSMETICS / UNLOCKS (Bridge Table to maximize database normalization)
CREATE TABLE IF NOT EXISTS player_cosmetics (
    player_id INT,
    cosmetic_id VARCHAR(64),
    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (player_id, cosmetic_id),
    FOREIGN KEY (player_id) REFERENCES players(player_id) ON DELETE CASCADE
) ENGINE=InnoDB;
