class NeoController:
    def __init__(self, driver):
        self.driver = driver

    # --- Helper para no repetir código (podés usarlo también en crear_nodo_usuario) ---
    def _run_write(self, query, params=None):
        params = params or {}
        with self.driver.session(database="neo4j") as session:
            return session.run(query, params)

    # ==========================
    #         NODOS
    # ==========================

    def crear_nodo_busqueda(self, busqueda):
        """
        Crea/actualiza el nodo (:Busqueda) usando id_procedimiento como ID lógico.
        """
        data = busqueda.to_dict()  # usa tu método ya definido en el modelo Busqueda :contentReference[oaicite:5]{index=5}

        params = {
            "id_procedimiento": data["id_procedimiento"],
            "titulo": data["titulo"],
            "descripcion": data["descripcion"],
            "fecha_finalizacion": data["fecha_finalizacion"],
            "modalidad_puesto": data["modalidad_puesto"],
            "ubicacion_oficina": data["ubicacion_oficina"],
            "rubro": data["rubro"],
            "esta_abierta": data["esta_abierta"],
        }

        query = """
        MERGE (b:Busqueda {id_procedimiento: $id_procedimiento})
        SET b.titulo = $titulo,
            b.descripcion = $descripcion,
            b.fecha_finalizacion = $fecha_finalizacion,
            b.modalidad_puesto = $modalidad_puesto,
            b.ubicacion_oficina = $ubicacion_oficina,
            b.rubro = $rubro,
            b.esta_abierta = $esta_abierta
        """

        try:
            self._run_write(query, params)
            print(f"[+] Nodo Busqueda creado/actualizado en Neo4j ({data['id_procedimiento']})")
        except Exception as e:
            print(f"[!] Error al crear nodo Busqueda en Neo4j: {e}")

    def crear_nodo_entrevista(self, entrevista_dict):
        """
        Recibe el dict de Entrevista (entrevista.to_dict()) y crea/actualiza (:Entrevista).
        
        """
        params = {
            "id_entrevista": entrevista_dict["id_entrevista"],
            "fecha_entrevista": entrevista_dict["fecha_entrevista"],
            "tipo": entrevista_dict["tipo"],  # 'presencial' / 'virtual'
        }

        query = """
        MERGE (e:Entrevista {id_entrevista: $id_entrevista})
        SET e.fecha_entrevista = $fecha_entrevista,
            e.tipo = $tipo
        """

        try:
            self._run_write(query, params)
            print(f"[+] Nodo Entrevista creado/actualizado en Neo4j ({params['id_entrevista']})")
        except Exception as e:
            print(f"[!] Error al crear nodo Entrevista en Neo4j: {e}")

    # ==========================
    #     RELACIONES BUSQUEDA
    # ==========================

    def relacionar_busqueda_completa(self, busqueda):
        """
        Crea TODAS las relaciones de una búsqueda:
        - (Empresa)-[:PUBLICA_BUSQUEDA]->(Busqueda)
        - (Reclutador:Usuario)-[:ES_RECLUTADOR_DE]->(Busqueda)
        - (Usuario)-[:POSTULO_A]->(Busqueda) para cada postulante
        - (Busqueda)-[:REQUIERE_SKILL]->(Skill) para cada aptitud
        :contentReference[oaicite:7]{index=7}
        """
        data = busqueda.to_dict()

        # 1) Empresa publica la búsqueda
        if data["empresa"]:
            query_emp = """
            MATCH (b:Busqueda {id_procedimiento: $id_procedimiento})
            MATCH (e:Empresa {matricula: $empresa})
            MERGE (e)-[:PUBLICA_BUSQUEDA]->(b)
            """
            params_emp = {
                "id_procedimiento": data["id_procedimiento"],
                "empresa": data["empresa"],  # asumo que es la matrícula de Empresa
            }
            self._run_write(query_emp, params_emp)

        # 2) Reclutador de la búsqueda
        if data["reclutador"]:
            query_rec = """
            MATCH (b:Busqueda {id_procedimiento: $id_procedimiento})
            MATCH (u:Usuario {email: $reclutador})
            MERGE (u)-[:ES_RECLUTADOR_DE]->(b)
            """
            params_rec = {
                "id_procedimiento": data["id_procedimiento"],
                "reclutador": data["reclutador"],
            }
            self._run_write(query_rec, params_rec)

        # 3) Usuarios postulados a la búsqueda
        if data["usuarios"]:
            query_post = """
            UNWIND $usuarios AS email
            MATCH (b:Busqueda {id_procedimiento: $id_procedimiento})
            MATCH (u:Usuario {email: email})
            MERGE (u)-[:POSTULO_A]->(b)
            """
            params_post = {
                "id_procedimiento": data["id_procedimiento"],
                "usuarios": data["usuarios"],
            }
            self._run_write(query_post, params_post)

        # 4) Aptitudes requeridas por la búsqueda
        if data["aptitudes"]:
            query_apt = """
            UNWIND $aptitudes AS apt
            MATCH (b:Busqueda {id_procedimiento: $id_procedimiento})
            MERGE (s:Skill {nombre: apt})
            MERGE (b)-[:REQUIERE_SKILL]->(s)
            """
            params_apt = {
                "id_procedimiento": data["id_procedimiento"],
                "aptitudes": data["aptitudes"],
            }
            self._run_write(query_apt, params_apt)

        print(f"[+] Relaciones de Busqueda creadas/actualizadas ({data['id_procedimiento']})")

    # ==========================
    #     RELACIONES ENTREVISTA
    # ==========================

    def relacionar_entrevista_con_busqueda_y_usuarios(
        self,
        id_entrevista,
        id_busqueda,
        entrevistador,
        entrevistado,
    ):
        """
        Crea:
        (reclutador:Usuario)-[:REALIZA_ENTREVISTA]->(ent:Entrevista)
        (candidato:Usuario)-[:ES_ENTREVISTADO_EN]->(ent)
        (ent)-[:SOBRE_BUSQUEDA]->(b:Busqueda)
        Donde:
          - id_busqueda = Busqueda.id_procedimiento
          - entrevistador / entrevistado = email de Usuario (asumido)
        
        """
        query = """
        MATCH (ent:Entrevista {id_entrevista: $id_entrevista})
        MATCH (b:Busqueda {id_procedimiento: $id_busqueda})
        MATCH (rec:Usuario {email: $entrevistador})
        MATCH (cand:Usuario {email: $entrevistado})

        MERGE (rec)-[:REALIZA_ENTREVISTA]->(ent)
        MERGE (cand)-[:ES_ENTREVISTADO_EN]->(ent)
        MERGE (ent)-[:SOBRE_BUSQUEDA]->(b)
        """
        params = {
            "id_entrevista": id_entrevista,
            "id_busqueda": id_busqueda,
            "entrevistador": entrevistador,
            "entrevistado": entrevistado,
        }

        try:
            self._run_write(query, params)
            print(f"[+] Relaciones de Entrevista creadas para {id_entrevista}")
        except Exception as e:
            print(f"[!] Error al crear relaciones de Entrevista en Neo4j: {e}")

    def actualizar_fecha_entrevista(self, id_entrevista, nueva_fecha_iso):
        """
        Actualiza solo la propiedad fecha_entrevista del nodo (:Entrevista).
        """
        query = """
        MATCH (ent:Entrevista {id_entrevista: $id_entrevista})
        SET ent.fecha_entrevista = $nueva_fecha
        """
        params = {
            "id_entrevista": id_entrevista,
            "nueva_fecha": nueva_fecha_iso,
        }

        try:
            self._run_write(query, params)
            print(f"[+] Fecha de Entrevista actualizada en Neo4j ({id_entrevista})")
        except Exception as e:
            print(f"[!] Error al actualizar fecha de Entrevista en Neo4j: {e}")

    def actualizar_entrevistador_entrevista(self, id_entrevista, nuevo_entrevistador):
        """
        Cambia el entrevistador:
         - borra la relación REALIZA_ENTREVISTA anterior (si existe)
         - crea la nueva relación desde el nuevo reclutador
        """
        query = """
        // Borramos relación anterior (si la hay)
        MATCH (ent:Entrevista {id_entrevista: $id_entrevista})
        OPTIONAL MATCH (oldRec:Usuario)-[rel:REALIZA_ENTREVISTA]->(ent)
        DELETE rel

        // Creamos nueva relación con el nuevo entrevistador
        WITH ent
        MATCH (newRec:Usuario {email: $nuevo_entrevistador})
        MERGE (newRec)-[:REALIZA_ENTREVISTA]->(ent)
        """
        params = {
            "id_entrevista": id_entrevista,
            "nuevo_entrevistador": nuevo_entrevistador,
        }

        try:
            self._run_write(query, params)
            print(f"[+] Entrevistador actualizado en Neo4j ({id_entrevista})")
        except Exception as e:
            print(f"[!] Error al actualizar entrevistador en Neo4j: {e}")