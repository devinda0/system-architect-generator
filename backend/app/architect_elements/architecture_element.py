from abc import ABC
from app.architect_elements import Relationship


class ArchitectureElement(ABC):
    def __init__(self, name: str, description: str, relationships: list[Relationship] = []):
        self.name = name
        self.description = description
        self.relationships = relationships

    def __repr__(self):
        return f"ArchitectureElement(name={self.name}, description={self.description}, relationships={self.relationships})"
    
    def toJSON(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "relationships": [rel.toJSON() for rel in self.relationships],
        }
    
    def add_relationship(self, relationship: Relationship) -> None:
        self.relationships.append(relationship)

    def remove_relationship(self, relationship: Relationship) -> None:
        self.relationships.remove(relationship)

    def get_relationships(self) -> list[Relationship]:
        return self.relationships
    

