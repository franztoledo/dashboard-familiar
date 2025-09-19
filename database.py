# Contenido para database.py

import sqlite3
import pandas as pd

def crear_conexion():
    """Establece y devuelve un objeto de conexión a la base de datos SQLite."""
    return sqlite3.connect('financiero.db')

def inicializar_db():
    """Crea las tablas 'transacciones' y 'configuracion' si no existen."""
    conn = crear_conexion()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transacciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            categoria TEXT NOT NULL,
            monto REAL NOT NULL,
            fecha TEXT NOT NULL,
            descripcion TEXT
        );
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS configuracion (
            key TEXT PRIMARY KEY,
            value REAL NOT NULL
        );
    """)
    
    cursor.execute("INSERT OR IGNORE INTO configuracion (key, value) VALUES ('presupuesto', 3000.0)")
    cursor.execute("INSERT OR IGNORE INTO configuracion (key, value) VALUES ('meta_ahorro', 600.0)")
        
    conn.commit()
    conn.close()

def insertar_transaccion(tipo, categoria, monto, fecha, descripcion):
    """Inserta un nuevo registro en la tabla de transacciones."""
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO transacciones (tipo, categoria, monto, fecha, descripcion) VALUES (?, ?, ?, ?, ?)",
        (tipo, categoria, monto, fecha, descripcion)
    )
    conn.commit()
    conn.close()

def obtener_transacciones():
    """Obtiene todos los registros de la tabla de transacciones."""
    conn = crear_conexion()
    df = pd.read_sql_query("SELECT * FROM transacciones", conn)
    conn.close()
    return df

def eliminar_transaccion(id_transaccion):
    """Elimina un registro de la tabla de transacciones según su ID."""
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transacciones WHERE id = ?", (id_transaccion,))
    conn.commit()
    conn.close()

def obtener_configuracion(key):
    """Obtiene un valor de la tabla de configuración."""
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM configuracion WHERE key = ?", (key,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0.0

def guardar_configuracion(key, value):
    """Establece o actualiza un valor en la tabla de configuración."""
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute("REPLACE INTO configuracion (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()