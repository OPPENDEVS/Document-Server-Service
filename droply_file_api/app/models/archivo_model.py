from app.database import get_connection
from datetime import datetime
from psycopg2 import sql, DatabaseError


def insert_archivo(nombre, url, tipo):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO archivos (nombre, url, creado, tipo)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id;
                """, (nombre, url, datetime.now(), tipo))
                return cur.fetchone()[0]
    except DatabaseError as e:
        print(f"Error al insertar archivo: {e}")
        return None


def get_all_archivos():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT a.id, a.nombre, a.url, a.creado, a.tipo, t.nombre as tipo_nombre
                    FROM archivos a
                    JOIN tipoArchivo t ON a.tipo = t.id
                    ORDER BY a.creado DESC;
                """)
                return cur.fetchall()
    except DatabaseError as e:
        print(f"Error al obtener archivos: {e}")
        return []


def update_archivo(id, nuevo_nombre):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE archivos SET nombre = %s WHERE id = %s;", (nuevo_nombre, id))
                conn.commit()
    except DatabaseError as e:
        print(f"Error al actualizar archivo: {e}")


def delete_archivo(id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT url FROM archivos WHERE id = %s;", (id,))
                row = cur.fetchone()
                if row:
                    path = row[0]
                    cur.execute("DELETE FROM archivos WHERE id = %s;", (id,))
                    conn.commit()
                    return path
                return None
    except DatabaseError as e:
        print(f"Error al eliminar archivo: {e}")
        return None
