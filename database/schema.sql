-- ================================================================
--  Nama Database  : sakkabase_ncf
--  Sistem         : Sistem Rekomendasi Menu Sakka Base
--  Metode         : Neural Collaborative Filtering (NCF)
--  DBMS           : MySQL 8.x
--  Charset        : utf8mb4 (mendukung karakter khusus Unicode penuh)
-- ================================================================

CREATE DATABASE IF NOT EXISTS sakkabase_ncf
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE sakkabase_ncf;


-- ----------------------------------------------------------------
-- TABEL 1 : users
-- Fungsi   : Menyimpan akun Admin, User terdaftar, dan entitas
--            historis No Transaksi kafe
-- ----------------------------------------------------------------
CREATE TABLE users (
    id           INT                              NOT NULL AUTO_INCREMENT,
    nama_lengkap VARCHAR(100)                     NOT NULL,
    username     VARCHAR(50)                      NOT NULL,
    password     VARCHAR(255)                         NULL,
    role         ENUM('admin','user')             NOT NULL DEFAULT 'user',
    source       ENUM('historical','registered')  NOT NULL DEFAULT 'registered',
    created_at   DATETIME                         NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_users          PRIMARY KEY (id),
    CONSTRAINT uq_users_username UNIQUE      (username)

) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci
  COMMENT = 'Akun seluruh pengguna: Admin, User terdaftar, dan entitas historis';


-- ----------------------------------------------------------------
-- TABEL 2 : menu_items
-- Fungsi   : Data master katalog menu kafe
-- ----------------------------------------------------------------
CREATE TABLE menu_items (
    id         INT          NOT NULL AUTO_INCREMENT,
    item_id    VARCHAR(100) NOT NULL,
    nama_menu  VARCHAR(150) NOT NULL,
    kategori   VARCHAR(100) NOT NULL,
    created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
                                     ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_menu_items         PRIMARY KEY (id),
    CONSTRAINT uq_menu_items_item_id UNIQUE      (item_id)

) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci
  COMMENT = 'Data master katalog menu kafe Sakka Base';


-- ----------------------------------------------------------------
-- TABEL 3 : orders
-- Fungsi   : Riwayat interaksi positif sebagai implicit feedback NCF
-- ----------------------------------------------------------------
CREATE TABLE orders (
    id           INT      NOT NULL AUTO_INCREMENT,
    user_id      INT      NOT NULL,
    menu_item_id INT      NOT NULL,
    tanggal      DATE     NOT NULL,
    created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_orders PRIMARY KEY (id),

    CONSTRAINT fk_orders_user_id
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_orders_menu_item_id
        FOREIGN KEY (menu_item_id)
        REFERENCES menu_items(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    INDEX idx_orders_user_id      (user_id),
    INDEX idx_orders_menu_item_id (menu_item_id),
    INDEX idx_orders_tanggal      (tanggal)

) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci
  COMMENT = 'Riwayat pemesanan positif sebagai implicit feedback model NCF';


-- ----------------------------------------------------------------
-- TABEL 4 : recommendations
-- Fungsi   : Cache Top-10 rekomendasi model NCF per pengguna
-- ----------------------------------------------------------------
CREATE TABLE recommendations (
    id           INT      NOT NULL AUTO_INCREMENT,
    user_id      INT      NOT NULL,
    menu_item_id INT      NOT NULL,
    `rank`       TINYINT  NOT NULL,
    score        FLOAT    NOT NULL,
    generated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_recommendations  PRIMARY KEY (id),
    CONSTRAINT uq_rec_user_rank    UNIQUE (user_id, `rank`),
    CONSTRAINT uq_rec_user_item    UNIQUE (user_id, menu_item_id),

    CONSTRAINT fk_rec_user_id
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_rec_menu_item_id
        FOREIGN KEY (menu_item_id)
        REFERENCES menu_items(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    INDEX idx_rec_user_id      (user_id),
    INDEX idx_rec_menu_item_id (menu_item_id)

) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci
  COMMENT = 'Cache hasil Top-10 rekomendasi model NCF per pengguna';


-- ----------------------------------------------------------------
-- TABEL 5 : model_status
-- Fungsi   : Log riwayat pelatihan dan metrik evaluasi model NCF
-- ----------------------------------------------------------------
CREATE TABLE model_status (
    id          INT                              NOT NULL AUTO_INCREMENT,
    status      ENUM('training','ready','error') NOT NULL DEFAULT 'ready',
    model_path  VARCHAR(255)                     NOT NULL,
    hr_at_10    FLOAT                                NULL,
    ndcg_at_10  FLOAT                                NULL,
    trained_at  DATETIME                             NULL,
    error_log   TEXT                                 NULL,
    created_at  DATETIME                         NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_model_status PRIMARY KEY (id),

    INDEX idx_model_status_status     (status),
    INDEX idx_model_status_trained_at (trained_at)

) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci
  COMMENT = 'Log riwayat pelatihan dan status aktif model NCF';


-- ----------------------------------------------------------------
-- SEED DATA : Akun Admin default
-- Password default: 'admin123' (bcrypt hash)
-- Ganti password setelah login pertama
-- ----------------------------------------------------------------
INSERT INTO users (nama_lengkap, username, password, role, source)
VALUES (
    'Administrator',
    'admin',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewLkBR8nW5Ay5HUO',
    'admin',
    'registered'
);


-- ----------------------------------------------------------------
-- VERIFIKASI : Pastikan semua tabel berhasil dibuat
-- ----------------------------------------------------------------
SHOW TABLES;
-- Expected output: 5 tabel — menu_items, model_status, orders, recommendations, users
