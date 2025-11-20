"""
    Hay que meter acá el tema de crear nodos, que no lo haga más UserController, pq es meterse en temas de BD y eso está mal.
"""

class NeoController:
    
    def __init__(self, driver):
        self.driver = driver

    def crear_nodo_usuario(self, usuario):
        with self.driver.session(database="neo4j") as session:
            try:
                session.run("""
                    CREATE (u:Usuario {
                        nombre: $nombre,
                        apellido: $apellido,
                        email: $email,
                        dni: $dni,
                        genero: $genero,
                        fecha_nacimiento: $fecha_nacimiento,
                        edad: $edad,
                        activo: $activo,
                        tipo_usuario: $tipo_usuario
                    })
                """, usuario.to_neo4j_node())
                print(f"[+] Nodo de usuario creado en Neo4J para {usuario.email}")
            except Exception as e:
                print(f"[!] Error al crear nodo de usuario en Neo4J: {e}")

    def actualizar_usuario(self, email, campos: dict):
        """
        Actualiza CUALQUIERA de los campos de un usuario en Neo4J dado su email.
        """
        
        # Creamos el set de cypher
        set_clause = ", ".join([f"u.{key} = ${key}" for key in campos.keys()])

        # Agregamos el email a los parámetros
        params = {"email": email}
        params.update(campos)
        query = f"""
            MATCH (u:Usuario {{email: $email}})
            SET {set_clause}
        """

        try:
            with self.driver.session(database="neo4j") as session:
                session.run(query, params)
            print(f"[+] Usuario {email} actualizado en Neo4J.")
        except Exception as e:
            print(f"[!] Error al actualizar usuario en Neo4J: {e}")