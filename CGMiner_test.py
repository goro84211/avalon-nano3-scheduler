iimport socket
import json

# Miner IP and CGMiner API port
HOST = '192.168.1.76'
HOST = '192.168.1.162
PORT = 4018

# Function to query the miner API
def query_cgminer(command="summary"):
    payload = json.dumps({"command": command})
    payload += '\n'

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)  # Timeout in seconds
            s.connect((HOST, PORT))
            s.sendall(payload.encode('utf-8'))
            data = s.recv(4096)

        response = data.decode('utf-8').strip('\x00')
        print("Raw Response:", response)

        result = json.loads(response)
        return result

    except Exception as e:
        print(f"Error querying cgminer: {e}")
        return None


# ✅ Test commands:
summary = query_cgminer("summary")
print("Summary:", json.dumps(summary, indent=2))

stats = query_cgminer("stats")
print("Stats:", json.dumps(stats, indent=2))
