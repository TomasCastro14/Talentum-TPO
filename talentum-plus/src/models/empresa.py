class Empresa:
    collection_name = "empresas"
    neo_label = "Empresa"

    def __init__(
        self,
        nombre: str,
        matricula: str,
        email: str,
        descripcion: str,
        rubro: list,
        pais_origen: str,
        fecha_fundacion
    ):
        self.nombre = nombre
        self.matricula = matricula
        self.email = email
        self.descripcion = descripcion
        self.rubro = rubro
        self.pais_origen = pais_origen
        self.fecha_fundacion = fecha_fundacion

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "matricula": self.matricula,
            "email": self.email,
            "descripcion": self.descripcion,
            "rubro": self.rubro,
            "pais_origen": self.pais_origen,
            "fecha_fundacion": str(self.fecha_fundacion)
        }
    
    def to_neo4j_node(self):
        return {
            "nombre": self.nombre,
            "matricula": self.matricula,
            "email": self.email,
            "descripcion": self.descripcion,
            "rubro": self.rubro,
            "pais_origen": self.pais_origen,
            "fecha_fundacion": str(self.fecha_fundacion)
        }
