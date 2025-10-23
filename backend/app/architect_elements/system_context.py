
from app.architect_elements import ArchitectureElement


class SystemContext(ArchitectureElement):
    def __init__(self, name: str, description: str, childrens: list[ArchitectureElement] = []):
        super().__init__(name, description)
        self.childrens = childrens

    def add_child(self, child: ArchitectureElement) -> None:
        self.childrens.append(child)

    def remove_child(self, child: ArchitectureElement) -> None:
        self.childrens.remove(child)

    def get_childrens(self) -> list[ArchitectureElement]:
        return self.childrens
    
    def toJSON(self) -> dict:
        base_json = super().toJSON()
        base_json.update({
            "childrens": [child.toJSON() for child in self.childrens],
        })
        return base_json