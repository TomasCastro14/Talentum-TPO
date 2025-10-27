from pymongo import MongoClient
from neo4j import GraphDatabase
import redis

class DatabaseConnections:
    def mongo_connection(self):
        try:
            mongo_user = "admin"
            mongo_pass = "password123"
            uri = f"mongodb://{mongo_user}:{mongo_pass}@localhost:27017/"

            client = MongoClient(uri, serverSelectionTimeoutMS=3000)
            print("[1/3] Mongo OK -> Databases:", client.list_database_names())

            db = client["talentum_db"]
            return db
        
        except Exception as e:
            print("[!] Error conectando a MongoDB:", e)
            return None

    def neo4j_connection(self):
        try:
            neo_user = "neo4j"
            neo_pass = "password"
            uri = "bolt://localhost:7687"

            neo4j_driver = GraphDatabase.driver(uri, auth=(neo_user, neo_pass))

            with neo4j_driver.session() as session:
                res = session.run("RETURN 1 AS result")
                print("[2/3] Neo4J OK ->", res.single()["result"])
        except Exception as e:
            print("[!] Error conectando a Neo4J:", e)

    def redis_connection(self):
        try:
            r = redis.Redis(host='localhost', port=6379, db=0)
            print("[3/3] Redis OK -> Ping:", r.ping())
        except Exception as e:
            print("[!] Error conectando a Redis:", e)