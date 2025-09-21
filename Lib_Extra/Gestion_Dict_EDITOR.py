


class Gestor_Variable_ActuEtiquetas:
	def __init__(self):

		# Diccionario que se usa para las etiquetas "actuales" del editor
		self.Lista_Etiquetas_SUP = {}


	def agregar_contenido(self, etiqueta, ruta):
		#Agrega o actualiza el contenido del diccionario
		self.Lista_Etiquetas_SUP[etiqueta] = ruta

	def limpiar_contenido(self):
		#Borra el contenido del diccionario
		self.Lista_Etiquetas_SUP.clear()

	def eliminar_Una(self, etiqueta):
		#Elimina una entrada según la etiqueta:

		if etiqueta in self.Lista_Etiquetas_SUP:
			del self.Lista_Etiquetas_SUP[etiqueta]

	def obtener_una(self, etiqueta):
		#Devuelve la ruta, si existe, de una etiqueta. Devuelve None si no existe
		return self.Lista_Etiquetas_SUP.get(etiqueta)

	def obtener_todas(self):
		#Devuelve todo el contenido del diccionari (copia)
		#Esta copia no afecta el contenido original.
		#Mantiene la misma estructura del original
		return dict(self.Lista_Etiquetas_SUP)

	def Ver_Content(self, etiqueta):
		#Revisa si la etiqueta está dentro del diccionario.
		return etiqueta in self.Lista_Etiquetas_SUP

