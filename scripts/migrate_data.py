#!/usr/bin/env python3
"""
Script de Migración de Datos - Sistema Integral de Protección de Activos
Migra datos desde Excel a PostgreSQL
Autor: Sistema desarrollado para Victor Manuel De La Torre
Fecha: 28 Febrero 2026
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import os
from datetime import datetime
import sys

# Configuración de base de datos (desde variable de entorno)
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:pass@localhost:5432/proteccion_activos_db')

# Rutas a archivos Excel
EXCEL_GASTOS = '/mnt/user-data/uploads/Sistema_de_registro_de_gastos_completo_zona_sur.xlsm'
EXCEL_CEDIS = '/mnt/user-data/uploads/SISTEMA_GESTION_CEDIS_COMPLETO.xlsm'

class MigradorDatos:
    def __init__(self, database_url):
        self.database_url = database_url
        self.conn = None
        self.cur = None
        
    def conectar(self):
        """Conectar a PostgreSQL"""
        try:
            self.conn = psycopg2.connect(self.database_url)
            self.cur = self.conn.cursor()
            print("✅ Conectado a PostgreSQL")
            return True
        except Exception as e:
            print(f"❌ Error conectando a BD: {e}")
            return False
    
    def cerrar(self):
        """Cerrar conexión"""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
        print("✅ Conexión cerrada")
    
    def migrar_estados(self):
        """Migrar estados (ya están en el init script, solo verificamos)"""
        print("\n📍 Verificando estados...")
        self.cur.execute("SELECT COUNT(*) FROM estados")
        count = self.cur.fetchone()[0]
        
        if count == 0:
            print("⚠️ Estados no encontrados, insertando...")
            estados = [
                ('Campeche', 'CAM', False, True),
                ('Quintana Roo', 'QROO', False, True),
                ('Tabasco', 'TAB', False, True),
                ('Chiapas', 'CHIS', True, False),
                ('Oaxaca', 'OAX', True, True),
                ('Yucatán', 'YUC', False, True)
            ]
            
            self.cur.executemany(
                "INSERT INTO estados (nombre, codigo, zona_sismica, zona_costera) VALUES (%s, %s, %s, %s)",
                estados
            )
            self.conn.commit()
            print(f"✅ {len(estados)} estados insertados")
        else:
            print(f"✅ {count} estados ya existen")
    
    def migrar_cedis(self):
        """Migrar 20 CEDIS desde Excel"""
        print("\n🏢 Migrando CEDIS...")
        
        try:
            # Leer Excel
            df = pd.read_excel(EXCEL_CEDIS, sheet_name='BASE DE DATOS', header=3, nrows=20, engine='openpyxl')
            
            # Mapeo de estados a IDs
            self.cur.execute("SELECT id, nombre FROM estados")
            estados_map = {nombre: id for id, nombre in self.cur.fetchall()}
            
            # Obtener ID de organización Omnilife
            self.cur.execute("SELECT id FROM organizaciones WHERE nombre = 'Omnilife México'")
            org_id = self.cur.fetchone()[0]
            
            cedis_insertados = 0
            
            for idx, row in df.iterrows():
                try:
                    # Generar código si no existe
                    codigo = f"MX{row['No.']:05d}"
                    nombre = str(row['CEDIS']).strip()
                    estado_nombre = str(row['ESTADO']).strip()
                    municipio = str(row['MUNICIPIO']).strip()
                    
                    # Buscar estado_id
                    estado_id = estados_map.get(estado_nombre)
                    if not estado_id:
                        print(f"⚠️ Estado no encontrado: {estado_nombre}, skipping {nombre}")
                        continue
                    
                    # Coordenadas aproximadas (se pueden refinar después)
                    # Por ahora usar valores placeholder
                    coords_map = {
                        'Campeche': (19.8301, -90.5349),
                        'Cancún': (21.1619, -86.8515),
                        'Chetumal': (18.5001, -88.2960),
                        'Ciudad del Carmen': (18.6500, -91.8333),
                        'Comalcalco': (18.2667, -93.2167),
                        'Comitán': (16.2500, -92.1333),
                        'Huajuapan': (17.8000, -97.7667),
                        'Mérida': (20.9674, -89.5926),
                        'Mérida Norte': (21.0000, -89.5926),
                        'Mérida HUB': (20.9500, -89.5926),
                        'Oaxaca': (17.0732, -96.7266),
                        'Playa del Carmen': (20.6296, -87.0739),
                        'Puerto Escondido': (15.8667, -97.0667),
                        'Salina Cruz': (16.1667, -95.2000),
                        'San Cristóbal': (16.7333, -92.6333),
                        'Tapachula': (14.9000, -92.2667),
                        'Tenosique': (17.4833, -91.4333),
                        'Tuxtepec': (18.0833, -96.1167),
                        'Tuxtla Gutiérrez': (16.7516, -93.1161),
                        'Villahermosa': (17.9892, -92.9475)
                    }
                    
                    lat, lng = coords_map.get(nombre, (0, 0))
                    
                    # Insertar CEDIS
                    self.cur.execute("""
                        INSERT INTO cedis (
                            codigo, nombre, estado_id, municipio,
                            superficie_m2, personal_total, gerente, correo,
                            latitud, longitud, organizacion_id, activo
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (codigo) DO UPDATE SET
                            nombre = EXCLUDED.nombre,
                            superficie_m2 = EXCLUDED.superficie_m2,
                            personal_total = EXCLUDED.personal_total
                        RETURNING id
                    """, (
                        codigo,
                        nombre,
                        estado_id,
                        municipio,
                        float(row['SUPERFICIE (m²)']) if pd.notna(row['SUPERFICIE (m²)']) else None,
                        int(row['PERSONAL']) if pd.notna(row['PERSONAL']) else 0,
                        str(row['GERENTE']) if pd.notna(row['GERENTE']) else None,
                        str(row['CORREO']) if pd.notna(row['CORREO']) else None,
                        lat,
                        lng,
                        org_id,
                        True
                    ))
                    
                    cedis_id = self.cur.fetchone()[0]
                    
                    # Migrar datos de extintores
                    self.migrar_extintores_cedis(row, cedis_id)
                    
                    # Migrar datos de PIPC
                    self.migrar_pipc_cedis(row, cedis_id)
                    
                    # Migrar dictámenes
                    self.migrar_dictamenes_cedis(row, cedis_id)
                    
                    cedis_insertados += 1
                    
                except Exception as e:
                    print(f"⚠️ Error con CEDIS {nombre}: {e}")
                    continue
            
            self.conn.commit()
            print(f"✅ {cedis_insertados} CEDIS migrados correctamente")
            
        except Exception as e:
            print(f"❌ Error migrando CEDIS: {e}")
            self.conn.rollback()
    
    def migrar_extintores_cedis(self, row, cedis_id):
        """Migrar datos de extintores para un CEDIS"""
        try:
            self.cur.execute("""
                INSERT INTO extintores (
                    cedis_id, clasificacion_riesgo,
                    extintores_requeridos, extintores_pqs, extintores_co2,
                    total_extintores, cumple,
                    fecha_recarga, proveedor, costo
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (cedis_id) DO UPDATE SET
                    extintores_requeridos = EXCLUDED.extintores_requeridos,
                    extintores_pqs = EXCLUDED.extintores_pqs,
                    extintores_co2 = EXCLUDED.extintores_co2
            """, (
                cedis_id,
                str(row['CLASIFICACIÓN RIESGO']) if pd.notna(row.get('CLASIFICACIÓN RIESGO')) else None,
                int(row['EXTINTORES REQ.']) if pd.notna(row.get('EXTINTORES REQ.')) else 0,
                int(row['EXT. PQS']) if pd.notna(row.get('EXT. PQS')) else 0,
                int(row['EXT. CO2']) if pd.notna(row.get('EXT. CO2')) else 0,
                int(row['TOTAL EXT.']) if pd.notna(row.get('TOTAL EXT.')) else 0,
                str(row.get('CUMPLE', '')).upper() in ['SI', 'SÍ', 'YES'],
                pd.to_datetime(row['FECHA RECARGA EXT.']).date() if pd.notna(row.get('FECHA RECARGA EXT.')) else None,
                str(row['PROVEEDOR EXT.']) if pd.notna(row.get('PROVEEDOR EXT.')) else None,
                float(row['COSTO EXT.']) if pd.notna(row.get('COSTO EXT.')) else None
            ))
        except Exception as e:
            print(f"    ⚠️ Error extintores: {e}")
    
    def migrar_pipc_cedis(self, row, cedis_id):
        """Migrar datos de PIPC para un CEDIS"""
        try:
            estatus = str(row.get('ESTATUS PIPC', 'Pendiente')).strip()
            
            self.cur.execute("""
                INSERT INTO pipc (
                    cedis_id, fecha_vobo, fecha_vencimiento,
                    estatus, proveedor, costo
                ) VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (cedis_id) DO UPDATE SET
                    fecha_vencimiento = EXCLUDED.fecha_vencimiento,
                    estatus = EXCLUDED.estatus
            """, (
                cedis_id,
                pd.to_datetime(row['FECHA PIPC']).date() if pd.notna(row.get('FECHA PIPC')) else None,
                pd.to_datetime(row['VENC. PIPC']).date() if pd.notna(row.get('VENC. PIPC')) else None,
                estatus if estatus else 'Pendiente',
                str(row['PROVEEDOR PIPC']) if pd.notna(row.get('PROVEEDOR PIPC')) else None,
                float(row['COSTO PIPC']) if pd.notna(row.get('COSTO PIPC')) else None
            ))
        except Exception as e:
            print(f"    ⚠️ Error PIPC: {e}")
    
    def migrar_dictamenes_cedis(self, row, cedis_id):
        """Migrar dictámenes para un CEDIS"""
        try:
            # Dictamen Estructural
            tiene_estr = str(row.get('DICT. ESTRUCTURAL', '')).upper() in ['SI', 'SÍ', 'YES']
            estatus_estr = str(row.get('ESTATUS ESTR.', 'Pendiente')).strip()
            
            self.cur.execute("""
                INSERT INTO dictamenes (
                    cedis_id, tipo, tiene_dictamen, estatus, proveedor
                ) VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (cedis_id, tipo) DO UPDATE SET
                    estatus = EXCLUDED.estatus
            """, (
                cedis_id,
                'Estructural',
                tiene_estr,
                estatus_estr if estatus_estr else 'Pendiente',
                str(row.get('PROVEEDOR DICT.')) if pd.notna(row.get('PROVEEDOR DICT.')) else None
            ))
            
            # Dictamen Eléctrico
            tiene_elec = str(row.get('DICT. ELÉCTRICO', '')).upper() in ['SI', 'SÍ', 'YES']
            estatus_elec = str(row.get('ESTATUS ELEC.', 'Pendiente')).strip()
            
            self.cur.execute("""
                INSERT INTO dictamenes (
                    cedis_id, tipo, tiene_dictamen, estatus, proveedor
                ) VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (cedis_id, tipo) DO UPDATE SET
                    estatus = EXCLUDED.estatus
            """, (
                cedis_id,
                'Eléctrico',
                tiene_elec,
                estatus_elec if estatus_elec else 'Pendiente',
                str(row.get('PROVEEDOR DICT.')) if pd.notna(row.get('PROVEEDOR DICT.')) else None
            ))
            
        except Exception as e:
            print(f"    ⚠️ Error dictámenes: {e}")
    
    def migrar_gastos(self):
        """Migrar gastos desde Excel"""
        print("\n💰 Migrando gastos...")
        
        try:
            # Leer Excel de gastos
            df = pd.read_excel(EXCEL_GASTOS, sheet_name='Registro de Gastos', engine='openpyxl')
            
            # Obtener IDs de CEDIS
            self.cur.execute("SELECT id, nombre FROM cedis")
            cedis_map = {nombre: id for id, nombre in self.cur.fetchall()}
            
            # Obtener ID de organización
            self.cur.execute("SELECT id FROM organizaciones WHERE nombre = 'Omnilife México'")
            org_id = self.cur.fetchone()[0]
            
            # Crear categorías si no existen
            categorias_unicas = df['Categoría'].dropna().unique()
            categorias_ids = {}
            
            for cat in categorias_unicas:
                self.cur.execute("""
                    INSERT INTO categorias_gasto (nombre, activo)
                    VALUES (%s, %s)
                    ON CONFLICT (nombre) DO UPDATE SET nombre = EXCLUDED.nombre
                    RETURNING id
                """, (str(cat).strip(), True))
                categorias_ids[cat] = self.cur.fetchone()[0]
            
            gastos_insertados = 0
            
            for idx, row in df.iterrows():
                try:
                    # Buscar CEDIS
                    cedis_nombre = str(row['CEDIS']).strip()
                    # Extraer solo el nombre del CEDIS (quitar código)
                    if ' - ' in cedis_nombre:
                        cedis_nombre = cedis_nombre.split(' - ')[1].split()[0]
                    
                    cedis_id = None
                    for nombre, id in cedis_map.items():
                        if nombre.lower() in cedis_nombre.lower() or cedis_nombre.lower() in nombre.lower():
                            cedis_id = id
                            break
                    
                    if not cedis_id:
                        print(f"⚠️ CEDIS no encontrado: {cedis_nombre}")
                        continue
                    
                    categoria = str(row['Categoría']).strip()
                    categoria_id = categorias_ids.get(categoria)
                    
                    # Insertar gasto
                    self.cur.execute("""
                        INSERT INTO gastos (
                            fecha, cedis_id, categoria_id,
                            proveedor, descripcion_completa, monto_total,
                            metodo_pago, num_factura, estado,
                            notas, organizacion_id
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (
                        pd.to_datetime(row['Fecha']).date() if pd.notna(row['Fecha']) else datetime.now().date(),
                        cedis_id,
                        categoria_id,
                        str(row['Proveedor']) if pd.notna(row.get('Proveedor')) else None,
                        str(row['Descripción Completa']) if pd.notna(row.get('Descripción Completa')) else None,
                        float(row['Monto Total']) if pd.notna(row['Monto Total']) else 0.0,
                        str(row['Método de Pago']) if pd.notna(row.get('Método de Pago')) else None,
                        str(row['No. Factura']) if pd.notna(row.get('No. Factura')) else None,
                        str(row['Estado']) if pd.notna(row.get('Estado')) else 'Pendiente',
                        str(row['Notas']) if pd.notna(row.get('Notas')) else None,
                        org_id
                    ))
                    
                    gastos_insertados += 1
                    
                except Exception as e:
                    print(f"⚠️ Error con gasto #{idx}: {e}")
                    continue
            
            self.conn.commit()
            print(f"✅ {gastos_insertados} gastos migrados correctamente")
            
        except Exception as e:
            print(f"❌ Error migrando gastos: {e}")
            self.conn.rollback()
    
    def ejecutar_migracion_completa(self):
        """Ejecutar migración completa"""
        print("\n" + "="*70)
        print("INICIANDO MIGRACIÓN COMPLETA DE DATOS")
        print("="*70)
        
        if not self.conectar():
            return False
        
        try:
            self.migrar_estados()
            self.migrar_cedis()
            self.migrar_gastos()
            
            print("\n" + "="*70)
            print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
            print("="*70)
            
            # Resumen
            self.cur.execute("SELECT COUNT(*) FROM cedis")
            total_cedis = self.cur.fetchone()[0]
            
            self.cur.execute("SELECT COUNT(*) FROM gastos")
            total_gastos = self.cur.fetchone()[0]
            
            self.cur.execute("SELECT COUNT(*) FROM extintores")
            total_ext = self.cur.fetchone()[0]
            
            print(f"\n📊 RESUMEN:")
            print(f"  - CEDIS migrados: {total_cedis}")
            print(f"  - Gastos migrados: {total_gastos}")
            print(f"  - Extintores registrados: {total_ext}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ ERROR EN MIGRACIÓN: {e}")
            return False
        finally:
            self.cerrar()


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║   SISTEMA INTEGRAL DE PROTECCIÓN DE ACTIVOS                         ║
║   Script de Migración de Datos                                      ║
║   Victor Manuel De La Torre - SCI DE OCCIDENTE                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    # Verificar que DATABASE_URL esté configurada
    if not os.getenv('DATABASE_URL'):
        print("\n⚠️  WARNING: DATABASE_URL no está configurada")
        print("Por favor ejecuta:")
        print('export DATABASE_URL="postgresql://user:pass@host:5432/dbname"')
        print("\nO si quieres usar valores por defecto (desarrollo local):")
        respuesta = input("¿Usar localhost por defecto? (s/n): ")
        if respuesta.lower() != 's':
            sys.exit(1)
    
    # Crear migrador y ejecutar
    migrador = MigradorDatos(DATABASE_URL)
    exito = migrador.ejecutar_migracion_completa()
    
    sys.exit(0 if exito else 1)
