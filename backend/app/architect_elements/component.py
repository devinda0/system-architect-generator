

from app.architect_elements import Relationship
from app.architect_elements import ArchitectureElement


class Component(ArchitectureElement):
    def __init__(self, name: str, description: str, relationships: list[Relationship] = [], technologies: list[str] = [], childrens: list[ArchitectureElement] = []):
        super().__init__(name, description, relationships)
        self.technologies = technologies
        self.childrens = childrens

    def add_child(self, child: ArchitectureElement) -> None:
        self.childrens.append(child)

    def remove_child(self, child: ArchitectureElement) -> None:
        self.childrens.remove(child)

    def get_childrens(self) -> list[ArchitectureElement]:
        return self.childrens

    def change_technologies(self, technologies: list[str]) -> None:
        self.technologies = technologies

    def get_technologies(self) -> list[str]:
        return self.technologies
    
    def toJSON(self) -> dict:
        base_json = super().toJSON()
        base_json.update({
            "technologies": self.technologies,
            "childrens": [child.toJSON() for child in self.childrens],
        })
        return base_json