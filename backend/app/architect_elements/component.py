from typing import TYPE_CHECKING, Any, List

from app.architect_elements.architecture_element import ArchitectureElement

if TYPE_CHECKING:
    from app.architect_elements.relationship import Relationship


class Component(ArchitectureElement):
    """
    Represents a component in the C4 architecture model.

    Components are groupings of code elements and can contain technologies
    and child elements.
    """

    def __init__(
        self,
        name: str,
        description: str,
        relationships: List["Relationship"] | None = None,
        technologies: List[str] | None = None,
        childrens: List[ArchitectureElement] | None = None,
    ) -> None:
        """
        Initialize a Component.

        Args:
            name: The name of the component.
            description: Description of what this component does.
            relationships: Optional list of Relationship objects.
            technologies: Optional list of technology names used by this component.
            childrens: Optional list of child ArchitectureElement objects.
        """
        if relationships is None:
            relationships = []
        if technologies is None:
            technologies = []
        if childrens is None:
            childrens = []

        super().__init__(name, description, relationships)
        self.technologies: List[str] = technologies
        self.childrens: List[ArchitectureElement] = childrens

    def add_child(self, child: ArchitectureElement) -> None:
        """
        Add a child architecture element to this component.

        Args:
            child: The ArchitectureElement to add as a child.
        """
        self.childrens.append(child)

    def remove_child(self, child: ArchitectureElement) -> None:
        """
        Remove a child architecture element from this component.

        Args:
            child: The ArchitectureElement to remove.

        Raises:
            ValueError: If child is not found in the component's children.
        """
        self.childrens.remove(child)

    def get_childrens(self) -> List[ArchitectureElement]:
        """
        Get all child elements of this component.

        Returns:
            List of child ArchitectureElement objects.
        """
        return self.childrens

    def change_technologies(self, technologies: List[str]) -> None:
        """
        Update the list of technologies used by this component.

        Args:
            technologies: New list of technology names.
        """
        self.technologies = technologies

    def get_technologies(self) -> List[str]:
        """
        Get the list of technologies used by this component.

        Returns:
            List of technology names.
        """
        return self.technologies

    def toJSON(self) -> dict[str, Any]:
        """
        Convert Component to JSON-compatible dictionary.

        Returns:
            Dictionary containing base class properties, technologies, and children.
        """
        base_json: dict[str, Any] = super().toJSON()
        base_json.update({
            "technologies": self.technologies,
            "childrens": [child.toJSON() for child in self.childrens],
        })
        return base_json