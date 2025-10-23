
from typing import TYPE_CHECKING, Any, List

from app.architect_elements.architecture_element import ArchitectureElement

if TYPE_CHECKING:
    from app.architect_elements.relationship import Relationship


class Code(ArchitectureElement):
    """
    Represents code-level architecture element in the C4 model.

    Code elements typically represent classes, functions, or other code artifacts.
    """

    def __init__(
        self,
        name: str,
        description: str,
        relationships: List["Relationship"] | None = None,
    ) -> None:
        """
        Initialize a Code element.

        Args:
            name: The name of the code element (e.g., class name, module name).
            description: Description of what this code element does.
            relationships: Optional list of Relationship objects.
        """
        if relationships is None:
            relationships = []
        super().__init__(name, description, relationships)

    def toJSON(self) -> dict[str, Any]:
        """
        Convert Code element to JSON-compatible dictionary.

        Returns:
            Dictionary with all base class properties.
        """
        base_json: dict[str, Any] = super().toJSON()
        return base_json