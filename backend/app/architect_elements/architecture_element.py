from abc import ABC
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.architect_elements.relationship import Relationship


class ArchitectureElement(ABC):
    def __init__(
        self,
        name: str,
        description: str,
        relationships: list["Relationship"] | None = None,
    ) -> None:
        """
        Initialize an ArchitectureElement.

        Args:
            name: The name of the architecture element.
            description: The description of the architecture element.
            relationships: Optional list of Relationship objects associated with this element.
        """
        self.name: str = name
        self.description: str = description
        self.relationships: list["Relationship"] = relationships if relationships is not None else []

    def __repr__(self) -> str:
        """
        Return string representation of ArchitectureElement.

        Returns:
            String representation with name, description, and relationships.
        """
        return f"ArchitectureElement(name={self.name}, description={self.description}, relationships={self.relationships})"

    def toJSON(self) -> dict[str, Any]:
        """
        Convert ArchitectureElement to JSON-compatible dictionary.

        Returns:
            Dictionary containing name, description, and serialized relationships.
        """
        return {
            "name": self.name,
            "description": self.description,
            "relationships": [rel.toJSON() for rel in self.relationships],
        }

    def add_relationship(self, relationship: "Relationship") -> None:
        """
        Add a relationship to this architecture element.

        Args:
            relationship: The Relationship object to add.
        """
        self.relationships.append(relationship)

    def remove_relationship(self, relationship: "Relationship") -> None:
        """
        Remove a relationship from this architecture element.

        Args:
            relationship: The Relationship object to remove.

        Raises:
            ValueError: If relationship is not found in the element's relationships.
        """
        self.relationships.remove(relationship)

    def get_relationships(self) -> list["Relationship"]:
        """
        Get all relationships associated with this element.

        Returns:
            List of Relationship objects.
        """
        return self.relationships
    

