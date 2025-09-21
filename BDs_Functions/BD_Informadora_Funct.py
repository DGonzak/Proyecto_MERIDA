import os
import sqlalchemy as sqlal
from sqlalchemy.orm import Session, close_all_sessions, sessionmaker
from BDs_Functions.Models_BD import BDInformadora as Mbd
import pytz
from datetime import datetime

from Lib_Extra.Rutas_Gestion import get_data_dir

class BD_Informadora_Functions ():

    def __init__ (self):
        #para la conexión, no para la creación de la bD
        self.ruta_bd = os.path.join(get_data_dir(), "BDs", "BD_Informadora.sqlite")
        self.conexion = sqlal.create_engine(f"sqlite:///{self.ruta_bd}", future=True)

        self.registro_predeterminado = [

            {
                "nombre": "BD_ComTecl",
                "descripcion": "Base de datos destinada para almacenar las combinaciones de teclas del programa",
                "estado": False,
                "tipo": "SQLite",
                "origen": "Sistema",
                "permisos": "lectura/escritura",
                "ubicacion": "Sin comprobar",
                "ubicacion_respaldo": "Sin comprobar"
            },
            {
                "nombre": "BD_RecentArch",
                "descripcion": "Base de datos destinada al almacenamiento de los <<archivos recientes>> abierto en el editor.",
                "estado": False,
                "tipo": "SQLite",
                "origen": "Sistema",
                "permisos": "lectura/escritura",
                "ubicacion": "Sin comprobar",
                "ubicacion_respaldo": "Sin comprobar"
            },
            {
                "nombre": "BD_TAGS",
                "descripcion": "Base de datos para almacenar las rutas de carpetas y etiquetas respectivas.",
                "estado": False,
                "tipo": "SQLite",
                "origen": "Sistema",
                "permisos": "lectura/escritura",
                "ubicacion": "Sin comprobar",
                "ubicacion_respaldo": "Sin comprobar"
            },
            {
                "nombre": "BD_Informadora",
                "descripcion": "Base de datos para almacenar la información de otras bases de datos del sistema",
                "estado": False,
                "tipo": "SQLite",
                "origen": "Sistema",
                "permisos": "lectura/escritura",
                "ubicacion": "Sin comprobar",
                "ubicacion_respaldo": "Sin comprobar"
            }

        ]

    def registrar_nuevas_BD(self, nueva_BD):
        """
        Registra un nuevo objeto en la base de datos.

        Parámetros:
        - nueva_BD: Instancia del modelo `Mbd` que representa el conjunto de datos para
        una nueva base de datos
        """
        with Session(self.conexion) as Sesion_Inform:
            Sesion_Inform.add(nueva_BD)
            Sesion_Inform.commit()

    def obtener_registros(self, modo: str = "lista"):
        """
        Obtiene TODOS los registros de la "base de datos" almacenados en la 
        base de datos.

        Parámetros:
        - modo (str): Forma de retorno. "lista" para una lista de tuplas, 
                    "diccionario" para un diccionario indexado por ID.

        Retorna:
        - list o dict: Registros en la forma solicitada según el modo.
        """
        lista_registros = []
        dict_registros = {}

        with Session(self.conexion) as Sesion_Inform:
            registros_get = Sesion_Inform.query(
                Mbd.id,
                Mbd.nombre,
                Mbd.descripcion,
                Mbd.estado,
                Mbd.tipo,
                Mbd.origen,
                Mbd.permisos,
                Mbd.primera_actualizacion,
                Mbd.ultima_actualizacion,
                Mbd.ubicacion,
                Mbd.ubicacion_respaldo
            ).all()

        for i in registros_get:
            if modo == "lista":
                lista_registros.append(i)
            
            elif modo == "diccionario":
                dict_registros[i.id] = {
                    "nombre": i.nombre,
                    "descripcion": i.descripcion,
                    "estado": i.estado,
                    "tipo": i.tipo,
                    "origen": i.origen,
                    "permisos": i.permisos,
                    "primera_actualizacion": i.primera_actualizacion,
                    "ultima_actualizacion": i.ultima_actualizacion,
                    "ubicacion": i.ubicacion,
                    "ubicacion_respaldo" : i.ubicacion_respaldo
                }

        return lista_registros if modo == "lista" else dict_registros

    def validar_unico (self, nombreBD_a_verificar:str ):
        """
        Verifica si ya existe una etiqueta con el mismo nombre en la base de datos.

        Parámetros:
        - etiqueta_a_verificar (str): Nombre de la etiqueta que se desea validar.

        Retorna:
        - Mbd o None: El registro(Mbd) si existe una coincidencia, o None si es único.
        """

        Nombre_BD_a_Verificar_get:Mbd = None

        with Session(self.conexion) as Sesion_Inform:

            Nombre_BD_a_Verificar_get = Sesion_Inform.query(Mbd).filter_by(nombre = nombreBD_a_verificar).first()

        return Nombre_BD_a_Verificar_get

    def obtener_registros_ID(self, id_get):

        """
        Obtiene un registro específico según su ID.

        Parámetros:
        - id_get: ID del registro a buscar.

        Retorna:
        - dict o None: Diccionario con los campos del registro si existe, None si no.
        """

        with Session(self.conexion) as Sesion_Inform:

            registro_get = Sesion_Inform.query(Mbd).filter_by(id = id_get).first()

            if registro_get:

                return {
                    "id": registro_get.id,
                    "nombre": registro_get.nombre,
                    "descripcion": registro_get.descripcion,
                    "estado": registro_get.estado,
                    "tipo": registro_get.tipo,
                    "origen": registro_get.origen,
                    "permisos": registro_get.permisos,
                    "primera_actualizacion": registro_get.primera_actualizacion,
                    "ultima_actualizacion": registro_get.ultima_actualizacion,
                    "ubicacion": registro_get.ubicacion,
                    "ubicacion_respaldo": registro_get.ubicacion_respaldo
                }
            else:
                return None

    def eliminar_registros (self, id_get):
        """
        Elimina un registro de la base de datos según su ID.

        Parámetros:
        - id_get: ID del registro a eliminar.
        """

        with Session(self.conexion) as Sesion_Inform:
            """Se realiza una consulta y se filtra mediante una ID que será igual a lo que se pase por id_get"""

            Sesion_Inform.query(Mbd).filter_by(id = id_get).delete()
            Sesion_Inform.commit()

    def verificar_estado_BD(self, id_get):
        """
        Obtiene el registro específico según una id proporcionada para devolver unicamente
        el estado registrado.

        Parámetros:
        - id_get: ID del registro a buscar.

        Retorna:
        - True o False dependiendo del estado de la base de datos registrada.
        """

        with Session(self.conexion) as Sesion_Inform:

            registro_get = Sesion_Inform.query(Mbd).filter_by(id = id_get).first()

            if registro_get:

                return registro_get.estado

    def Obtener_Ruta_BD(self, id_get=None, nombre_BD_get=None):
        """
        Obtiene el registro específico según una id proporcionada para devolver unicamente
        la ruta registrada.

        Parámetros:
        - id_get: ID del registro a buscar.

        Retorna:
        - La ruta registrada en la base de datos (Propiedad Ubicación).
        """

        with Session(self.conexion) as Sesion_Inform:

            if not id_get == None:
                registro_get = Sesion_Inform.query(Mbd).filter_by(id = id_get).first()
            
            elif not nombre_BD_get == None:

                registro_get = Sesion_Inform.query(Mbd).filter_by(nombre=nombre_BD_get).first()

            if registro_get:

                return registro_get.ubicacion

    def obtener_registros_origen(self, origen_get):
        """
        Devuelve una lista de registros que coinciden con el origen proporcionado.

        Parámetros:
            - origen_get (str): El origen a buscar.

        Retorna:
            - Una lista de diccionarios, cada uno representando un registro coincidente.
            - Si no se encuentran resultados, retorna una lista vacía.
        """
        with Session(self.conexion) as Sesion_Inform:
            registros_get = Sesion_Inform.query(Mbd).filter_by(origen=origen_get).all()

            resultados = []

            for reg in registros_get:
                resultados.append({
                    "id": reg.id,
                    "nombre": reg.nombre,
                    "descripcion": reg.descripcion,
                    "ubicacion": reg.ubicacion
                })

            return resultados

    def asegurar_bds_registro_preder(self):
        """
        Verifica que todos los registros predeterminados de `self.registro_predeterminado` existan en la base de datos.
        Si un registro no existe, lo crea con la información especificada en el diccionario correspondiente.
        """
        
        with Session(self.conexion) as Sesion_Inform:

            for registro in self.registro_predeterminado:

                #Verificación de existencia
                existe = Sesion_Inform.query(Mbd).filter_by(nombre=registro["nombre"]).first()

                if not existe:

                    nuevo_registro = Mbd(
                        nombre=registro["nombre"],
                        descripcion=registro["descripcion"],
                        estado=registro["estado"],
                        tipo=registro["tipo"],
                        origen=registro["origen"],
                        permisos=registro["permisos"],
                        ubicacion=registro["ubicacion"],
                        ubicacion_respaldo=registro["ubicacion_respaldo"]
                        )
                    Sesion_Inform.add(nuevo_registro)

            Sesion_Inform.commit()

    def asegurar_bd_registro_preder_INDIVIDUAL(self, nombre_BD_filtr):
        """
        Verifica que exista un registro específico en la base de datos según su nombre.
        Si no existe, lo crea usando la información definida en `self.registro_predeterminado`.

        Args:
            nombre_BD_filtr (str): Nombre de la base de datos a verificar o crear.
        """
        
        with Session(self.conexion) as Sesion_Inform:

            # Buscar el diccionario correspondiente en la lista
            registro = next(
                (d for d in self.registro_predeterminado if d["nombre"] == nombre_BD_filtr),
                None
            )

            # Si no se encuentra el registro, no se hace nada
            if not registro:
                return

            # Verificar si ya existe en la base de datos
            existe = Sesion_Inform.query(Mbd).filter_by(nombre=registro["nombre"]).first()

            if not existe:
                nuevo_registro = Mbd(
                    nombre=registro["nombre"],
                    descripcion=registro["descripcion"],
                    estado=registro["estado"],
                    tipo=registro["tipo"],
                    origen=registro["origen"],
                    permisos=registro["permisos"],
                    ubicacion=registro["ubicacion"],
                    ubicacion_respaldo=registro["ubicacion_respaldo"]
                )
                Sesion_Inform.add(nuevo_registro)

            Sesion_Inform.commit()

    def modificar_UNA_propiedad(self, nombre_BD_get, propiedad_a_cambiar, nuevo_cont_propiedad):
        """
        Modifica una propiedad específica de un registro en la base de datos.

        Args:
            nombre_BD_get : Nombre de la base de datos a modificar.
            propiedad_a_cambiar : Nombre de la columna/atributo a modificar.
            nuevo_cont_propiedad : Nuevo contenido que se asignará a la propiedad indicada.
        """
        with Session(self.conexion) as Sesion_Inform:
            registro_get = Sesion_Inform.query(Mbd).filter_by(nombre=nombre_BD_get).first()

            if registro_get:
                setattr(registro_get, propiedad_a_cambiar, nuevo_cont_propiedad)
                
                Sesion_Inform.commit()

    def reconstruir_base_de_datos_completa(self):
        """
        Cierra las conexiones activas, elimina el archivo físico,
        recrea la base de datos y repuebla los datos predeterminados.
        """
        error_reconstr = None 
        estado_reconstr = False

        try: 
            close_all_sessions()
            self.conexion.dispose()
            self.conexion = sqlal.create_engine(f"sqlite:///{self.ruta_bd}", future=True)

            estado_reconstr = True

        except Exception as e:
            error_reconstr = e

        return estado_reconstr, error_reconstr

    def obtener_UNA_propiedad_ID(self, id_get, propiedad_a_obtener):
        """
        Devuelve el valor de una propiedad específica de un registro,
        buscado por su ID.

        Parámetros:
        - id_get: ID del registro a buscar.
        - propiedad_a_obtener: nombre de la propiedad a obtener (str).

        Retorna:
        - El valor de la propiedad si se encuentra, o None si no existe.
        """
        with Session(self.conexion) as Sesion_Inform:
            registro = Sesion_Inform.query(Mbd).filter_by(id=id_get).first()

            if registro:
                return getattr(registro, propiedad_a_obtener, None)
            else:
                return None

    def obtener_id_registro(self, propiedad_a_buscar, contenido_propiedad):
        """
        Devuelve el ID de un registro que coincide con una propiedad dada.

        Parámetros:
        - propiedad_a_buscar: El nombre de la propiedad por la que se desea buscar (str).
        - contenido_propiedad: El valor exacto de la propiedad (str, int, etc.).

        Retorna:
        - El ID del registro si se encuentra, o None si no existe.
        """
        with Session(self.conexion) as Sesion_Inform:
            # Buscar el primer registro donde propiedad == valor dado
            registro = Sesion_Inform.query(Mbd).filter(getattr(Mbd, propiedad_a_buscar) == contenido_propiedad).first()

            if registro:
                return registro.id
            
            else:
                return None

    def obtener_TODAS_las_BDs(self):
        """
        Esta función obtiene todas las bases de datos registradas en la bd informadora y 
        devuelve unicamente su NOMBRE.
        """
        lista_nombres_bds_R = [] 

        #Para las bases de datos del sistema
        for nombre_bd in self.registro_predeterminado:

            with Session(self.conexion) as Sesion_Inform:
                registro_get = Sesion_Inform.query(Mbd).filter_by(nombre=nombre_bd["nombre"]).first()

                if registro_get:
                    nombre_get = registro_get.nombre

                    lista_nombres_bds_R.append(nombre_get)



        return lista_nombres_bds_R

    def convertir_horaUTC_a_horalocal(self, hora_UTC, region_a_convertir):
        """
        Convierte una hora UTC a hora local según la región especificada.

        :param hora_UTC: datetime en formato UTC (puede ser naive o con tzinfo=pytz.utc)
        :param region_a_convertir: string con la zona horaria destino (ej. "America/La_Paz")
        :return: datetime convertido a la hora local de la región
        """

        # Lista de regiones permitidas (puedes ampliarla)
        lista_regiones = [
            "America/La_Paz",
            "America/Lima",
            "America/Bogota",
            "UTC"
        ]

        if region_a_convertir not in lista_regiones:
            raise ValueError(f"Región no soportada: {region_a_convertir}")

        # Asegurar que hora_UTC tenga información de zona horaria UTC
        if hora_UTC.tzinfo is None:
            hora_UTC = hora_UTC.replace(tzinfo=pytz.utc)

        # Convertir a la zona horaria destino
        zona_destino = pytz.timezone(region_a_convertir)
        hora_local = hora_UTC.astimezone(zona_destino)

        return hora_local, region_a_convertir
