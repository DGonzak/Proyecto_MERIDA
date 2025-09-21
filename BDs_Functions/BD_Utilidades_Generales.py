import sqlite3
import os
from datetime import datetime
import io
import shutil
from sqlalchemy import create_engine, text
from Lib_Extra.Funciones_extras import mostrar_vent_IEO, filtrar_archivos_por_extension_BD, obtener_archivo_mas_reciente_ResplArch,leer_archivo_recurrente
from dateutil.relativedelta import relativedelta
from collections import defaultdict

from Lib_Extra.Rutas_Gestion import get_data_dir

class BD_UtilidadesGenerales ():

    def __init__(self):
        pass

    def respaldar_base_de_datos(self, nombre_BD, origenbd_get, carpeta_respaldo, ruta_sqlite_origen):
        """
        Crea un respaldo dual (binario y volcado SQL) de una base de datos.
        - nombre_BD: nombre base (sin extensión)
        - origenbd_get: 'sistema' o 'usuario'
        - carpeta_respaldo: carpeta raíz para los respaldos
        - ruta_sqlite_origen: ruta absoluta de la base .sqlite original
        """

        tiempo_creacion = datetime.now().strftime("%Y-%m-%d_%H-%M")

        #comprueba el origen (para usuarios, habrá otra validación (elif))
        if origenbd_get.lower() == "sistema":
            # Crear carpeta específica para esta base
            ruta_carpeta_individual = os.path.join(carpeta_respaldo, nombre_BD)
            os.makedirs(ruta_carpeta_individual, exist_ok=True)

            # Ruta del archivo binario y volcado
            archivo_sqlite = os.path.join(ruta_carpeta_individual, f"{nombre_BD}_respaldo_{tiempo_creacion}.sqlite")
            archivo_sql = os.path.join(ruta_carpeta_individual, f"{nombre_BD}_respaldo_{tiempo_creacion}.sql")

            # Realizar el respaldo dual
            self.backup_sqlite_dual(ruta_sqlite_origen, archivo_sqlite, archivo_sql)

    def backup_sqlite_dual(self, ruta_origen_sqlite, ruta_destino_sqlite, ruta_destino_sql):
        """
        Crea un respaldo binario (sqlite) y uno textual (sql) desde ruta origen.
        """

        try:
            # Conexión a origen y destino
            origen = sqlite3.connect(ruta_origen_sqlite)
            destino = sqlite3.connect(ruta_destino_sqlite)

            with destino:
                origen.backup(destino)
 

            # Volcado SQL
            with io.open(ruta_destino_sql, "w", encoding="utf-8") as f:
                for linea in origen.iterdump():
                    f.write(f"{linea}\n")

        except Exception as e:
            print("Error durante el respaldo:", e)

        finally:
            origen.close()
            destino.close()

    def restaurar_sqlite(self, ruta_origen_bd, ruta_respaldo_bd):
        error_restau = None
        estado_restaur = False

        if not os.path.exists(ruta_respaldo_bd):
            error_restau = "No se encuentra el archivo de respaldo (.sqlite).Imposible continuar"
            estado_restaur= False
            return error_restau, estado_restaur

        try:
            """
            Al parecer copy2 tiene la capacidad de reescribir el nombre de un archivo.
            En este caso, como ambas rutas son exactas, es decir, NO son directorios, copy2
            toma el nombre ya establecido en la ruta origen (es decir, el nombre del archivo),
            y lo mantiene a pesar de ser diferente del que posee la ruta_respaldo_bd (ese nombre con fecha).
            Cosa diferente sucedería si se le pasara un directorio. Ahí, el nombre se mantiene.
            """
            shutil.copy2(ruta_respaldo_bd, ruta_origen_bd)

            estado_restaur = True

            return error_restau, estado_restaur
        except Exception as e:
            error_restau = e
            estado_restaur = False

            return error_restau, estado_restaur 

    def restaurar_desde_sql(self, ruta_respaldo_bd, ruta_origen_bd):

        error_restau = None 
        estado_restaur = False

        if not os.path.exists(ruta_respaldo_bd):
            error_restau = f"[ERROR] El archivo .sql no existe: {ruta_respaldo_bd}"
            estado_restaur = False

            return error_restau, estado_restaur

        # Elimina la base de datos anterior si existe
        if os.path.exists(ruta_origen_bd):
            os.remove(ruta_origen_bd)

        try:
            with sqlite3.connect(ruta_origen_bd) as conn:
                with open(ruta_respaldo_bd, "r", encoding="utf-8") as archivo_sql:
                    instrucciones_sql = archivo_sql.read()

                # Ejecutar múltiples instrucciones SQL
                conn.executescript(instrucciones_sql)

            estado_restaur = True
            return error_restau, estado_restaur

        except Exception as e:
            error_restau = f"[ERROR] Error al ejecutar el archivo SQL: {e}"
            estado_restaur = False

            return error_restau, estado_restaur

    def Verificar_Intervalo_RespalAutomic(self):
        """
        Verifica si ha transcurrido el intervalo (días, meses, años) desde el último respaldo
        para cada base de datos en lista_archivos.

        Retorna un diccionario con el estado True/False para cada BD.
        """
        def extraer_nombre_bd(nombre_archivo):
            """
            Dado un nombre como BD_TAGS_respaldo_2025-08-07_09-34.sqlite
            devuelve: BD_TAGS
            """
            nombre_bd = os.path.basename(nombre_archivo).split("_respaldo_") [0]

            return nombre_bd

        def ordenar_Y_filtrar():
            #Obtencion de Archivo de restauración más reciente
            ruta_resguardos_bd_Sistema = os.path.join(get_data_dir(),"BDs", "Resguardos_BD")

            lista_sqlite, lista_sql = filtrar_archivos_por_extension_BD(ruta_resguardos_bd_Sistema)

            #Procesamiento de datos (ordenamos por base de datos y seleccionamos el más reciente)
            grupos_sqlite = defaultdict(list)

            grupos_sql = defaultdict(list)

            for archivo in lista_sqlite:
                nombre_bd = extraer_nombre_bd(archivo)

                grupos_sqlite[nombre_bd].append(archivo)

            for archivo in lista_sql:
                nombre_bd = extraer_nombre_bd(archivo)

                grupos_sql[nombre_bd].append(archivo)

            archivos_mas_recientes_sqlite = {}
            archivos_mas_recientes_sql = {}

            for nombre_bd, archivos in grupos_sqlite.items():
                archivo_reciente = obtener_archivo_mas_reciente_ResplArch(archivos)
                archivos_mas_recientes_sqlite[nombre_bd] = archivo_reciente

            for nombre_bd, archivos in grupos_sql.items():
                archivo_reciente = obtener_archivo_mas_reciente_ResplArch(archivos)
                archivos_mas_recientes_sql[nombre_bd] = archivo_reciente

            return archivos_mas_recientes_sqlite, archivos_mas_recientes_sql

        def unificar_estados(estados_sqlite: dict, estados_sql: dict) -> dict:
            estados_unificados = {}

            # Unir todas las claves únicas de ambos diccionarios
            todas_las_bases = set(estados_sqlite) | set(estados_sql)

            for nombre_bd in todas_las_bases:
                estados_unificados[nombre_bd] = {
                    "estado_sqlite": estados_sqlite.get(nombre_bd, False),
                    "estado_sql": estados_sql.get(nombre_bd, False)
                }

            return estados_unificados

        def evaluar_respaldo(archivos_mas_recientes, datos_spins):

            estados = {}

            for nombre_bd, ruta_archivo in archivos_mas_recientes.items():
                try:
                    nombre_archivo = os.path.basename(ruta_archivo)
                    fecha_str = nombre_archivo.split("_respaldo_")[1].replace(".sqlite", "").replace(".sql", "")
                    fecha_archivo = datetime.strptime(fecha_str, "%Y-%m-%d_%H-%M")

                    fecha_objetivo = fecha_archivo + relativedelta(
                        days=datos_spins["dias"],
                        months=datos_spins["meses"],
                        years=datos_spins["años"]
                    )

                    nombre_arch = f"nombre_arch-{nombre_bd}"

                    estados[nombre_bd] = datetime.now() >= fecha_objetivo
         
                
                except Exception:
                    estados[nombre_bd] = False

            return estados

        archivos_mas_recientes_sqlite, archivos_mas_recientes_sql = ordenar_Y_filtrar()

        datos_spins = leer_archivo_recurrente("Archivo_Recurrente_Spinn.json", "json")

        estados_respaldo_sqlite = evaluar_respaldo(archivos_mas_recientes_sqlite, datos_spins)
        estados_respaldo_sql = evaluar_respaldo(archivos_mas_recientes_sql, datos_spins)

        estados_unificados = unificar_estados(estados_respaldo_sqlite, estados_respaldo_sql)

        return estados_unificados

    def Eliminar_ArchivosRes_Antiguos(self, lista_sqlite, lista_sql, num_archivos_a_mantener=3):
        """
        Elimina archivos antiguos dejando solo `num_archivos_a_mantener` por carpeta.
        """
        

        def extraer_nombre_bd(nombre_archivo):
            return os.path.basename(nombre_archivo).split("_respaldo_")[0]

        def extraer_fecha(nombre_archivo):
            try:
                fecha_str = nombre_archivo.split("_respaldo_")[1].replace(".sqlite", "").replace(".sql", "")
                return datetime.strptime(fecha_str, "%Y-%m-%d_%H-%M")
            except Exception:
                return datetime.min

        def eliminar_excedentes(grupo_archivos, num_archivos_a_mantener):
            estados = []  # Lista para guardar todos los mensajes de estado
            errores = []  # Lista para guardar todos los mensajes de error

            for nombre_bd, archivos in grupo_archivos.items():
                # Ordenar del más reciente al más antiguo
                archivos_ordenados = sorted(archivos, key=extraer_fecha, reverse=True)
 
                archivos_a_eliminar = archivos_ordenados[num_archivos_a_mantener:]

                for archivo in archivos_a_eliminar:
                    try:
                        os.remove(archivo)
                        estados.append(f"[OK] {nombre_bd} → Eliminado archivo antiguo: {archivo}")
                    except Exception as e:
                        errores.append(f"[ERROR] {nombre_bd} → No se pudo eliminar {archivo}: {e}")

            # Si no hubo mensajes, devolver None para mantener compatibilidad
            return (estados if estados else None, errores if errores else None)

        # Agrupamos los archivos
        grupos_sqlite = defaultdict(list)
        grupos_sql = defaultdict(list)

        for archivo in lista_sqlite:
            nombre_bd = extraer_nombre_bd(archivo)
            grupos_sqlite[nombre_bd].append(archivo)

        for archivo in lista_sql:
            nombre_bd = extraer_nombre_bd(archivo)
            grupos_sql[nombre_bd].append(archivo)

        # Aplicamos eliminación
        estado_sqlite, error_sqlite = eliminar_excedentes(grupos_sqlite, num_archivos_a_mantener)
        estado_sql, error_sql = eliminar_excedentes(grupos_sql, num_archivos_a_mantener)

        return estado_sqlite, error_sqlite, estado_sql, error_sql



 
