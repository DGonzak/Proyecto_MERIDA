from sqlalchemy import Column, Integer, String, Numeric, DateTime, Boolean
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base


Base = declarative_base()

class BD_Tags_General(Base):

	__tablename__ = "Base de Datos: TAGS General"

	ID = Column(Integer(), primary_key=True, autoincrement=True)

	Nombre_etiqueta = Column(String(50), nullable=False, unique=True )
	Ruta_carpeta = Column(String(200), nullable=False)

class BD_Comb_Teclas(Base):
	__tablename__ = "Base de Datos: COMBINACIÓN TECLAS"

	ID = Column(Integer(), primary_key=True, autoincrement=True)

	nombre_CombTeclas = Column(String(60), nullable=False, unique=True)
	Comb_Teclas = Column(String(60), nullable=False, unique=True)
	Desc_acción = Column(String(200), nullable=False)

class BD_Recient_Arch(Base):

	__tablename__ = "Base de Datos: ARCHIVOS RECIENTES"

	ID = Column(Integer(), primary_key=True, autoincrement=True)

	RA_Nombre_Etiqueta = Column(String(50), nullable=False, unique=True)
	RA_Ruta_Carpeta = Column(String(200), nullable=False)
	Fecha_de_Registro = Column(DateTime, default=datetime.utcnow)
	Fecha_de_Modificación = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BDInformadora(Base):

    __tablename__ = "bd_informadora"

    id = Column(Integer, primary_key=True, autoincrement=True)

    nombre = Column(
    	String(80),
    	nullable=False,
    	unique=True,
    	doc="Nombre único de la base de datos (identificador interno).")
    
    descripcion = Column(
    	String(250),
    	nullable=True,
    	doc="Descripción del propósito de la base de datos.")
    
    estado = Column(
    	Boolean,
    	default=True,
        doc="Indica si la base está activa y en uso.")
    
    tipo = Column(
    	String(30),
    	nullable=False,
    	default="SQLite",
    	doc="Tipo de base de datos: SQLite, PostgreSQL, etc.")
    
    origen = Column(
    	String(30),
    	nullable=False,
    	default="sistema",
        doc="Origen de la base de datos: sistema, usuario, externa, extensión.")
    
    permisos = Column(
    	String(30),
    	nullable=False,
    	default="lectura/escritura",
    	doc="Permisos: lectura, lectura/escritura, bloqueada, solo interna.")

    """
    La hora de la primera actualización y ultima actulización funciona mediante hora
    UTC. Para cualquier presentación visual, se necesita CONVERTIR la hora utc a 
    hora local, o de lo contrario podría presentarse un desfase. 
    """
    primera_actualizacion = Column(
    	DateTime,
    	default=datetime.utcnow,
    	doc="Fecha de creación del registro.")
    
    ultima_actualizacion = Column(
    	DateTime, default=datetime.utcnow,
    	onupdate=datetime.utcnow,
    	doc="Última vez que se modificó el registro.")

    ubicacion = Column(
    	String(250),
    	nullable=False,
    	doc="Ruta física o virtual del archivo de la base de datos.")

    ubicacion_respaldo = Column(
    	String(250),
    	nullable=False,
    	doc="Ruta fisica o vitual destinada para resguardar el respaldo (backup)")
	
class BD_Moduls(Base):

	__tablename__ = "Base de Datos: MODULOS"

	ID = Column(Integer(), primary_key=True, autoincrement=True)

	Nombre_Modulo = Column(
		String(60),
		nullable=False,
		unique=True)

	Identificador_Modulo = Column(
		String(60),
		nullable=False,
		unique=True)

	Version_Modulo = Column(
		String(20),
		nullable=False)

	Autor_Modulo = Column(
		String(100),
		nullable=False)

	CorreoElectronico_Autor = Column(
		String(100),
		nullable=False)
	
	Descripcion_Modulo = Column(
		String(200),
		nullable=False)
	
	Arch_Principal_Ejecucion = Column(
		String(100),
		nullable=False)
	
	Arch_Icono_Ubicacion = Column(
		String(200),
		nullable=False)

	Recursos_Adicionales = Column(
		String(200),
		nullable=True)
	
	Dependencias_Especiales = Column(
		String(200),
		nullable=True)

	Estado_Modulo = Column(
		Boolean,
		nullable=False,
		default=True)
	
	Fecha_Instalacion = Column(
		DateTime,
		default=datetime.utcnow)

	Ubicacion_Modulo = Column(
		String(200),
		nullable=False)	