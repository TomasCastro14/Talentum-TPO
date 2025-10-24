# Talentum-TPO
## ⚙️ 2. Información del Proyecto

- **Lenguaje:** Python 3.11  
- **Entorno:** Visual Studio Code  
- **Bases de Datos NoSQL:**  
  - MongoDB → para perfiles, ofertas y cursos  
  - Neo4J → para relaciones y recomendaciones  
  - Redis → para cache y sesiones  
- **Virtualización:** Docker y Docker Compose

## 🧩 1. Preparación de VSCode
### 1.1 Extensiones necesarias

1. Python (Microsoft)  
2. Docker  
3. MongoDB for VSCode  
4. Neo4J VSCode Extension  
5. REST Client *(opcional para testear endpoints)*  

### 1.2 Instalación del Entorno Virtual

- **Paso 1.** Ejecutá desde la consola de VSCode para crear la carpeta de las dependencias. `[ctrl + ñ]`
```
  python -m venv venv
  venv\Scripts\activate
```

- **Paso 2.** Creá el archivo `requeriments.txt`
  - [requeriments.txt](talentum-plus/requeriments.txt)

- **Paso 3.** Ejecutá desde la consola de VSCode para instalar las dependencias.
```
  pip install -r requirements.txt
```

## 🔗 2. Conexiones con las BDD
### 1.1 Verificar que las BDD estén bien configuradas en Docker

- **Paso 1.** Verificar que las bdd están bien configuradas
  - [Config MongoDB](talentum-plus/BDD%20Congif/MongoDB.txt)
  - [Config Neo4J](talentum-plus/BDD%20Congif/Neo4J.txt)
  
- **Paso 2.** Ejecutar test de conexiones
  - [Test de conexión](talentum-plus/src/config/test_database_conection.py)
    
## 🖥️ 3. Ejecución del Proyecto

- **Paso 1.** En el [main](talentum-plus/src/main.py) escribí los usuarios que quieras agregar utilizando la función `crear_candidato()`
  - En **MongoDB Express** debería aparecer la base de datos *talentum-db*
