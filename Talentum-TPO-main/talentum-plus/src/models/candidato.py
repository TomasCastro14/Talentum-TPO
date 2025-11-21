class Candidato:
    def __init__(self, nombre, apellido, email, skills, experiencia):
        self.nombre = nombre
        self.apellido = apellido
        self.email = email
        self.skills = skills
        self.experiencia = experiencia

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "apellido": self.apellido,
            "email": self.email,
            "skills": self.skills,
            "experiencia": self.experiencia
        }