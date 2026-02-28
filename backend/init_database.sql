-- ============================================
-- SISTEMA INTEGRAL DE PROTECCIÓN DE ACTIVOS
-- Base de Datos PostgreSQL - Script de Inicialización
-- ============================================
-- Cliente: Victor Manuel De La Torre
-- Fecha: 28 Febrero 2026
-- ============================================

-- Extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- Para búsquedas de texto

-- ============================================
-- TABLAS MAESTRAS
-- ============================================

-- Organizaciones (Multi-tenant: Omnilife + SCI)
CREATE TABLE organizaciones (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT,
    logo_url TEXT,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Insertar organizaciones iniciales
INSERT INTO organizaciones (nombre, descripcion) VALUES
('Omnilife México', 'Corporativo Omnilife - Zona Sureste'),
('SCI DE OCCIDENTE', 'Servicios de Consultoría Integral');

-- Estados de México
CREATE TABLE estados (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    codigo VARCHAR(10),
    zona_sismica BOOLEAN DEFAULT FALSE,
    zona_costera BOOLEAN DEFAULT FALSE
);

-- Insertar estados de la zona sureste
INSERT INTO estados (nombre, codigo, zona_sismica, zona_costera) VALUES
('Campeche', 'CAM', FALSE, TRUE),
('Quintana Roo', 'QROO', FALSE, TRUE),
('Tabasco', 'TAB', FALSE, TRUE),
('Chiapas', 'CHIS', TRUE, FALSE),
('Oaxaca', 'OAX', TRUE, TRUE),
('Yucatán', 'YUC', FALSE, TRUE);

-- CEDIS (20 ubicaciones)
CREATE TABLE cedis (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    estado_id INT REFERENCES estados(id),
    municipio VARCHAR(100) NOT NULL,
    direccion TEXT,
    cp VARCHAR(10),
    superficie_m2 DECIMAL(10,2),
    personal_total INT DEFAULT 0,
    gerente VARCHAR(150),
    correo VARCHAR(150),
    telefono VARCHAR(20),
    latitud DECIMAL(10,6),
    longitud DECIMAL(10,6),
    organizacion_id INT REFERENCES organizaciones(id),
    activo BOOLEAN DEFAULT TRUE,
    notas TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Crear índices para búsquedas geográficas
CREATE INDEX idx_cedis_estado ON cedis(estado_id);
CREATE INDEX idx_cedis_municipio ON cedis(municipio);
CREATE INDEX idx_cedis_coords ON cedis(latitud, longitud);

-- ============================================
-- MÓDULO 1: MONITOREO DE SEGURIDAD
-- ============================================

CREATE TABLE eventos_seguridad (
    id SERIAL PRIMARY KEY,
    fecha TIMESTAMP NOT NULL,
    cedis_id INT REFERENCES cedis(id),
    tipo_evento VARCHAR(100) NOT NULL, 
    estado VARCHAR(50),
    
    -- Campos comunes
    descripcion TEXT,
    observaciones TEXT,
    
    -- Campos específicos (JSON para flexibilidad)
    datos_especificos JSONB,
    
    -- Campos extraídos para búsquedas
    hora VARCHAR(10),
    mes VARCHAR(20),
    dia_semana VARCHAR(20),
    responsable VARCHAR(150),
    estatus VARCHAR(50),
    
    -- Metadata
    organizacion_id INT REFERENCES organizaciones(id),
    usuario_registro_id INT,
    archivos_adjuntos TEXT[], -- Array de URLs
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_eventos_fecha ON eventos_seguridad(fecha DESC);
CREATE INDEX idx_eventos_tipo ON eventos_seguridad(tipo_evento);
CREATE INDEX idx_eventos_cedis ON eventos_seguridad(cedis_id);
CREATE INDEX idx_eventos_estatus ON eventos_seguridad(estatus);

-- ============================================
-- MÓDULO 2: CONTROL PRESUPUESTAL
-- ============================================

CREATE TABLE categorias_gasto (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT,
    color VARCHAR(20),
    icono VARCHAR(50),
    orden INT DEFAULT 999,
    activo BOOLEAN DEFAULT TRUE
);

CREATE TABLE subcategorias_gasto (
    id SERIAL PRIMARY KEY,
    categoria_id INT REFERENCES categorias_gasto(id),
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    UNIQUE(categoria_id, nombre)
);

CREATE TABLE gastos (
    id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    cedis_id INT REFERENCES cedis(id),
    categoria_id INT REFERENCES categorias_gasto(id),
    subcategoria_id INT REFERENCES subcategorias_gasto(id),
    
    proveedor VARCHAR(200),
    descripcion_completa TEXT,
    monto_total DECIMAL(10,2) NOT NULL,
    
    metodo_pago VARCHAR(50),
    num_factura VARCHAR(100),
    estado VARCHAR(50) DEFAULT 'Pendiente',
    
    notas TEXT,
    
    organizacion_id INT REFERENCES organizaciones(id),
    usuario_registro_id INT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE productos_gasto (
    id SERIAL PRIMARY KEY,
    gasto_id INT REFERENCES gastos(id) ON DELETE CASCADE,
    descripcion VARCHAR(300),
    cantidad DECIMAL(10,2),
    unidad VARCHAR(20),
    precio_unitario DECIMAL(10,2),
    subtotal DECIMAL(10,2),
    orden INT DEFAULT 1
);

CREATE INDEX idx_gastos_fecha ON gastos(fecha DESC);
CREATE INDEX idx_gastos_cedis ON gastos(cedis_id);
CREATE INDEX idx_gastos_categoria ON gastos(categoria_id);

-- ============================================
-- MÓDULO 3: PROTECCIÓN CIVIL
-- ============================================

-- Extintores
CREATE TABLE extintores (
    id SERIAL PRIMARY KEY,
    cedis_id INT REFERENCES cedis(id) UNIQUE,
    
    clasificacion_riesgo VARCHAR(50),
    extintores_requeridos INT DEFAULT 0,
    extintores_pqs INT DEFAULT 0,
    extintores_co2 INT DEFAULT 0,
    total_extintores INT DEFAULT 0,
    cumple BOOLEAN DEFAULT FALSE,
    
    fecha_recarga DATE,
    proveedor VARCHAR(200),
    costo DECIMAL(10,2),
    
    observaciones TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- PIPC (Programa Interno Protección Civil)
CREATE TABLE pipc (
    id SERIAL PRIMARY KEY,
    cedis_id INT REFERENCES cedis(id) UNIQUE,
    
    fecha_vobo DATE,
    fecha_vencimiento DATE,
    estatus VARCHAR(50) DEFAULT 'Pendiente',
    
    proveedor VARCHAR(200),
    costo DECIMAL(10,2),
    
    archivo_url TEXT,
    observaciones TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Dictámenes
CREATE TABLE dictamenes (
    id SERIAL PRIMARY KEY,
    cedis_id INT REFERENCES cedis(id),
    tipo VARCHAR(50) NOT NULL, -- 'Estructural' o 'Eléctrico'
    
    tiene_dictamen BOOLEAN DEFAULT FALSE,
    estatus VARCHAR(50), -- 'Vigente', 'Vencido', 'Pendiente'
    
    fecha_emision DATE,
    fecha_vencimiento DATE,
    proveedor VARCHAR(200),
    costo DECIMAL(10,2),
    
    archivo_url TEXT,
    observaciones TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(cedis_id, tipo)
);

CREATE INDEX idx_pipc_vencimiento ON pipc(fecha_vencimiento);
CREATE INDEX idx_dictamenes_vencimiento ON dictamenes(fecha_vencimiento);

-- ============================================
-- MÓDULO 4: INTELIGENCIA CRIMINAL
-- ============================================

CREATE TABLE indices_delictivos (
    id SERIAL PRIMARY KEY,
    año INT NOT NULL,
    mes INT NOT NULL,
    estado_id INT REFERENCES estados(id),
    municipio VARCHAR(100) NOT NULL,
    
    -- Delitos de alto impacto
    homicidio_doloso INT DEFAULT 0,
    homicidio_culposo INT DEFAULT 0,
    secuestro INT DEFAULT 0,
    extorsion INT DEFAULT 0,
    
    -- Robos (relevantes para CEDIS)
    robo_total INT DEFAULT 0,
    robo_con_violencia INT DEFAULT 0,
    robo_sin_violencia INT DEFAULT 0,
    robo_vehiculo INT DEFAULT 0,
    robo_negocio INT DEFAULT 0,
    robo_casa_habitacion INT DEFAULT 0,
    robo_transeúnte INT DEFAULT 0,
    robo_transporte INT DEFAULT 0,
    robo_mercancia INT DEFAULT 0,
    
    -- Otros delitos
    violencia_familiar INT DEFAULT 0,
    violacion INT DEFAULT 0,
    lesiones INT DEFAULT 0,
    daño_propiedad INT DEFAULT 0,
    
    -- Metadata
    fuente VARCHAR(100) DEFAULT 'SESNSP',
    fecha_carga TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(año, mes, estado_id, municipio)
);

CREATE INDEX idx_delictivos_fecha ON indices_delictivos(año DESC, mes DESC);
CREATE INDEX idx_delictivos_estado ON indices_delictivos(estado_id);

-- Vista: Riesgo delictivo por CEDIS
CREATE OR REPLACE VIEW v_riesgo_delictivo_cedis AS
SELECT 
    c.id AS cedis_id,
    c.nombre AS cedis,
    c.codigo,
    e.nombre AS estado,
    c.municipio,
    i.año,
    i.mes,
    (COALESCE(i.robo_negocio, 0) + COALESCE(i.robo_vehiculo, 0) + 
     COALESCE(i.robo_transporte, 0) + COALESCE(i.robo_mercancia, 0) + 
     COALESCE(i.extorsion, 0)) AS delitos_relevantes,
    i.robo_total,
    i.extorsion,
    i.secuestro,
    CASE 
        WHEN (COALESCE(i.robo_negocio, 0) + COALESCE(i.extorsion, 0)) > 50 THEN 'CRÍTICO'
        WHEN (COALESCE(i.robo_negocio, 0) + COALESCE(i.extorsion, 0)) > 20 THEN 'ALTO'
        WHEN (COALESCE(i.robo_negocio, 0) + COALESCE(i.extorsion, 0)) > 5 THEN 'MEDIO'
        ELSE 'BAJO'
    END AS nivel_riesgo
FROM cedis c
LEFT JOIN estados e ON c.estado_id = e.id
LEFT JOIN indices_delictivos i ON 
    c.estado_id = i.estado_id AND 
    UPPER(c.municipio) = UPPER(i.municipio)
ORDER BY c.nombre, i.año DESC, i.mes DESC;

-- ============================================
-- MÓDULO 5: MONITOREO AUTOMATIZADO 24/7
-- ============================================

CREATE TABLE fuentes_monitoreo (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    tipo VARCHAR(50) NOT NULL, 
    -- 'Periódico', 'RSS', 'Twitter', 'Facebook', 
    -- 'Alerta Oficial SSN', 'Alerta Oficial CONAGUA', 'Atlas Riesgos'
    url TEXT NOT NULL,
    estado_id INT REFERENCES estados(id),
    activo BOOLEAN DEFAULT TRUE,
    frecuencia_minutos INT DEFAULT 60,
    ultima_consulta TIMESTAMP,
    configuracion JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Insertar fuentes oficiales clave
INSERT INTO fuentes_monitoreo (nombre, tipo, url, frecuencia_minutos) VALUES
('SSN UNAM - Servicio Sismológico Nacional', 'Alerta Oficial SSN', 'http://www.ssn.unam.mx/', 15),
('CONAGUA - Ciclones Tropicales', 'Alerta Oficial CONAGUA', 'https://smn.conagua.gob.mx/es/ciclones-tropicales/informacion-historica', 360),
('Atlas Nacional de Riesgos', 'Atlas Riesgos', 'http://www.atlasnacionalderiesgos.gob.mx/', 1440);

CREATE TABLE noticias_monitoreadas (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4(),
    
    -- Fuente
    fuente_id INT REFERENCES fuentes_monitoreo(id),
    fuente_nombre VARCHAR(200),
    tipo_fuente VARCHAR(50),
    url TEXT,
    
    -- Contenido
    titulo TEXT NOT NULL,
    contenido TEXT,
    fecha_publicacion TIMESTAMP,
    fecha_deteccion TIMESTAMP DEFAULT NOW(),
    
    -- Clasificación automática (IA)
    tipo_alerta VARCHAR(50),
    -- 'Sísmica', 'Ciclón Tropical', 'Meteorológica', 'Seguridad', 
    -- 'Laboral', 'Protección Civil', 'Delictiva'
    nivel_criticidad VARCHAR(20) DEFAULT 'Informativo',
    -- 'Crítico', 'Alto', 'Medio', 'Bajo', 'Informativo'
    
    -- Geolocalización
    estado_afectado_id INT REFERENCES estados(id),
    municipio_afectado VARCHAR(100),
    cedis_afectados INT[], -- Array de IDs
    radio_impacto_km DECIMAL(10,2),
    
    -- Análisis IA
    analisis_ia TEXT,
    palabras_clave TEXT[],
    entidades_mencionadas TEXT[],
    sentimiento VARCHAR(20),
    confianza_clasificacion DECIMAL(3,2), -- 0.00 a 1.00
    
    -- Medidas sugeridas (IA)
    medidas_inmediatas TEXT,
    medidas_preventivas TEXT,
    medidas_correctivas TEXT,
    
    -- Reportes
    informe_preliminar_generado BOOLEAN DEFAULT FALSE,
    informe_preliminar_url TEXT,
    informe_completo_generado BOOLEAN DEFAULT FALSE,
    informe_completo_url TEXT,
    
    -- Alertas
    alertas_enviadas BOOLEAN DEFAULT FALSE,
    destinatarios_alertados TEXT[],
    fecha_alerta TIMESTAMP,
    
    -- Estado
    revisado BOOLEAN DEFAULT FALSE,
    relevante BOOLEAN DEFAULT TRUE,
    archivado BOOLEAN DEFAULT FALSE,
    notas_seguimiento TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_noticias_fecha ON noticias_monitoreadas(fecha_deteccion DESC);
CREATE INDEX idx_noticias_criticidad ON noticias_monitoreadas(nivel_criticidad);
CREATE INDEX idx_noticias_tipo ON noticias_monitoreadas(tipo_alerta);
CREATE INDEX idx_noticias_estado ON noticias_monitoreadas(estado_afectado_id);
CREATE INDEX idx_noticias_revisado ON noticias_monitoreadas(revisado, archivado);

-- ============================================
-- SISTEMA DE USUARIOS Y PERMISOS
-- ============================================

CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    
    rol VARCHAR(50) NOT NULL DEFAULT 'Usuario',
    -- 'Administrador', 'Supervisor', 'Gerente CEDIS', 'Consulta'
    
    organizacion_id INT REFERENCES organizaciones(id),
    cedis_asignados INT[],
    
    permisos JSONB,
    
    activo BOOLEAN DEFAULT TRUE,
    ultimo_login TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_usuarios_email ON usuarios(email);
CREATE INDEX idx_usuarios_rol ON usuarios(rol);

CREATE TABLE sesiones (
    id SERIAL PRIMARY KEY,
    usuario_id INT REFERENCES usuarios(id),
    token_hash TEXT NOT NULL,
    ip_address VARCHAR(50),
    user_agent TEXT,
    valido_hasta TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_sesiones_token ON sesiones(token_hash);
CREATE INDEX idx_sesiones_usuario ON sesiones(usuario_id);

CREATE TABLE auditoria (
    id SERIAL PRIMARY KEY,
    usuario_id INT REFERENCES usuarios(id),
    accion VARCHAR(100) NOT NULL,
    tabla_afectada VARCHAR(100),
    registro_id INT,
    datos_anteriores JSONB,
    datos_nuevos JSONB,
    ip_address VARCHAR(50),
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_auditoria_usuario ON auditoria(usuario_id);
CREATE INDEX idx_auditoria_fecha ON auditoria(timestamp DESC);
CREATE INDEX idx_auditoria_tabla ON auditoria(tabla_afectada);

-- ============================================
-- REPORTES Y TEMPLATES
-- ============================================

CREATE TABLE reportes_generados (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4(),
    
    tipo_reporte VARCHAR(100) NOT NULL,
    titulo VARCHAR(300),
    
    organizacion_id INT REFERENCES organizaciones(id),
    cedis_id INT REFERENCES cedis(id),
    evento_id INT,
    noticia_id INT REFERENCES noticias_monitoreadas(id),
    
    formato VARCHAR(20), -- 'PDF', 'DOCX', 'XLSX', 'HTML'
    url_archivo TEXT,
    tamaño_bytes BIGINT,
    
    estado VARCHAR(50) DEFAULT 'Generando',
    -- 'Generando', 'Completado', 'Error'
    error_mensaje TEXT,
    
    generado_por_usuario_id INT REFERENCES usuarios(id),
    generado_automaticamente BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_reportes_tipo ON reportes_generados(tipo_reporte);
CREATE INDEX idx_reportes_fecha ON reportes_generados(created_at DESC);

-- ============================================
-- CONFIGURACIÓN Y CATÁLOGOS
-- ============================================

CREATE TABLE configuraciones (
    id SERIAL PRIMARY KEY,
    clave VARCHAR(100) UNIQUE NOT NULL,
    valor TEXT,
    tipo VARCHAR(50) DEFAULT 'string',
    descripcion TEXT,
    categoria VARCHAR(50),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Configuraciones iniciales
INSERT INTO configuraciones (clave, valor, tipo, descripcion, categoria) VALUES
('sistema.nombre', 'Sistema Integral de Protección de Activos', 'string', 'Nombre del sistema', 'general'),
('sistema.version', '1.0.0', 'string', 'Versión actual', 'general'),
('alertas.emails', 'delatorrev0@gmail.com,victor.delatorre@omnilife.com', 'string', 'Emails para alertas', 'alertas'),
('monitoreo.frecuencia_noticias', '60', 'number', 'Minutos entre consultas de noticias', 'monitoreo'),
('reportes.logo_omnilife', '', 'string', 'URL logo Omnilife', 'reportes'),
('reportes.logo_sci', '', 'string', 'URL logo SCI', 'reportes');

-- ============================================
-- FUNCIONES Y TRIGGERS
-- ============================================

-- Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Aplicar trigger a tablas principales
CREATE TRIGGER update_cedis_updated_at 
BEFORE UPDATE ON cedis
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_eventos_updated_at 
BEFORE UPDATE ON eventos_seguridad
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_gastos_updated_at 
BEFORE UPDATE ON gastos
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_extintores_updated_at 
BEFORE UPDATE ON extintores
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_pipc_updated_at 
BEFORE UPDATE ON pipc
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_dictamenes_updated_at 
BEFORE UPDATE ON dictamenes
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_noticias_updated_at 
BEFORE UPDATE ON noticias_monitoreadas
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Función para calcular cumplimiento de extintores
CREATE OR REPLACE FUNCTION calcular_cumplimiento_extintores()
RETURNS TRIGGER AS $$
BEGIN
    NEW.total_extintores = COALESCE(NEW.extintores_pqs, 0) + COALESCE(NEW.extintores_co2, 0);
    NEW.cumple = (NEW.total_extintores >= COALESCE(NEW.extintores_requeridos, 0));
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER trigger_cumplimiento_extintores 
BEFORE INSERT OR UPDATE ON extintores
FOR EACH ROW EXECUTE FUNCTION calcular_cumplimiento_extintores();

-- Función para calcular subtotal de productos
CREATE OR REPLACE FUNCTION calcular_subtotal_producto()
RETURNS TRIGGER AS $$
BEGIN
    NEW.subtotal = COALESCE(NEW.cantidad, 0) * COALESCE(NEW.precio_unitario, 0);
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER trigger_subtotal_producto 
BEFORE INSERT OR UPDATE ON productos_gasto
FOR EACH ROW EXECUTE FUNCTION calcular_subtotal_producto();

-- ============================================
-- VISTAS ANALÍTICAS
-- ============================================

-- Vista: Resumen de compliance por CEDIS
CREATE OR REPLACE VIEW v_compliance_cedis AS
SELECT 
    c.id AS cedis_id,
    c.codigo,
    c.nombre,
    e.nombre AS estado,
    
    -- Extintores
    COALESCE(ext.cumple, FALSE) AS extintores_cumple,
    ext.total_extintores,
    ext.extintores_requeridos,
    ext.fecha_recarga AS extintores_ultima_recarga,
    
    -- PIPC
    p.estatus AS pipc_estatus,
    p.fecha_vencimiento AS pipc_vencimiento,
    CASE 
        WHEN p.fecha_vencimiento IS NULL THEN FALSE
        WHEN p.fecha_vencimiento < CURRENT_DATE THEN FALSE
        ELSE TRUE
    END AS pipc_vigente,
    
    -- Dictámenes
    de.estatus AS dictamen_estructural_estatus,
    dl.estatus AS dictamen_electrico_estatus,
    
    -- Score general (0-100)
    (
        (CASE WHEN COALESCE(ext.cumple, FALSE) THEN 25 ELSE 0 END) +
        (CASE WHEN p.fecha_vencimiento >= CURRENT_DATE THEN 25 ELSE 0 END) +
        (CASE WHEN de.estatus = 'Vigente' THEN 25 ELSE 0 END) +
        (CASE WHEN dl.estatus = 'Vigente' THEN 25 ELSE 0 END)
    ) AS compliance_score
    
FROM cedis c
LEFT JOIN estados e ON c.estado_id = e.id
LEFT JOIN extintores ext ON c.id = ext.cedis_id
LEFT JOIN pipc p ON c.id = p.cedis_id
LEFT JOIN dictamenes de ON c.id = de.cedis_id AND de.tipo = 'Estructural'
LEFT JOIN dictamenes dl ON c.id = dl.cedis_id AND dl.tipo = 'Eléctrico'
WHERE c.activo = TRUE;

-- Vista: Eventos recientes por CEDIS
CREATE OR REPLACE VIEW v_eventos_recientes AS
SELECT 
    e.id,
    e.fecha,
    e.tipo_evento,
    c.nombre AS cedis,
    c.codigo AS cedis_codigo,
    est.nombre AS estado,
    e.descripcion,
    e.estatus,
    e.created_at
FROM eventos_seguridad e
JOIN cedis c ON e.cedis_id = c.id
JOIN estados est ON c.estado_id = est.id
ORDER BY e.fecha DESC
LIMIT 100;

-- Vista: Gastos del mes actual
CREATE OR REPLACE VIEW v_gastos_mes_actual AS
SELECT 
    g.id,
    g.fecha,
    c.nombre AS cedis,
    cat.nombre AS categoria,
    sub.nombre AS subcategoria,
    g.proveedor,
    g.descripcion_completa,
    g.monto_total,
    g.metodo_pago,
    g.estado
FROM gastos g
JOIN cedis c ON g.cedis_id = c.id
LEFT JOIN categorias_gasto cat ON g.categoria_id = cat.id
LEFT JOIN subcategorias_gasto sub ON g.subcategoria_id = sub.id
WHERE EXTRACT(YEAR FROM g.fecha) = EXTRACT(YEAR FROM CURRENT_DATE)
  AND EXTRACT(MONTH FROM g.fecha) = EXTRACT(MONTH FROM CURRENT_DATE)
ORDER BY g.fecha DESC;

-- ============================================
-- ÍNDICES ADICIONALES PARA PERFORMANCE
-- ============================================

CREATE INDEX idx_eventos_org ON eventos_seguridad(organizacion_id);
CREATE INDEX idx_gastos_org ON gastos(organizacion_id);
CREATE INDEX idx_gastos_estado ON gastos(estado);

-- Índices para búsqueda de texto
CREATE INDEX idx_eventos_descripcion_trgm ON eventos_seguridad USING gin(descripcion gin_trgm_ops);
CREATE INDEX idx_noticias_titulo_trgm ON noticias_monitoreadas USING gin(titulo gin_trgm_ops);
CREATE INDEX idx_noticias_contenido_trgm ON noticias_monitoreadas USING gin(contenido gin_trgm_ops);

-- ============================================
-- COMENTARIOS EN TABLAS
-- ============================================

COMMENT ON TABLE cedis IS 'Centros de Distribución (20 en Zona Sureste)';
COMMENT ON TABLE eventos_seguridad IS 'Registro de eventos de monitoreo (alarmas, actas, servicios)';
COMMENT ON TABLE gastos IS 'Control presupuestal y gastos por CEDIS';
COMMENT ON TABLE extintores IS 'Inventario y cumplimiento de extintores por CEDIS';
COMMENT ON TABLE pipc IS 'Programa Interno de Protección Civil por CEDIS';
COMMENT ON TABLE dictamenes IS 'Dictámenes estructurales y eléctricos por CEDIS';
COMMENT ON TABLE indices_delictivos IS 'Datos de SESNSP - Índices delictivos por municipio';
COMMENT ON TABLE noticias_monitoreadas IS 'Noticias y alertas monitoreadas 24/7 con análisis IA';
COMMENT ON TABLE fuentes_monitoreo IS 'Fuentes configuradas para monitoreo automático';

-- ============================================
-- FIN DEL SCRIPT
-- ============================================

-- Verificar tablas creadas
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;
