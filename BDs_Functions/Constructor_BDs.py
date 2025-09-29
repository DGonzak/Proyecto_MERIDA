import os
from pathlib import Path

import sqlalchemy as sqlal 
from BDs_Functions.Models_BD import Base, BD_Tags_General, BD_Comb_Teclas, BD_Recient_Arch, BDInformadora, BD_Moduls

from Lib_Extra.Rutas_Gestion import get_data_dir

"""Las siguientes lineas crear las bases de datos respectivas a las encontradas en el archivo Models_BD.py
Ahora bien, como se quiere crear archivos individuales para cada tabla, se selecciona mediante la 
opción tables=.Sin esta opción y específicación, todas las tablas se crearán en un solo archivo."""

def crear_BDs_Constructor(bases_a_construir=None):
    """
    Crea solo las bases de datos especificadas en `bases_a_construir`.

    Parámetros:
        bases_a_construir (list[str]): Nombres de las BDs a crear, como:
            ["BD_TAGS", "BD_ComTecl"]

    Retorna:
        tuple: (estado: bool, error: Exception|None)
    """
    estado_construc = False
    error_construc = None

    """
    Nota: Recuerda que en sqlite:/// se usan tres barras diagonales, ya que se usa una 
    dirección relativa. 
    """
    ruta_bds_us = Path(get_data_dir()) / "BDs"

    # Asegurar que exista el directorio
    ruta_bds_us.mkdir(parents=True, exist_ok=True)

    def sqlite_uri(nombre_archivo: str) -> str:
        """
        Construye una URI SQLite cross-platform.
        Ejemplo:
          sqlite:///C:/Users/.../BDs/BD_TAGS.sqlite  (Windows)
          sqlite:////home/.../.local/share/merida/BDs/BD_TAGS.sqlite  (Linux)
        """
        # Convertimos a ruta absoluta
        ruta_abs = ruta_bds_us / nombre_archivo
        # Path.as_uri() se encarga de usar file:// con el formato correcto
        return f"sqlite:///{ruta_abs.as_posix()}"

    tablas_disponibles = {
        "BD_TAGS":        (BD_Tags_General.__table__, sqlite_uri("BD_TAGS.sqlite")),
        "BD_ComTecl":     (BD_Comb_Teclas.__table__, sqlite_uri("BD_ComTecl.sqlite")),
        "BD_RecentArch":  (BD_Recient_Arch.__table__, sqlite_uri("BD_RecentArch.sqlite")),
        "BD_Informadora": (BDInformadora.__table__,  sqlite_uri("BD_Informadora.sqlite")),
        "BD_Moduls":      (BD_Moduls.__table__, sqlite_uri("BD_Modulos.sqlite")),
    }

    # Si quieres conservar el equivalente a RUTA_PARA_BDs_SISTEMA (para logs, etc.)
    RUTA_PARA_BDs_SISTEMA = str(ruta_bds_us)


    try:

        #Asegura que la carpeta designada exista
        os.makedirs(RUTA_PARA_BDs_SISTEMA, exist_ok=True)



        for nombre_bd in bases_a_construir:

            if nombre_bd in tablas_disponibles:

                tabla, ruta = tablas_disponibles[nombre_bd]
                
                engine = sqlal.create_engine(ruta)
                
                Base.metadata.create_all(engine, tables=[tabla])

        estado_construc = True

    except Exception as e:
        error_construc = e

    return estado_construc, error_construc

