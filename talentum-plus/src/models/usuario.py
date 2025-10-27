from enums.genero_enum import GeneroEnum
from enums.estado_cuenta_enum import EstadoCuentaEnum
from enums.tipo_usuario_enum import TipoUsuarioEnum
from datetime import date

class Usuario:
    def __init__(self, nombre, apellido, email, dni, genero, fecha_nacimiento,  
                 tipo_usuario, experiencia=None, historial_laboral=None, historial_entrevistas=None, relaciones=None):
        
        # --- Datos Físicos ---
        self.nombre = nombre
        self.apellido = apellido
        self.email = email
        self.dni = dni
        self.genero = genero
        self.fecha_nacimiento = fecha_nacimiento
        
        # --- Datos del Sistema ---
        self.activo = EstadoCuentaEnum.ACTIVO
        self.tipo_usuario = tipo_usuario
        
        # --- Relaciones ---
        self.experiencia = experiencia if experiencia is not None else []
        self.historial_laboral = historial_laboral if historial_laboral is not None else []
        self.historial_entrevistas = historial_entrevistas if historial_entrevistas is not None else []
        self.relaciones = relaciones if relaciones is not None else []

    def edad(self):
        """Devuelve la edad actual del usuario."""
        hoy = date.today()
        return hoy.year - self.fecha_nacimiento.year - (
            (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )

    def to_dict(self):
        """Convierte el objeto en un diccionario para guardarlo o exportarlo."""
        return {
            "nombre": self.nombre,
            "apellido": self.apellido,
            "email": self.email,
            "dni": self.dni,
            "genero": self.genero.value,
            "fecha_nacimiento": self.fecha_nacimiento.isoformat(),
            "edad": self.edad(),
            "activo": self.activo.value,
            "tipo_usuario": self.tipo_usuario.name,
            "experiencia": self.experiencia,
            "historial_laboral": self.historial_laboral,
            "historial_entrevistas": self.historial_entrevistas,
            "relaciones": self.relaciones
        }

    def __str__(self):
        """Representación legible del usuario."""
        return f"{self.nombre} {self.apellido} ({self.tipo_usuario.name}) - Estado: {self.activo.value}"