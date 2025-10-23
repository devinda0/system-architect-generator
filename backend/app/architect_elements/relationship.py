
from app.architect_elements.architecture_element import ArchitectureElement


class Relationship:
    def __init__(self, source: ArchitectureElement, target: ArchitectureElement, description: str):
        self.source = source
        self.target = target
        self.description = description

    def __repr__(self):
        return f"Relationship({self.source} --{self.description}--> {self.target})"
    
    def toJSON(self) -> dict:
        return {
            "source": self.source.name if self.source else None,
            "target": self.target.name,
            "description": self.description,
        }