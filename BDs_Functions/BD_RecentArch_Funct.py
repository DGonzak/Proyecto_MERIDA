import os

import sqlalchemy as sqlal 
from BDs_Functions.Models_BD import BD_Recient_Arch as Mbd
from sqlalchemy.orm import Session, close_all_sessions, sessionmaker
from sqlalchemy import desc, asc
from Lib_Extra.Rutas_Gestion import get_data_dir

class BD_Recient_Arch_Functions ():

	def __init__(self):

		#para la conexión, no para la creación de la bD
		self.ruta_bd = os.path.join(get_data_dir(),"BDs","BD_RecentArch.sqlite")
		self.conexion = sqlal.create_engine(f"sqlite:///{self.ruta_bd}", future=True)


	def registrar_nuevas_listas(self, nueva_lista):
		"""
		Registra una nueva entrada en la base de datos de archivos recientes.

		Parámetros:
		- nueva_lista: Instancia del modelo `Mbd` representando una nueva entrada (etiqueta, ruta, fechas, etc.).
		"""
		with Session(self.conexion) as Sesion_RecentArch:
			Sesion_RecentArch.add(nueva_lista)
			Sesion_RecentArch.commit()


	def validar_unico (self, etiqueta_a_verificar:str ):
		"""
		Verifica si ya existe una etiqueta con el mismo nombre en la base de datos.

		Parámetros:
		- etiqueta_a_verificar (str): Nombre de la etiqueta que se desea validar.

		Retorna:
		- Mbd o None: El registro(Mbd) si existe una coincidencia, o None si es único.
		"""

		etiqueta_a_verificar_get:Mbd = None

		with Session(self.conexion) as Sesion_RecentArch:

			etiqueta_a_verificar_get = Sesion_RecentArch.query(Mbd).filter_by(RA_Nombre_Etiqueta = etiqueta_a_verificar).first()

		return etiqueta_a_verificar_get

	def obtener_registros(self, modo:str= "diccionario"):
		"""
		Obtiene todos los registros almacenados en la base de datos de archivos recientes,
		ordenados por la fecha de creación (ascendente).

		Parámetros:
		- modo (str): Puede ser "diccionario" o "lista". 
			- "diccionario": Devuelve un diccionario indexado por ID.
			- "lista": Devuelve una lista de objetos Mbd.

		Retorna:
		- dict o list: Los registros obtenidos según el modo indicado.
		"""

		lista_registros = []
		lista_diccionario = {}

		with Session(self.conexion) as Sesion_RecentArch:

			"""Usamos la fecha de creación para ordenarlos en orden ascendentes (más antiguo primero)
			mediante asc. Si queremos lo contrario, orden descendente, se usa desc."""
			registros_get = Sesion_RecentArch.query(Mbd).order_by(asc(Mbd.Fecha_de_Registro)).all()

			if modo == "diccionario":

				for registro in registros_get :

					#Utilizamos el ID como clave

					lista_diccionario[registro.ID] = {
						"RA_Nombre_Etiqueta": registro.RA_Nombre_Etiqueta,
						"RA_Ruta_Carpeta": registro.RA_Ruta_Carpeta,
						"Fecha_de_Registro": registro.Fecha_de_Registro,
						"Fecha_de_Modificación": registro.Fecha_de_Modificación
					}
				return lista_diccionario

			elif modo == "lista":
				for registro in registros_get:
					lista_registros.append(registro)
				return lista_registros

	def eliminar_todos_registros(self):
		"""
		Elimina todos los registros de la base de datos de archivos recientes.
		Esta acción borra completamente el historial registrado.
		"""

		with Session(self.conexion) as Sesion_RecentArch:

			Sesion_RecentArch.query(Mbd).delete()
			Sesion_RecentArch.commit()
			
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