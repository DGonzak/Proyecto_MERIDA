import os

import sqlalchemy as sqlal 
from BDs_Functions.Models_BD import BD_Comb_Teclas as Mbd
from sqlalchemy.orm import Session, close_all_sessions, sessionmaker

from Lib_Extra.Rutas_Gestion import get_data_dir


class BD_ComTecl_Functions ():

    def __init__ (self):
        #para la conexión, no para la creación de la bD
        #para la conexión, no para la creación de la bD
        self.ruta_bd = os.path.join(get_data_dir(),"BDs","BD_ComTecl.sqlite")
        self.conexion = sqlal.create_engine(f"sqlite:///{self.ruta_bd}", future=True)


    def registrar_nuevas_listas(self, nueva_lista):
        """
        Registra un nuevo objeto en la base de datos.

        Parámetros:
        - nueva_lista: Instancia del modelo `Mbd` que representa una combinación 
        de teclas nueva.
        """
        with Session(self.conexion) as Sesion_ComTecl:
            Sesion_ComTecl.add(nueva_lista)
            Sesion_ComTecl.commit()

    def obtener_registros(self, modo: str = "lista"):
        """
        Obtiene todos los registros de combinaciones de teclas almacenados en la 
        base de datos.

        Parámetros:
        - modo (str): Forma de retorno. "lista" para una lista de tuplas, 
                    "diccionario" para un diccionario indexado por ID.

        Retorna:
        - list o dict: Registros en la forma solicitada según el modo.
        """
        lista_registros = []
        dict_registros = {}

        with Session(self.conexion) as Sesion_ComTecl:
            registros_get = Sesion_ComTecl.query(
                Mbd.ID,
                Mbd.nombre_CombTeclas,
                Mbd.Comb_Teclas,
                Mbd.Desc_acción
            ).all()

        for i in registros_get:
            if modo == "lista":
                lista_registros.append(i)
            elif modo == "diccionario":
                # Puedes usar el ID como clave, o el nombre del atajo
                dict_registros[i.ID] = {
                    "nombre": i.nombre_CombTeclas,
                    "atajo": i.Comb_Teclas,
                    "descripcion": i.Desc_acción
                }

        return lista_registros if modo == "lista" else dict_registros

    def eliminar_registros (self, id_get):
        """
        Elimina un registro de la base de datos según su ID.

        Parámetros:
        - id_get: ID del registro a eliminar.
        """

        with Session(self.conexion) as Sesion_ComTecl:
            """Se realiza una consulta y se filtra mediante una ID que será igual a lo que se pase por id_get"""

            Sesion_ComTecl.query(Mbd).filter_by(ID = id_get).delete()
            Sesion_ComTecl.commit()

    def validar_unica_ComTec (self, Comb_a_Verificar:str ):
        """
        Verifica si una combinación de teclas ya existe en la base de datos.

        Parámetros:
        - Comb_a_Verificar (str): Combinación a verificar.

        Retorna:
        - Mbd o None: Registro si existe, None si no existe.
        """

        Combinación_a_verificar_get:Mbd = None

        with Session(self.conexion) as Sesion_ComTecl:

            Combinación_a_verificar_get = Sesion_ComTecl.query(Mbd).filter_by(Comb_Teclas = Comb_a_Verificar).first()

        return Combinación_a_verificar_get

    def asegurar_entradas_preder(self):
        """
        Inserta combinaciones de teclas predeterminadas si no existen ya en la base 
        de datos.

        Esta función evita duplicados al verificar el nombre de cada entrada antes 
        de insertarla.
        """

        # Lista de combinaciones predeterminadas (puedes ampliarla fácilmente)
        atajos_predeterminados = [
            {
                "nombre_CombTeclas": "Guardar",
                "Comb_Teclas": "<Control>S",
                "Desc_acción": "Guardar archivo en el editor"
            },
            {
                "nombre_CombTeclas": "Abrir",
                "Comb_Teclas": "<Control>N",
                "Desc_acción": "Abrir un archivo desde el editor"
            },
            {
                "nombre_CombTeclas": "Mostrar/Ocultar_Barra_Lateral",
                "Comb_Teclas": "<Control>D",
                "Desc_acción": "Muestra u oculta la barra lateral (la que contiene el árbol de archivos)."
            },
            {
                "nombre_CombTeclas": "Crear_Nuevas_Notastex",
                "Comb_Teclas": "<Control>A",
                "Desc_acción": "Crea nuevas notas en la barra lateral (la que contiene las notas como tal)."
            },
            {
                "nombre_CombTeclas": "Crear_Nuevo_Archivo",
                "Comb_Teclas": "<Control>G",
                "Desc_acción": "Limpia (elimina) todo el contenido del editor."
            }
            # Puedes seguir añadiendo más entradas aquí
        ]

        with Session(self.conexion) as sesion:
            for atajo in atajos_predeterminados:
                # Verifica si ya existe un atajo con el mismo nombre (para no duplicar)
                existe = sesion.query(Mbd).filter_by(
                    nombre_CombTeclas=atajo["nombre_CombTeclas"]
                ).first()

                if not existe:
                    nuevo_atajo = Mbd(
                        nombre_CombTeclas=atajo["nombre_CombTeclas"],
                        Comb_Teclas=atajo["Comb_Teclas"],
                        Desc_acción=atajo["Desc_acción"]
                    )
                    sesion.add(nuevo_atajo)

            sesion.commit()

    def obtener_registros_ID(self, id_get):
        """
        Obtiene un registro específico según su ID.

        Parámetros:
        - id_get: ID del registro a buscar.

        Retorna:
        - dict o None: Diccionario con los campos del registro si existe, None si no.
        """

        with Session(self.conexion) as Sesion_ComTecl:

            registro_get = Sesion_ComTecl.query(Mbd).filter_by(ID = id_get).first()

            if registro_get:

                return {
                    "ID": registro_get.ID,
                    "nombre": registro_get.nombre_CombTeclas,
                    "atajo": registro_get.Comb_Teclas,
                    "descripción": registro_get.Desc_acción
                }
            else:
                return None                     

    def eliminar_todas_comteclas(self):
        """
        Elimina todos los registros de combinaciones de teclas en la base de datos.
        """
        #Elimina todos los registros de combinaciones de teclas en la base de datos

        with Session(self.conexion) as Sesion_ComTecl:

            Sesion_ComTecl.query(Mbd).delete()
            Sesion_ComTecl.commit()

    def modificar_registros (self, ID_GET_MOD, nuevo_nombre_get=None, nuevo_atajo_get=None, nueva_descripción_get=None):
        """
        Modifica campos específicos de un registro existente.

        Parámetros:
        - ID_GET_MOD: ID del registro a modificar.
        - nuevo_nombre_get (str, opcional): Nuevo nombre del atajo.
        - nuevo_atajo_get (str, opcional): Nueva combinación de teclas.
        - nueva_descripción_get (str, opcional): Nueva descripción de la acción.

        Retorna:
        - bool: True si se modificó exitosamente, False si no se encontró el registro.
        """

        """
        Notas: Esta función tiene la capacidad de modificar uno o varios campos de un 
        registro de un registro en la base de datos. Para ello, para que no de error, 
        se inicializa todos los campos precindibles, exceptuando el ID, como None."""
        
        with Session(self.conexion) as Sesion_ComTecl:

            registro_get = Sesion_ComTecl.query(Mbd).filter_by(ID=ID_GET_MOD).first()

            if registro_get:
                if nuevo_nombre_get is not None: #verificamos que tenga un valor DISTINTO a None

                    registro_get.nombre_CombTeclas = nuevo_nombre_get

                if nuevo_atajo_get is not None:

                    registro_get.Comb_Teclas = nuevo_atajo_get

                if nueva_descripción_get is not None:

                    registro_get.Desc_acción = nueva_descripción_get

                Sesion_ComTecl.commit()

                return True #La modificación se realizó con exito

            else:

                return False #La modificación fallo

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