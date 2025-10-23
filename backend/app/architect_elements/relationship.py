
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.architect_elements.architecture_element import ArchitectureElement


class Relationship:
    """
    Represents a relationship between two architecture elements in the C4 model.

    Attributes:
        source: The source architecture element (can be None for external dependencies).
        target: The target architecture element.
        description: Description of the relationship.
    """

    def __init__(
        self,
        source: "ArchitectureElement | None",
        target: "ArchitectureElement",
        description: str,
    ) -> None:
        """
        Initialize a Relationship.

        Args:
            source: The source ArchitectureElement or None for external relationships.
            target: The target ArchitectureElement.
            description: Description of what this relationship represents.
        """
        self.source: "ArchitectureElement | None" = source
        self.target: "ArchitectureElement" = target
        self.description: str = description

    def __repr__(self) -> str:
        """
        Return string representation of Relationship.

        Returns:
            String showing source, description, and target in arrow format.
        """
        return f"Relationship({self.source} --{self.description}--> {self.target})"

    def toJSON(self) -> dict[str, Any]:
        """
        Convert Relationship to JSON-compatible dictionary.

        Returns:
            Dictionary containing source name (or None), target name, and description.
        """
        return {
            "source": self.source.name if self.source else None,
            "target": self.target.name,
            "description": self.description,
        }