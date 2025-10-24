# Talentum-TPO
## 1. Preparación de VSCode
### 1.1 Extensiones de Visual Studio Code
1. Python
2. Docker
3. MongoDB for VSCode
4. Neo4J VSCode Extension
5. REST Client

### 1.2 Instalación del Entorno Virtual
1. En la consola de VSCode ejecutá
```
  python -m venv venv
  venv\Scripts\activate
```
2. Creá el archivo `requeriments.txt`
```
  pymongo
  neo4j
  redis
  python-dotenv
```
3. Ejecutar desde la consola de VSCode
```
  pip install -r requirements.txt
```
## 2. Conexiones con las BDD
1. Verificar que las bdd están bien configuradas
  - [Config MongoDB](talentum-plus/BDD Congif/MongoDB.txt)
  - [Config Neo4J](talentum-plus/BDD Congif/Neo4J.txt)
3. Ejecutar test de conexiones
  - [Test de conexión](talentum-plus/src/config/test_database_conection.py)
