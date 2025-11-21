from neo4j import GraphDatabase

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