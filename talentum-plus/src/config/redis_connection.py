import redis

try:
    r = redis.Redis(host='localhost', port=6379, db=0)
    print("[+] Redis OK -> Ping:", r.ping())
except Exception as e:
    print("[!] Error conectando a Redis:", e)