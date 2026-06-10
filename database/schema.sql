-- ================================================================
--  Nama Database  : sakkabase_ncf
--  Sistem         : Sistem Rekomendasi Menu Sakka Base
--  Metode         : Neural Collaborative Filtering (NCF)
--  DBMS           : MySQL 8.x
--  Charset        : utf8mb4
-- ================================================================

CREATE DATABASE IF NOT EXISTS sakkabase_ncf
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE sakkabase_ncf;


-- ----------------------------------------------------------------
-- TABEL 1 : users
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
  COLLATE = utf8mb4_unicode_ci;


-- ----------------------------------------------------------------
-- TABEL 2 : menu_items
-- ----------------------------------------------------------------
CREATE TABLE menu_items (
    id         INT              NOT NULL AUTO_INCREMENT,
    item_id    VARCHAR(100)     NOT NULL,
    nama_menu  VARCHAR(150)     NOT NULL,
    kategori   VARCHAR(100)     NOT NULL,
    price      INT              NOT NULL DEFAULT 0 COMMENT 'Harga estimasi dalam Rupiah',
    created_at DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP
                                         ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_menu_items         PRIMARY KEY (id),
    CONSTRAINT uq_menu_items_item_id UNIQUE      (item_id)

) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;


-- ----------------------------------------------------------------
-- TABEL 3 : orders
-- Setiap baris = satu transaksi (bisa punya banyak item di order_details)
-- ----------------------------------------------------------------
CREATE TABLE orders (
    id         INT              NOT NULL AUTO_INCREMENT,
    user_id    INT              NOT NULL,
    tanggal    DATE             NOT NULL,
    total      INT              NOT NULL DEFAULT 0 COMMENT 'Total harga semua item',
    created_at DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_orders PRIMARY KEY (id),

    CONSTRAINT fk_orders_user_id
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    INDEX idx_orders_user_id (user_id),
    INDEX idx_orders_tanggal (tanggal)

) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci
  COMMENT = 'Transaksi pemesanan (header). Detail item ada di order_details.';


-- ----------------------------------------------------------------
-- TABEL 4 : order_details
-- Setiap baris = satu item dalam satu transaksi
-- ----------------------------------------------------------------
CREATE TABLE order_details (
    id           INT     NOT NULL AUTO_INCREMENT,
    order_id     INT     NOT NULL,
    menu_item_id INT     NOT NULL,
    qty          TINYINT NOT NULL DEFAULT 1,
    price        INT     NOT NULL DEFAULT 0 COMMENT 'Harga per item saat transaksi',

    CONSTRAINT pk_order_details PRIMARY KEY (id),

    CONSTRAINT fk_od_order_id
        FOREIGN KEY (order_id)
        REFERENCES orders(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_od_menu_item_id
        FOREIGN KEY (menu_item_id)
        REFERENCES menu_items(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    INDEX idx_od_order_id     (order_id),
    INDEX idx_od_menu_item_id (menu_item_id)

) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci
  COMMENT = 'Detail item per transaksi. Digunakan sebagai implicit feedback NCF.';


-- ----------------------------------------------------------------
-- TABEL 5 : recommendations
-- ----------------------------------------------------------------
CREATE TABLE recommendations (
    id           INT      NOT NULL AUTO_INCREMENT,
    user_id      INT      NOT NULL,
    menu_item_id INT      NOT NULL,
    `rank`       TINYINT  NOT NULL,
    score        FLOAT    NOT NULL,
    generated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_recommendations PRIMARY KEY (id),
    CONSTRAINT uq_rec_user_rank   UNIQUE (user_id, `rank`),
    CONSTRAINT uq_rec_user_item   UNIQUE (user_id, menu_item_id),

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
  COLLATE = utf8mb4_unicode_ci;


-- ----------------------------------------------------------------
-- TABEL 6 : model_status
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
    INDEX idx_model_status_status (status)

) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;


-- ----------------------------------------------------------------
-- SEED DATA : Akun Admin default  (password: admin123)
-- ----------------------------------------------------------------
INSERT INTO users (nama_lengkap, username, password, role, source)
VALUES (
    'Administrator',
    'admin',
    '$2b$12$O1gqvVRWCZgPj1OFOH/BLOswgZXkL8jBDMN0a1p/t7VCdzx8t7WI6',
    'admin',
    'registered'
);

SHOW TABLES;
-- Expected: 6 tabel — menu_items, model_status, order_details, orders, recommendations, users
