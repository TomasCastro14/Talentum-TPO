from datetime import date, datetime

class NeoController:
    
    def __init__(self, driver):
        self.driver = driver

    def crear_nodo(self, obj):
        """
        Crea un nodo en Neo4J según el tipo de objeto.
        """
        label = type(obj).neo_label
        data = obj.to_neo4j_node()

        #Construimos dinámicamente los parámetros y la query
        props = ", ".join([f"{key}: ${key}" for key in data.keys()])

        query = f"""CREATE (n:{label} {{{props}}})"""

        try:
            with self.driver.session(database="neo4j") as session:
                session.run(query, data)
            print(f"[+] Nodo de {label} creado en Neo4J.")
        except Exception as e:
            print(f"[!] Error al crear nodo de {label} en Neo4J: {e}")

    def actualizar_nodo(self, label: str, email: str, campos: dict):
        """
        Actualiza CUALQUIERA de los campos de un nodo en Neo4J dado su email.
        """
        set_clause = ", ".join([f"n.{key} = ${key}" for key in campos.keys()])

        params = {"email": email}
        params.update(campos)
        query = f"""
            MATCH (n:{label} {{email: $email}})
            SET {set_clause}
        """

        try:
            with self.driver.session(database="neo4j") as session:
                session.run(query, params)
            print(f"[+] Nodo {label} con email {email} actualizado en Neo4J.")
        except Exception as e:
            print(f"[!] Error al actualizar nodo {label} en Neo4J: {e}")

    def crear_relacion(self, obj_origen, obj_destino_label, obj_destino_key, obj_destino_value, relacion):

        """
        Crea una relación en Neo4J:
        (obj_destino)-[:RELACION]->(obj_origen)
        """
        
        origen_label = type(obj_origen).neo_label
        origen_key = obj_origen.get_neo4j_key()
        origen_value = getattr(obj_origen, origen_key)

        query = f"""
        MATCH (a:{origen_label} {{{origen_key}: $origen_value}})
        MATCH (b:{obj_destino_label} {{{obj_destino_key}: $destino_value}})
        MERGE (b)-[:{relacion}]->(a)
        """

        try:
            with self.driver.session(database="neo4j") as session:
                session.run(query, {
                    "origen_value": origen_value,
                    "destino_value": obj_destino_value
                })
            print(f"[+] Relación ({obj_destino_label})-[:{relacion}]->({origen_label}) creada correctamente")
        except Exception as e:
            print(f"[!] Error creando relación: {e}")

    def obtener_relaciones(self, label_origen, key_origen, value_origen, tipo_relacion, label_destino=None):
        try:
            with self.driver.session(database="neo4j") as session:
                query = f"""
                    MATCH (o:{label_origen} {{{key_origen}: $value_origen}})-[r:{tipo_relacion}]->(d)
                    RETURN d, r
                """
                if label_destino:
                    query = f"""
                        MATCH (o:{label_origen} {{{key_origen}: $value_origen}})-[r:{tipo_relacion}]->(d:{label_destino})
                        RETURN d, r
                    """
                result = session.run(query, {"value_origen": value_origen})

                relaciones = []

                for record in result:
                    nodo = record["d"]
                    relacion = record["r"]

                    relaciones.append({
                        "nodo": dict(nodo),
                        "relacion": relacion.type
                    })

                return relaciones
        except Exception as e:
            print(f"[!] Error obteniendo relaciones en Neo4J: {e}")
            return []
        
    def buscar_nodos_por_campo(
        self,
        label: str,
        campo: str,
        valor,
        operador: str = "=",
        max_results: int = 100
    ):
        """
        Busca nodos de un label dado según el campo y el valor.
        Se puede usar cualquier operador Cypher: =, CONTAINS, STARTS WITH, etc.
        Devuelve una lista de nodos como diccionarios.
        """
        try:
            with self.driver.session(database="neo4j") as session:
                query = f"""
                    MATCH (n:{label})
                    WHERE n.{campo} {operador} $valor
                    RETURN n
                    LIMIT $max_results
                """
                # Convertimos valor a string si es enum o date
                if hasattr(valor, "value"):  # ejemplo enums
                    valor = valor.value
                elif isinstance(valor, (datetime, date)):
                    valor = str(valor)

                result = session.run(query, {"valor": valor, "max_results": max_results})

                nodos = [dict(record["n"]) for record in result]
                return nodos

        except Exception as e:
            print(f"[!] Error buscando nodos en Neo4J: {e}")
            return []

