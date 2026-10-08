import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv()


class Neo4jClient:

    def __init__(self):

        uri = os.getenv("NEO4J_URI")
        username = os.getenv(
            "NEO4J_USERNAME"
        )
        password = os.getenv(
            "NEO4J_PASSWORD"
        )

        if not all([
            uri,
            username,
            password
        ]):
            raise ValueError(
                "Neo4j credentials missing from .env"
            )

        self.driver = GraphDatabase.driver(
            uri,
            auth=(
                username,
                password
            )
        )

    def verify_connection(self):
        self.driver.verify_connectivity()

    def close(self):
        self.driver.close()