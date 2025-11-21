from datetime import date

class Busqueda:
    def __init__(
        self,
        id_procedimiento,
        titulo,
        descripcion,
        fecha_finalizacion, 
        modalidad_puesto,    
        ubicacion_oficina,
        rubro,
        empresa,              
        reclutador,           
        aptitudes=None,
        entrevistas=None,
        usuarios=None,
        esta_abierta=True
    ):
        self.id_procedimiento = id_procedimiento
        self.titulo = titulo
        self.descripcion = descripcion
        self.fecha_finalizacion = fecha_finalizacion
        self.modalidad_puesto = modalidad_puesto
        self.ubicacion_oficina = ubicacion_oficina
        self.rubro = rubro

        self.esta_abierta = esta_abierta

        self.empresa = empresa
        self.reclutador = reclutador
        self.aptitudes = aptitudes if aptitudes is not None else []
        self.entrevistas = entrevistas if entrevistas is not None else []
        self.usuarios = usuarios if usuarios is not None else []   

    def cambiar_reclutador(self, nuevo_reclutador):
        """Cambia el reclutador asignado a la búsqueda."""
        self.reclutador = nuevo_reclutador

    def agregar_usuario(self, usuario):
        """
        Agrega un usuario a la búsqueda (postulante).
        Podés guardar el objeto Usuario o solo su ID.
        """
        if usuario not in self.usuarios:
            self.usuarios.append(usuario)

    def asignar_entrevista(self, entrevista):
        """
        Asigna una entrevista a la búsqueda.
        """
        self.entrevistas.append(entrevista)

    def cambiar_fecha_finalizacion(self, nueva_fecha: date):
        """Actualiza la fecha de finalización del procedimiento."""
        self.fecha_finalizacion = nueva_fecha

    def abrir(self):
        """Marca la búsqueda como abierta."""
        self.esta_abierta = True

    def cerrar(self):
        """Marca la búsqueda como cerrada."""
        self.esta_abierta = False


    def to_dict(self):
        """
        Convierte el objeto en un diccionario para guardarlo en Mongo / Neo4j
        o enviarlo por API.
        """
        return {
            "id_procedimiento": self.id_procedimiento,
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "fecha_finalizacion": (
                self.fecha_finalizacion.isoformat()
                if isinstance(self.fecha_finalizacion, date)
                else self.fecha_finalizacion
            ),
            "modalidad_puesto": self.modalidad_puesto,
            "ubicacion_oficina": self.ubicacion_oficina,
            "rubro": self.rubro,
            "aptitudes": self.aptitudes,
            "empresa": self.empresa,
            "reclutador": self.reclutador,
            "entrevistas": self.entrevistas,
            "usuarios": self.usuarios,
            "esta_abierta": self.esta_abierta,
        }

    def __str__(self):
        estado = "Abierta" if self.esta_abierta else "Cerrada"
        return f"[{self.id_procedimiento}] {self.titulo} - {estado}"