

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GObject, Gio

import sqlalchemy as sqlal 
from BDs_Functions.Models_BD import BD_Moduls as Mbd
from sqlalchemy.orm import Session, close_all_sessions
import os

from Lib_Extra.Rutas_Gestion import get_data_dir
from Lib_Extra.Funciones_extras import mostrar_vent_IEO

class BD_Moduls_Functions():

    def __init__ (self):
        #para la conexión, no para la creación de la bD
        self.ruta_bd = os.path.join(get_data_dir(),"BDs", "BD_Moduls.sqlite")
        self.conexion = sqlal.create_engine(f"sqlite:///{self.ruta_bd}", future=True)


    def registrar_nuevas_listas(self, nueva_lista):
        """
        Registra una nueva etiqueta en la base de datos.

        Parámetros:
        - nueva_lista: Instancia del modelo `Mbd` con los datos de la etiqueta (nombre y ruta asociada).
        """
        with Session(self.conexion) as Sesion_Moduls:
            Sesion_Moduls.add(nueva_lista)
            Sesion_Moduls.commit()

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

        with Session(self.conexion) as Sesion_Moduls:
            registros_get = Sesion_Moduls.query(
                Mbd.ID,
                Mbd.Nombre_Modulo,
                Mbd.Identificador_Modulo,
                Mbd.Version_Modulo,
                Mbd.Autor_Modulo,
                Mbd.CorreoElectronico_Autor,
                Mbd.Descripcion_Modulo,
                Mbd.Arch_Principal_Ejecucion,
                Mbd.Recursos_Adicionales,
                Mbd.Dependencias_Especiales,
                Mbd.Estado_Modulo,
                Mbd.Fecha_Instalacion,
                Mbd.Ubicacion_Modulo
            ).all()

        for i in registros_get:
            if modo == "lista":
                lista_registros.append(i)
            
            elif modo == "diccionario":
                dict_registros[i.ID] = {
                    "nombre": i.Nombre_Modulo,
                    "identificador": i.Identificador_Modulo,
                    "version": i.Version_Modulo,
                    "autor": i.Autor_Modulo,
                    "correo": i.CorreoElectronico_Autor,
                    "descripcion": i.Descripcion_Modulo,
                    "arch_principal": i.Arch_Principal_Ejecucion,
                    "recursos": i.Recursos_Adicionales,
                    "dependencias": i.Dependencias_Especiales,
                    "estado": i.Estado_Modulo,
                    "fecha_instalacion": i.Fecha_Instalacion,
                    "ubicacion": i.Ubicacion_Modulo
                }

        return lista_registros if modo == "lista" else dict_registros

    def eliminar_registros (self, id_get):
        """
        Elimina un registro específico de la base de datos, dada su ID.

        Parámetros:
        - id_get: ID del registro que se desea eliminar.
        """

        with Session(self.conexion) as Sesion_Moduls:
            """Se realiza una consulta y se filtra mediante una ID que será igual a lo que se pase por id_get"""

            Sesion_Moduls.query(Mbd).filter_by(ID = id_get).delete()
            Sesion_Moduls.commit()

    def validar_unico(self, propiedad_a_verificar: str, contenido_a_buscar: str):
        """
        Verifica si un elemento ya existe en la base de datos usando la propiedad indicada.

        Parámetros:
        - propiedad_a_verificar (str): Nombre de la columna/atributo de Mbd que se usará para la búsqueda.
        - contenido_a_buscar (str): Valor que se desea buscar en la columna indicada.

        Retorna:
        - Mbd o None: Devuelve el registro encontrado si existe, o None si no hay coincidencias.
        """

        with Session(self.conexion) as Sesion_Moduls:
            # Obtener el atributo dinámicamente desde la clase Mbd
            columna = getattr(Mbd, propiedad_a_verificar, None)

            if columna is None:
                # Si la propiedad no existe, lanza un error para evitar consultas inválidas
                raise AttributeError(f"La propiedad '{propiedad_a_verificar}' no existe en el modelo Mbd.")

            # Realizar la búsqueda usando filter (no filter_by, porque filter_by no acepta expresiones dinámicas, al parecer)
            registro_encontrado = Sesion_Moduls.query(Mbd).filter(columna == contenido_a_buscar).first()

        return registro_encontrado

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

    def obtener_datos_simples_Registros(self):
        """
        Obtiene datos simples de todos los registros almacenados en la base de datos.
        Estos son: 
            -Nombre
            -Version
            -Icono (la ruta del icono)
        
        Estos datos son usados para mostrar los módulos en la pantalla de gestión de módulos,
        y además, para saber cuantos módulos hay en la base de datos.
        """

        diccionario_datos_simples = {}

        with Session(self.conexion) as Sesion_Moduls:
            registros_get = Sesion_Moduls.query(
                Mbd.ID,
                Mbd.Nombre_Modulo,
                Mbd.Version_Modulo,
                Mbd.Arch_Icono_Ubicacion
            ).all()

        for registro in registros_get:
            diccionario_datos_simples[registro.ID] = {
                "nombre_modulo": registro.Nombre_Modulo,
                "version": registro.Version_Modulo,
                "icono": registro.Arch_Icono_Ubicacion
            }

        return diccionario_datos_simples