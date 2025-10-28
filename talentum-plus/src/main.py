from config.database_conection import DatabaseConnections
from controllers.user_controller import UserController

def cargar_modulos():
    print("Iniciando Talentum Plus...\n")
    
    print("[+] Creando objetos...\n")
    database_connections = DatabaseConnections()
    user_controller = UserController()

    print("[0/3] Cargando módulos...")
    mongodb = database_connections.mongo_connection()
    neo4jdb = database_connections.neo4j_connection()
    redisdb = database_connections.redis_connection()

    print()
    return mongodb, neo4jdb, redisdb, user_controller

def mostrar_menu():
    print("\n\n=== Menú de Talentum Plus ===")
    print("[1] Menú Usuarios")
    print("[2] null")
    print("[3] null")
    print("[0] Salir")
    print("=============================")
    print()

def pausar():
    input("\nPresione ENTER para continuar...")

def start_application():

    mongodb, neo4jdb, redisdb, user_controller = cargar_modulos()

    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ")

        if opcion == "0":
            print("\nSaliendo del sistema... ¡Hasta luego!\n")
            break

        elif opcion == "1":
            print("Opcion 1 - Modificar Usuarios\n")
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
                    UserController.crear_usuario_input(mongodb)
                case "2":
                    print("\n[TODO] Buscar por mail")
                case "3":
                    UserController.cambiar_estado_cuenta(mongodb)
                case "4":
                    UserController.cambiar_nombre_usuario(mongodb)
                case "5":
                    UserController.cambiar_apellido_usuario(mongodb)
                case "6":
                    UserController.cambiar_genero_usuario(mongodb)
                case "7":
                    UserController.cambiar_tipo_usuario(mongodb)
                case _:
                    print("\n[*] Volviendo al menú principal.")

        elif opcion == "2":
            print("Opcion 2 - Eliminar Usuario\n")
            

        elif opcion == "3":
            print("Opcion 3")

        else:
            print("\n[!] Opción inválida. Intente nuevamente.\n")

        pausar()

if __name__ == "__main__":
    start_application()

