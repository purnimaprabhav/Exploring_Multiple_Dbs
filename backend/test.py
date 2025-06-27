from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Retrieve credentials
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# Optional debug print
print("Connecting to:", NEO4J_URI)

# Initialize the driver
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# Function to run a test query
def test_connection():
    try:
        with driver.session() as session:
            result = session.run("RETURN 'Connected to Neo4j Aura' AS message")
            message = result.single()["message"]
            print("✅", message)
    except Exception as e:
        print("❌ Connection failed:", e)
    finally:
        driver.close()

# Run the test
if __name__ == "__main__":
    test_connection()
