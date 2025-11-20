class Empresa:
    def __init__(self, nombre: str, anio_fundacion: str, matricula: str):
        self.nombre = nombre
        self.anio_fundacion = anio_fundacion
        self.matricula = matricula

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "anio_fundacion": self.anio_fundacion,
            "matricula": self.matricula
        }
    
    def __str__(self):
        return f"Empresa: {self.nombre}, Año de Fundación: {self.anio_fundacion}, Matrícula: {self.matricula}"