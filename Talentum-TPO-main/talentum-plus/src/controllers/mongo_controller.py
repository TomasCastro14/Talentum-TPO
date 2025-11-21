"""
    Controller de Mongo que hace todo lo de mongo
"""

class MongoController:
    def __init__(self, driver):
        self.driver = driver
        self.collection_map = {
            "Usuario": "usuarios",
            "Empresa": "empresas",
            "Busqueda": "busquedas",
            "Entrevista": "entrevistas"
        }

    def insertar_documento(self, obj):
        class_name = type(obj).__name__

        if class_name not in self.collection_map:
            raise ValueError(f"[!] No existe una colección definida para {class_name}")
        
        collection_name = self.collection_map[class_name]

        try:
            self.driver[collection_name].insert_one(obj.to_dict())
            print(f"[+] MongoDB ok.")
        except Exception as e:
            print(f"[!] Error MongoDB: {e}")

    def buscar_documento_mail(self, obj_class, email):
        collection_name = obj_class.collection_name

        try:
            doc = self.driver[collection_name].find_one({"email": email})

            if doc:
                print(f"[+] Documento encontrado en MongoDB para {email}")
                return doc
            if not doc:
                print(f"[-] No se encontró documento en MongoDB para {email}")
                return None
        except Exception as e:
            print(f"[!] Error al buscar documento en MongoDB: {e}")
            return None
        
    def actualizar_documento(self,collection_name: str, filtro: dict, campos: dict):
        try:
            colection = self.driver[collection_name]
            resultado = colection.update_one(filtro, {"$set": campos})

            if resultado.matched_count == 0:
                print(f"[-] No se encontró ningún documento que coincida con el filtro en MongoDB.")
                return
            print(f"[+] Documento actualizado en MongoDB.")
        except Exception as e:
            print(f"[!] Error al actualizar documento en MongoDB: {e}")
            return False

