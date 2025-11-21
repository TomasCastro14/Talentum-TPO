from config.database_conection import DatabaseConnections
from controllers.user_controller import UserController
from controllers.neo4j_controller import NeoController
from controllers.mongo_controller import MongoController

def cargar_modulos():
    print("Iniciando Talentum Plus...\n")
    
    print("[+] Creando objetos...\n")
    database_connections = DatabaseConnections()
    user_controller = UserController()
    # empresa_controller = EmpresaController()

    print("[0/3] Cargando módulos...")
    mongodb = database_connections.mongo_connection()
    neo4jdb = database_connections.neo4j_connection()
    redisdb = database_connections.redis_connection()

    neo_controller = NeoController(neo4jdb)
    mongo_controller = MongoController(mongodb)

    print()
    return mongo_controller, neo_controller, redisdb, user_controller

def mostrar_menu():
    print("\n\n=== Menú de Talentum Plus ===")
    print("[1] Menú Usuarios")
    print("[2] Menú Empresas")
    print("[3] null")
    print("[0] Salir")
    print("=============================")
    print()

def pausar():
    input("\nPresione ENTER para continuar...")

def start_application():

    mongo_controller, neo_controller, redisdb, user_controller = cargar_modulos()

    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ")

        if opcion == "0":
            print("\nSaliendo del sistema... ¡Hasta luego!\n")
            break

        elif opcion == "1":
            print("Opcion 1 - Usuarios\n")
            print("======== Menú Modificación de Usuarios ========")
            print("[1] Crear nuevo usuario")
            print("[2] Buscar por mail [TODO]")
            print("[3] Cambiar estado de cuenta (Activo/Inactivo)")
            print("[4] Cambiar nombre")
            print("[5] Cambiar apellido")
            print("[6] Cambiar género")
            print("[7] Cambiar tipo")
            print("===============================================\n")
            opcion = input("Seleccione una opción: ")

            match opcion:
                case "1":
                    UserController.crear_usuario_input(mongo_controller, neo_controller)
                case "2":
                    print("\n[TODO] Buscar por mail")
                case "3":
                    UserController.cambiar_estado_cuenta(mongo_controller, neo_controller)
                case "4":
                    UserController.cambiar_nombre_usuario(mongo_controller, neo_controller)
                case "5":
                    UserController.cambiar_apellido_usuario(mongo_controller, neo_controller)
                case "6":
                    UserController.cambiar_genero_usuario(mongo_controller, neo_controller)
                case "7":
                    UserController.cambiar_tipo_usuario(mongo_controller, neo_controller)
                case _:
                    print("\n[*] Volviendo al menú principal.")

        elif opcion == "2":
            print("Opcion 2 - Empresas\n")

        elif opcion == "3":
            print("Opcion 3 - Databases\n")
            print("======== Menú de Databases ========")
            print("[1] Buscar por mail Neo4J")
            print("===============================================\n")
            opcion = input("Seleccione una opción: ")

            match opcion:
                case "1":
                    UserController.buscar_usuario_neo4j(neo4jdb, UserController.email_input())
                case "2":
                    print("\n[TODO] Buscar por mail")
                case "3":
                    print("\n[TODO] Buscar por mail")
                case "4":
                    print("\n[TODO] Buscar por mail")
                case "5":
                    print("\n[TODO] Buscar por mail")
                case "6":
                    print("\n[TODO] Buscar por mail")
                case "7":
                    print("\n[TODO] Buscar por mail")
                case _:
                    print("\n[*] Volviendo al menú principal.")

        else:
            print("\n[!] Opción inválida. Intente nuevamente.\n")

        pausar()

if __name__ == "__main__":
    start_application()

