

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GObject, Gio

import sqlalchemy as sqlal 
from BDs_Functions.Models_BD import BD_Tags_General as Mbd
from sqlalchemy.orm import Session, close_all_sessions, sessionmaker
import os

from Lib_Extra.Rutas_Gestion import get_data_dir
from Lib_Extra.Funciones_extras import mostrar_vent_IEO

class BD_TAGS_Functions ():

    def __init__ (self):
        #para la conexión, no para la creación de la bD
        self.ruta_bd = os.path.join(get_data_dir(),"BDs", "BD_TAGS.sqlite")
        self.conexion = sqlal.create_engine(f"sqlite:///{self.ruta_bd}", future=True)


    def registrar_nuevas_listas(self, nueva_lista):
        """
        Registra una nueva etiqueta en la base de datos.

        Parámetros:
        - nueva_lista: Instancia del modelo `Mbd` con los datos de la etiqueta (nombre y ruta asociada).
        """
        with Session(self.conexion) as Sesion_TAGS:
            Sesion_TAGS.add(nueva_lista)
            Sesion_TAGS.commit()

    def modificar_lista_existente(self, filtro_etiqueta=None,filtro_ruta=None, nueva_etiqueta=None,nueva_ruta=None):
        """
        Modifica una etiqueta existente en la base de datos, ya sea cambiando su nombre,
        su ruta, o ambos. Se requiere proporcionar al menos un filtro: `filtro_etiqueta` o `filtro_ruta`.

        Parámetros:
        - filtro_etiqueta (str): Nombre de la etiqueta a modificar (usado como filtro).
        - filtro_ruta (str): Ruta actual asociada a una etiqueta (usado como filtro alternativo).
        - nueva_etiqueta (str): Nuevo nombre de etiqueta (si se desea modificar).
        - nueva_ruta (str): Nueva ruta a asociar (si se desea modificar).

        Retorna:
        - True si la modificación fue exitosa.
        - False si no se encontró ningún registro que coincida.
        """
        with Session(self.conexion) as Sesion_TAGS:
            # Buscar registro por etiqueta o ruta
            if filtro_etiqueta:
                registro = Sesion_TAGS.query(Mbd).filter_by(Nombre_etiqueta=filtro_etiqueta).first()
            elif filtro_ruta:
                registro = Sesion_TAGS.query(Mbd).filter_by(Ruta_carpeta=filtro_ruta).first()
            else:
                raise ValueError("Debes proporcionar al menos 'filtro_etiqueta' o 'filtro_ruta'")

            # Si se encontró, modificar campos
            if registro:
                if nueva_etiqueta:
                    registro.Nombre_etiqueta = nueva_etiqueta
                if nueva_ruta:
                    registro.Ruta_carpeta = nueva_ruta

                Sesion_TAGS.commit()
                return True
            else:
                return False

    def obtener_registros (self):
        """
        Obtiene todos los registros de etiquetas almacenados en la base de datos.

        Retorna:
        - list: Lista de tuplas que contienen (ID, Nombre_etiqueta, Ruta_carpeta) para cada etiqueta registrada.
        """
        lista_registros = []

        with Session(self.conexion) as Sesion_TAGS:
            registros_get = Sesion_TAGS.query(
                Mbd.ID,
                Mbd.Nombre_etiqueta,
                Mbd.Ruta_carpeta).all()

        for i in registros_get:
            lista_registros.append(i)

        return lista_registros

    def eliminar_registros (self, id_get):
        """
        Elimina una etiqueta específica de la base de datos, dada su ID.

        Parámetros:
        - id_get: ID del registro (etiqueta) que se desea eliminar.
        """

        with Session(self.conexion) as Sesion_TAGS:
            """Se realiza una consulta y se filtra mediante una ID que será igual a lo que se pase por id_get"""

            Sesion_TAGS.query(Mbd).filter_by(ID = id_get).delete()
            Sesion_TAGS.commit()

    def validar_unico (self, etiqueta_a_verificar:str ):
        """
        Verifica si una etiqueta ya existe en la base de datos.

        Parámetros:
        - etiqueta_a_verificar (str): Nombre de la etiqueta a buscar.

        Retorna:
        - Mbd o None: Registro coincidente si existe(Mbd), o None si no se encuentra.
        """

        etiqueta_a_verificar_get:Mbd = None

        with Session(self.conexion) as Sesion_TAGS:

            etiqueta_a_verificar_get = Sesion_TAGS.query(Mbd).filter_by(Nombre_etiqueta = etiqueta_a_verificar).first()

        return etiqueta_a_verificar_get

    def obtener_registro_NombEtiq (self, etiqueta_nombre):
        """
        Recupera la ruta de carpeta asociada a una etiqueta específica por su nombre.

        Parámetros:
        - etiqueta_nombre (str): Nombre exacto de la etiqueta.

        Retorna:
        - str: Ruta asociada si se encuentra; de lo contrario, devuelve "No encontrado".
        """

        with Session(self.conexion) as Sesion_TAGS:

            registro_get = Sesion_TAGS.query(Mbd).filter_by(Nombre_etiqueta = etiqueta_nombre).first()

        return registro_get.Ruta_carpeta if registro_get else "No encontrado"

    def asegurar_etiqueta_predeterminada(self, parent, ruta_preder_get):
        """
        Verifica si existe la etiqueta 'Etiqueta Predeterminada' en la base de datos.
        Si no existe, la crea con una ruta fija.

        Paso adicional:
        - Comprueba si la ruta de dicha etiqueta existe como carpeta.
        - Si no existe, ofrece crearla mediante diálogo.

        Ruta por defecto:
        - /Documentos/MERIDA_EDITOR (Es decir, siempre en documentos de cualquier sistema)
        """
        self.ruta_preder_verificar = ruta_preder_get

        NOMBRE_CARPETA_GET = os.path.basename(os.path.normpath(self.ruta_preder_verificar))
        
        # Paso 1: Verificar si la carpeta existe
        if not os.path.isdir(self.ruta_preder_verificar):

            texto1 = f"No se ha detectado la carpeta predeterminada <<{NOMBRE_CARPETA_GET}>>."
            texto2 = "Sin esta carpeta, la ruta predeterminada no funcionará y puede causar errores en el programa."
            texto3 = f"¿Desea crearla ahora?\nRuta a crear: {self.ruta_preder_verificar}"

            # Mostrar diálogo para crear la carpeta
            dialog = Gtk.MessageDialog(
                transient_for=parent,
                modal=True,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.NONE,
                text="Error: Carpeta predeterminada ausente"
            )

            label1 = Gtk.Label(label=f"{texto1}\n\n{texto2}")
            label1.set_wrap(True)

            label2 = Gtk.Label(label=texto3)
            label2.set_wrap(True)

            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            vbox.set_vexpand(True)
            vbox.set_hexpand(True)
            vbox.append(label1)
            vbox.append(label2)

            dialog.get_content_area().append(vbox)
            dialog.add_button("Sí, crear carpeta", Gtk.ResponseType.OK)
            dialog.add_button("No, no crear carpeta", Gtk.ResponseType.CANCEL)
            dialog.connect("response", self.on_dialog_response)

            dialog.present()


        # Paso 2: Verificar o crear la etiqueta en base de datos
        with Session(self.conexion) as Sesion_TAGS:
            etiqueta = Sesion_TAGS.query(Mbd).filter_by(Nombre_etiqueta="Etiqueta Predeterminada").first()

            if not etiqueta:
                etiq_preder = Mbd(
                    Nombre_etiqueta="Etiqueta Predeterminada",
                    Ruta_carpeta=self.ruta_preder_verificar
                )
                Sesion_TAGS.add(etiq_preder)
                Sesion_TAGS.commit()

    def on_dialog_response(self, dialog, response):
        """
        Callback ejecutado al cerrar el diálogo que propone crear la carpeta predeterminada.

        Si el usuario acepta, se intenta crear la carpeta. Si falla, se informa del error.
        """
        ruta_a_usar = self.ruta_preder_verificar

        if response == Gtk.ResponseType.OK:
            try:
                os.makedirs(ruta_a_usar, exist_ok=True)
            except Exception as e:
                mostrar_vent_IEO(
                    dialog.get_transient_for(),
                    "Error al crear carpeta",
                    f"No se pudo crear la carpeta predeterminada.\nDetalles: {e}",
                    Gtk.MessageType.ERROR,
                    1,
                    "Aceptar"
                )

        dialog.destroy()
        
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