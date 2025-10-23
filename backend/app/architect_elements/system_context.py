from typing import Any, List

from app.architect_elements.architecture_element import ArchitectureElement


class SystemContext(ArchitectureElement):
    """
    Represents the system context in the C4 architecture model.

    The system context is the highest level in the C4 model hierarchy,
    containing all containers and external systems.
    """

    def __init__(
        self,
        name: str,
        description: str,
        childrens: List[ArchitectureElement] | None = None,
    ) -> None:
        """
        Initialize a SystemContext.

        Args:
            name: The name of the system.
            description: Description of what the system does.
            childrens: Optional list of child ArchitectureElement objects (typically Containers).
        """
        if childrens is None:
            childrens = []

        super().__init__(name, description)
        self.childrens: List[ArchitectureElement] = childrens

    def add_child(self, child: ArchitectureElement) -> None:
        """
        Add a child architecture element to this system context.

        Args:
            child: The ArchitectureElement to add as a child.
        """
        self.childrens.append(child)

    def remove_child(self, child: ArchitectureElement) -> None:
        """
        Remove a child architecture element from this system context.

        Args:
            child: The ArchitectureElement to remove.

        Raises:
            ValueError: If child is not found in the context's children.
        """
        self.childrens.remove(child)

    def get_childrens(self) -> List[ArchitectureElement]:
        """
        Get all child elements of this system context.

        Returns:
            List of child ArchitectureElement objects.
        """
        return self.childrens

    def toJSON(self) -> dict[str, Any]:
        """
        Convert SystemContext to JSON-compatible dictionary.

        Returns:
            Dictionary containing base class properties and children.
        """
        base_json: dict[str, Any] = super().toJSON()
        base_json.update({
            "childrens": [child.toJSON() for child in self.childrens],
        })
        return base_json