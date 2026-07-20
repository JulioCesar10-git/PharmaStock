import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

class Conexion:
    _conexion = None

    @classmethod
    def obtener_conexion(cls):
        if cls._conexion is None or cls._conexion.closed:
            cls._conexion = psycopg2.connect(
                host = os.getenv("DB_HOST"),
                port = os.getenv("DB_PORT"),
                database = os.getenv("DB_NAME"),
                user = os.getenv("DB_USER"),
                password = os.getenv("DB_PASSWORD"),
            )
        return cls._conexion
    
    @classmethod
    def cerrar_conexion(cls):
        if cls._conexion and not cls._conexion.closed:
            cls._conexion.close()
        
