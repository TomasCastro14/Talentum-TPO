from pymongo import MongoClient
from neo4j import GraphDatabase
import redis

try:
    mongo_user = "admin"
    mongo_pass = "password123"
    uri = f"mongodb://{mongo_user}:{mongo_pass}@localhost:27017/"
    client = MongoClient(uri, serverSelectionTimeoutMS=3000)
    print("[+] Mongo OK -> Databases:", client.list_database_names())
except Exception as e:
    print("[!] Error conectando a MongoDB:", e)

try:
    neo_user = "neo4j"
    neo_pass = "password"
    uri = "bolt://localhost:7687"
    neo4j_driver = GraphDatabase.driver(uri, auth=(neo_user, neo_pass))
    with neo4j_driver.session() as session:
        res = session.run("RETURN 1 AS result")
        print("[+] Neo4J OK ->", res.single()["result"])
except Exception as e:
    print("[!] Error conectando a Neo4J:", e)

try:
    r = redis.Redis(host='localhost', port=6379, db=0)
    print("[+] Redis OK -> Ping:", r.ping())
except Exception as e:
    print("[!] Error conectando a Redis:", e)