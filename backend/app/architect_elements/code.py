
from app.architect_elements import Relationship
from app.architect_elements import ArchitectureElement

class Code(ArchitectureElement):
    def __init__(self, name: str, description: str, relationships: list[Relationship] = [], ):
        super().__init__(name, description, relationships)

    def toJSON(self) -> dict:
        base_json = super().toJSON()
        return base_json
    
