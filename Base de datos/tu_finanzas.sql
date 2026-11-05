-- =====================================================
-- Base de datos: tu_finanzas (MySQL / MySQL Workbench)
-- Tablas: roles, usuarios, categorias, metodos_pago, suscripciones,
--         gastos, pagos_suscripcion, alertas, presupuestos, configuracion
-- Vistas: v_resumen_usuario, v_gastos_por_categoria, v_proximos_cobros
-- =====================================================
CREATE DATABASE IF NOT EXISTS tu_finanzas CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE tu_finanzas;

CREATE TABLE IF NOT EXISTS roles (
    id     INT PRIMARY KEY,
    nombre VARCHAR(30) NOT NULL UNIQUE
) ENGINE=InnoDB;
INSERT IGNORE INTO roles (id, nombre) VALUES (1, 'administrador'), (2, 'usuario');

CREATE TABLE IF NOT EXISTS usuarios (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    nombre          VARCHAR(20) NOT NULL UNIQUE,
    nombre_completo VARCHAR(80) NULL,
    correo          VARCHAR(100) NULL UNIQUE,
    sal             VARCHAR(32) NOT NULL,
    clave           VARCHAR(64) NOT NULL,
    rol_id          INT NOT NULL DEFAULT 2,
    activo          TINYINT(1) NOT NULL DEFAULT 1,
    fecha_registro  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ultimo_acceso   TIMESTAMP NULL DEFAULT NULL,
    CONSTRAINT fk_usuario_rol FOREIGN KEY (rol_id) REFERENCES roles(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS categorias (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    nombre      VARCHAR(40) NOT NULL UNIQUE,
    color       CHAR(7) NOT NULL DEFAULT '#cbd5e1',
    descripcion VARCHAR(100) NULL
) ENGINE=InnoDB;
INSERT IGNORE INTO categorias (nombre, color, descripcion) VALUES
    ('Suscripciones', '#93c5fd', 'Cobros recurrentes de servicios'),
    ('Alimentación', '#c4b5fd', 'Mercado y comidas'),
    ('Transporte', '#86efac', 'Buses, taxis y gasolina'),
    ('Entretenimiento', '#fca5a5', 'Salidas, cine y juegos'),
    ('Educación', '#fdba74', 'Cursos, libros y matrículas'),
    ('Salud', '#5eead4', 'Citas, medicinas y seguros'),
    ('Servicios', '#a5b4fc', 'Agua, luz, internet'),
    ('Otros', '#fde68a', 'Gastos sin categoría');

CREATE TABLE IF NOT EXISTS metodos_pago (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    nombre     VARCHAR(40) NOT NULL,
    tipo       ENUM('debito','credito','efectivo','transferencia','otro') NOT NULL DEFAULT 'otro',
    CONSTRAINT uq_metodo_usuario UNIQUE (usuario_id, nombre),
    CONSTRAINT fk_metodo_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS suscripciones (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id     INT NOT NULL,
    categoria_id   INT NULL,
    metodo_pago_id INT NULL,
    nombre         VARCHAR(60) NOT NULL,
    descripcion    VARCHAR(150) NULL,
    valor          DECIMAL(12,2) NOT NULL,
    periodicidad   ENUM('semanal','mensual','anual') NOT NULL DEFAULT 'mensual',
    dia_cobro      TINYINT NOT NULL,
    fecha_inicio   DATE NULL,
    activa         TINYINT(1) NOT NULL DEFAULT 1,
    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_susc_valor CHECK (valor > 0),
    CONSTRAINT ck_susc_dia CHECK (dia_cobro BETWEEN 1 AND 31),
    CONSTRAINT fk_susc_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    CONSTRAINT fk_susc_categoria FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE SET NULL,
    CONSTRAINT fk_susc_metodo FOREIGN KEY (metodo_pago_id) REFERENCES metodos_pago(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS gastos (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id     INT NOT NULL,
    categoria_id   INT NOT NULL,
    metodo_pago_id INT NULL,
    descripcion    VARCHAR(100) NOT NULL,
    valor          DECIMAL(12,2) NOT NULL,
    fecha          DATE NOT NULL,
    CONSTRAINT ck_gasto_valor CHECK (valor > 0),
    CONSTRAINT fk_gasto_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    CONSTRAINT fk_gasto_categoria FOREIGN KEY (categoria_id) REFERENCES categorias(id),
    CONSTRAINT fk_gasto_metodo FOREIGN KEY (metodo_pago_id) REFERENCES metodos_pago(id) ON DELETE SET NULL,
    INDEX idx_gastos_fecha (usuario_id, fecha)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS pagos_suscripcion (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    suscripcion_id  INT NOT NULL,
    fecha_pago      DATE NOT NULL,
    valor           DECIMAL(12,2) NOT NULL,
    estado          ENUM('pagado','pendiente','omitido') NOT NULL DEFAULT 'pagado',
    CONSTRAINT fk_pago_susc FOREIGN KEY (suscripcion_id) REFERENCES suscripciones(id) ON DELETE CASCADE,
    INDEX idx_pagos_fecha (suscripcion_id, fecha_pago)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS alertas (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id     INT NOT NULL,
    suscripcion_id INT NULL,
    mensaje        VARCHAR(200) NOT NULL,
    fecha_alerta   DATE NOT NULL,
    leida          TINYINT(1) NOT NULL DEFAULT 0,
    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_alerta_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    CONSTRAINT fk_alerta_susc FOREIGN KEY (suscripcion_id) REFERENCES suscripciones(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS presupuestos (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id    INT NOT NULL,
    categoria_id  INT NOT NULL,
    monto_limite  DECIMAL(12,2) NOT NULL,
    CONSTRAINT ck_presupuesto_monto CHECK (monto_limite > 0),
    CONSTRAINT uq_presupuesto UNIQUE (usuario_id, categoria_id),
    CONSTRAINT fk_presupuesto_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    CONSTRAINT fk_presupuesto_categoria FOREIGN KEY (categoria_id) REFERENCES categorias(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS configuracion (
    usuario_id     INT PRIMARY KEY,
    dias_alerta    INT NOT NULL DEFAULT 3,
    moneda         CHAR(3) NOT NULL DEFAULT 'COP',
    notificaciones TINYINT(1) NOT NULL DEFAULT 1,
    CONSTRAINT ck_config_dias CHECK (dias_alerta BETWEEN 1 AND 15),
    CONSTRAINT fk_config_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE OR REPLACE VIEW v_resumen_usuario AS
SELECT u.id AS usuario_id, u.nombre,
    COALESCE((SELECT SUM(CASE s.periodicidad WHEN 'anual' THEN s.valor / 12
                                             WHEN 'semanal' THEN s.valor * 4
                                             ELSE s.valor END)
              FROM suscripciones s WHERE s.usuario_id = u.id AND s.activa = 1), 0) AS total_suscripciones,
    COALESCE((SELECT SUM(g.valor) FROM gastos g WHERE g.usuario_id = u.id), 0) AS total_gastos
FROM usuarios u;

CREATE OR REPLACE VIEW v_gastos_por_categoria AS
SELECT g.usuario_id, c.nombre AS categoria, SUM(g.valor) AS total
FROM gastos g JOIN categorias c ON c.id = g.categoria_id
GROUP BY g.usuario_id, c.nombre;

CREATE OR REPLACE VIEW v_proximos_cobros AS
SELECT s.usuario_id, s.id AS suscripcion_id, s.nombre, s.valor, s.dia_cobro,
    CASE WHEN s.dia_cobro >= DAY(CURDATE()) THEN s.dia_cobro - DAY(CURDATE())
         ELSE DAY(LAST_DAY(CURDATE())) - DAY(CURDATE()) + s.dia_cobro END AS dias_restantes
FROM suscripciones s WHERE s.activa = 1;

-- ---------- datos de ejemplo (usuario demo / clave 1234) ----------
INSERT IGNORE INTO usuarios (id, nombre, nombre_completo, correo, sal, clave, rol_id) VALUES
    (1, 'demo', 'Usuario de Demostración', 'demo@tufinanzas.com',
     '69e6c65cda15a8c4fffb3c734c8d0196',
     '934cba54dc588fb232d8ae720b3434da3fb3ba919650449c2f8132fa76f4dda2', 2);

INSERT IGNORE INTO metodos_pago (id, usuario_id, nombre, tipo) VALUES
    (1, 1, 'Tarjeta débito', 'debito'),
    (2, 1, 'Tarjeta crédito', 'credito'),
    (3, 1, 'Efectivo', 'efectivo');

INSERT IGNORE INTO suscripciones (id, usuario_id, categoria_id, metodo_pago_id, nombre, descripcion, valor, periodicidad, dia_cobro, fecha_inicio, activa) VALUES
    (1, 1, (SELECT id FROM categorias WHERE nombre = 'Suscripciones'), 2, 'Spotify', 'Música en streaming', 19900, 'mensual', 6, '2026-01-06', 1),
    (2, 1, (SELECT id FROM categorias WHERE nombre = 'Suscripciones'), 2, 'Netflix', 'Series y películas', 24900, 'mensual', 15, '2026-01-15', 1),
    (3, 1, (SELECT id FROM categorias WHERE nombre = 'Suscripciones'), 1, 'Dropbox', 'Almacenamiento en la nube', 11900, 'mensual', 20, '2026-02-20', 0);

INSERT IGNORE INTO gastos (id, usuario_id, categoria_id, metodo_pago_id, descripcion, valor, fecha) VALUES
    (1, 1, (SELECT id FROM categorias WHERE nombre = 'Alimentación'), 3, 'Mercado del mes', 64000, '2026-10-02'),
    (2, 1, (SELECT id FROM categorias WHERE nombre = 'Transporte'), 1, 'Transmilenio', 48000, '2026-10-05'),
    (3, 1, (SELECT id FROM categorias WHERE nombre = 'Otros'), 3, 'Salidas', 64000, '2026-10-10');

INSERT IGNORE INTO pagos_suscripcion (id, suscripcion_id, fecha_pago, valor, estado) VALUES
    (1, 1, '2026-08-06', 19900, 'pagado'),
    (2, 1, '2026-09-06', 19900, 'pagado'),
    (3, 1, '2026-10-06', 19900, 'pagado'),
    (4, 2, '2026-09-15', 24900, 'pagado'),
    (5, 2, '2026-10-15', 24900, 'pagado'),
    (6, 3, '2026-03-20', 11900, 'omitido');

INSERT IGNORE INTO alertas (id, usuario_id, suscripcion_id, mensaje, fecha_alerta, leida) VALUES
    (1, 1, 2, 'Netflix cobra $ 24.900 el 15 de noviembre', '2026-11-12', 0);

INSERT IGNORE INTO presupuestos (id, usuario_id, categoria_id, monto_limite) VALUES
    (1, 1, (SELECT id FROM categorias WHERE nombre = 'Alimentación'), 300000),
    (2, 1, (SELECT id FROM categorias WHERE nombre = 'Transporte'), 120000);

INSERT IGNORE INTO configuracion (usuario_id, dias_alerta, moneda, notificaciones) VALUES (1, 3, 'COP', 1);

-- ---------- consultas utiles ----------
-- SELECT * FROM v_resumen_usuario;
-- SELECT * FROM v_gastos_por_categoria WHERE usuario_id = 1;
-- SELECT * FROM v_proximos_cobros WHERE usuario_id = 1 AND dias_restantes <= 3;
