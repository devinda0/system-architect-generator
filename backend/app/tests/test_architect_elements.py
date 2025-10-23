"""
Unit tests for Architect Elements module.

Tests for C4 Architecture Model classes including:
- ArchitectureElement (base class)
- Relationship
- Code
- Component
- Container
- SystemContext
"""

import pytest
from typing import List, Dict, Any
from app.architect_elements.architecture_element import ArchitectureElement
from app.architect_elements.relationship import Relationship
from app.architect_elements.code import Code
from app.architect_elements.component import Component
from app.architect_elements.container import Container
from app.architect_elements.system_context import SystemContext


class ConcreteArchitectureElement(ArchitectureElement):
    """Concrete implementation of ArchitectureElement for testing abstract class."""

    def __init__(
        self,
        name: str,
        description: str,
        relationships: List[Relationship] | None = None,
    ) -> None:
        """
        Initialize ConcreteArchitectureElement.

        Args:
            name: The name of the architecture element.
            description: The description of the architecture element.
            relationships: Optional list of relationships for this element.
        """
        if relationships is None:
            relationships = []
        super().__init__(name, description, relationships)


class TestArchitectureElement:
    """Test suite for ArchitectureElement base class."""

    def test_initialization(self) -> None:
        """
        Test basic initialization of ArchitectureElement.

        Verifies that name and description are set correctly.
        """
        element: ArchitectureElement = ConcreteArchitectureElement(
            name="TestElement",
            description="A test element",
        )

        assert element.name == "TestElement"
        assert element.description == "A test element"
        assert element.relationships == []

    def test_initialization_with_relationships(self) -> None:
        """
        Test initialization with existing relationships.

        Verifies that relationships are properly assigned during initialization.
        """
        element1: ArchitectureElement = ConcreteArchitectureElement(
            name="Element1", description="First element"
        )
        element2: ArchitectureElement = ConcreteArchitectureElement(
            name="Element2", description="Second element"
        )

        rel: Relationship = Relationship(
            source=element1, target=element2, description="connects to"
        )
        element1_with_rel: ArchitectureElement = ConcreteArchitectureElement(
            name="Element1",
            description="First element",
            relationships=[rel],
        )

        assert len(element1_with_rel.relationships) == 1
        assert element1_with_rel.relationships[0] == rel

    def test_add_relationship(self) -> None:
        """
        Test adding a relationship to an element.

        Verifies that relationships are properly appended to the element.
        """
        element1: ArchitectureElement = ConcreteArchitectureElement(
            name="Element1", description="First element"
        )
        element2: ArchitectureElement = ConcreteArchitectureElement(
            name="Element2", description="Second element"
        )

        rel: Relationship = Relationship(
            source=element1, target=element2, description="uses"
        )
        element1.add_relationship(rel)

        assert len(element1.relationships) == 1
        assert element1.relationships[0] == rel

    def test_add_multiple_relationships(self) -> None:
        """
        Test adding multiple relationships to an element.

        Verifies that multiple relationships can be added sequentially.
        """
        element1: ArchitectureElement = ConcreteArchitectureElement(
            name="Element1", description="First element"
        )
        element2: ArchitectureElement = ConcreteArchitectureElement(
            name="Element2", description="Second element"
        )
        element3: ArchitectureElement = ConcreteArchitectureElement(
            name="Element3", description="Third element"
        )

        rel1: Relationship = Relationship(
            source=element1, target=element2, description="uses"
        )
        rel2: Relationship = Relationship(
            source=element1, target=element3, description="depends on"
        )

        element1.add_relationship(rel1)
        element1.add_relationship(rel2)

        assert len(element1.relationships) == 2
        assert element1.relationships[0] == rel1
        assert element1.relationships[1] == rel2

    def test_remove_relationship(self) -> None:
        """
        Test removing a relationship from an element.

        Verifies that relationships can be successfully removed.
        """
        element1: ArchitectureElement = ConcreteArchitectureElement(
            name="Element1", description="First element"
        )
        element2: ArchitectureElement = ConcreteArchitectureElement(
            name="Element2", description="Second element"
        )

        rel: Relationship = Relationship(
            source=element1, target=element2, description="uses"
        )
        element1.add_relationship(rel)
        assert len(element1.relationships) == 1

        element1.remove_relationship(rel)
        assert len(element1.relationships) == 0

    def test_remove_relationship_not_found(self) -> None:
        """
        Test removing a relationship that doesn't exist.

        Verifies that ValueError is raised when trying to remove non-existent relationship.
        """
        element1: ArchitectureElement = ConcreteArchitectureElement(
            name="Element1", description="First element"
        )
        element2: ArchitectureElement = ConcreteArchitectureElement(
            name="Element2", description="Second element"
        )

        rel: Relationship = Relationship(
            source=element1, target=element2, description="uses"
        )

        with pytest.raises(ValueError):
            element1.remove_relationship(rel)

    def test_get_relationships(self) -> None:
        """
        Test retrieving all relationships from an element.

        Verifies that all relationships are returned in correct order.
        """
        element1: ArchitectureElement = ConcreteArchitectureElement(
            name="Element1", description="First element"
        )
        element2: ArchitectureElement = ConcreteArchitectureElement(
            name="Element2", description="Second element"
        )
        element3: ArchitectureElement = ConcreteArchitectureElement(
            name="Element3", description="Third element"
        )

        rel1: Relationship = Relationship(
            source=element1, target=element2, description="uses"
        )
        rel2: Relationship = Relationship(
            source=element1, target=element3, description="depends on"
        )

        element1.add_relationship(rel1)
        element1.add_relationship(rel2)

        relationships: List[Relationship] = element1.get_relationships()
        assert len(relationships) == 2
        assert rel1 in relationships
        assert rel2 in relationships

    def test_repr(self) -> None:
        """
        Test string representation of ArchitectureElement.

        Verifies that repr() returns a valid string representation.
        """
        element: ArchitectureElement = ConcreteArchitectureElement(
            name="TestElement",
            description="A test element",
        )

        repr_str: str = repr(element)
        assert "ArchitectureElement" in repr_str
        assert "TestElement" in repr_str
        assert "A test element" in repr_str

    def test_to_json_basic(self) -> None:
        """
        Test JSON serialization of basic ArchitectureElement.

        Verifies that toJSON() returns correct structure without relationships.
        """
        element: ArchitectureElement = ConcreteArchitectureElement(
            name="TestElement",
            description="A test element",
        )

        json_data: Dict[str, Any] = element.toJSON()
        assert json_data["name"] == "TestElement"
        assert json_data["description"] == "A test element"
        assert json_data["relationships"] == []

    def test_to_json_with_relationships(self) -> None:
        """
        Test JSON serialization with relationships included.

        Verifies that toJSON() includes relationships in the output.
        """
        element1: ArchitectureElement = ConcreteArchitectureElement(
            name="Element1", description="First element"
        )
        element2: ArchitectureElement = ConcreteArchitectureElement(
            name="Element2", description="Second element"
        )

        rel: Relationship = Relationship(
            source=element1, target=element2, description="uses"
        )
        element1.add_relationship(rel)

        json_data: Dict[str, Any] = element1.toJSON()
        assert len(json_data["relationships"]) == 1
        assert json_data["relationships"][0]["description"] == "uses"


class TestRelationship:
    """Test suite for Relationship class."""

    def test_initialization(self) -> None:
        """
        Test basic initialization of Relationship.

        Verifies that source, target, and description are set correctly.
        """
        source: ArchitectureElement = ConcreteArchitectureElement(
            name="Source", description="Source element"
        )
        target: ArchitectureElement = ConcreteArchitectureElement(
            name="Target", description="Target element"
        )

        rel: Relationship = Relationship(
            source=source, target=target, description="connects to"
        )

        assert rel.source == source
        assert rel.target == target
        assert rel.description == "connects to"

    def test_repr(self) -> None:
        """
        Test string representation of Relationship.

        Verifies that repr() returns a readable format.
        """
        source: ArchitectureElement = ConcreteArchitectureElement(
            name="Source", description="Source element"
        )
        target: ArchitectureElement = ConcreteArchitectureElement(
            name="Target", description="Target element"
        )

        rel: Relationship = Relationship(
            source=source, target=target, description="connects to"
        )

        repr_str: str = repr(rel)
        assert "Relationship" in repr_str
        assert "connects to" in repr_str

    def test_to_json(self) -> None:
        """
        Test JSON serialization of Relationship.

        Verifies that toJSON() returns correct structure with element names.
        """
        source: ArchitectureElement = ConcreteArchitectureElement(
            name="Source", description="Source element"
        )
        target: ArchitectureElement = ConcreteArchitectureElement(
            name="Target", description="Target element"
        )

        rel: Relationship = Relationship(
            source=source, target=target, description="uses"
        )

        json_data: Dict[str, Any] = rel.toJSON()
        assert json_data["source"] == "Source"
        assert json_data["target"] == "Target"
        assert json_data["description"] == "uses"

    def test_to_json_with_none_source(self) -> None:
        """
        Test JSON serialization with None source.

        Verifies that toJSON() handles None source gracefully.
        """
        target: ArchitectureElement = ConcreteArchitectureElement(
            name="Target", description="Target element"
        )

        rel: Relationship = Relationship(
            source=None, target=target, description="external dependency"
        )

        json_data: Dict[str, Any] = rel.toJSON()
        assert json_data["source"] is None
        assert json_data["target"] == "Target"
        assert json_data["description"] == "external dependency"


class TestCode:
    """Test suite for Code class."""

    def test_initialization(self) -> None:
        """
        Test basic initialization of Code element.

        Verifies that Code inherits from ArchitectureElement correctly.
        """
        code: Code = Code(name="AuthService", description="Authentication service code")

        assert code.name == "AuthService"
        assert code.description == "Authentication service code"
        assert code.relationships == []

    def test_initialization_with_relationships(self) -> None:
        """
        Test Code initialization with relationships.

        Verifies that relationships are properly passed to parent class.
        """
        code1: Code = Code(name="Code1", description="First code")
        code2: Code = Code(name="Code2", description="Second code")

        rel: Relationship = Relationship(source=code1, target=code2, description="imports")
        code1_with_rel: Code = Code(
            name="Code1",
            description="First code",
            relationships=[rel],
        )

        assert len(code1_with_rel.relationships) == 1

    def test_to_json(self) -> None:
        """
        Test JSON serialization of Code element.

        Verifies that toJSON() returns correct structure.
        """
        code: Code = Code(name="AuthService", description="Authentication service code")

        json_data: Dict[str, Any] = code.toJSON()
        assert json_data["name"] == "AuthService"
        assert json_data["description"] == "Authentication service code"
        assert "relationships" in json_data

    def test_inheritance_from_architecture_element(self) -> None:
        """
        Test that Code properly inherits from ArchitectureElement.

        Verifies that Code can use inherited methods.
        """
        code1: Code = Code(name="Code1", description="First code")
        code2: Code = Code(name="Code2", description="Second code")

        rel: Relationship = Relationship(source=code1, target=code2, description="imports")
        code1.add_relationship(rel)

        assert len(code1.get_relationships()) == 1
        assert code1.get_relationships()[0] == rel


class TestComponent:
    """Test suite for Component class."""

    def test_initialization_basic(self) -> None:
        """
        Test basic initialization of Component.

        Verifies that Component can be initialized with minimal parameters.
        """
        component: Component = Component(
            name="UserService", description="Manages user data"
        )

        assert component.name == "UserService"
        assert component.description == "Manages user data"
        assert component.technologies == []
        assert component.childrens == []
        assert component.relationships == []

    def test_initialization_with_technologies(self) -> None:
        """
        Test Component initialization with technologies.

        Verifies that technologies list is properly assigned.
        """
        techs: List[str] = ["Python", "FastAPI", "PostgreSQL"]
        component: Component = Component(
            name="UserService",
            description="Manages user data",
            technologies=techs,
        )

        assert component.technologies == techs
        assert len(component.technologies) == 3

    def test_initialization_with_children(self) -> None:
        """
        Test Component initialization with child elements.

        Verifies that children can be assigned during initialization.
        """
        child1: Code = Code(name="User", description="User model")
        child2: Code = Code(name="Repository", description="Data repository")
        children: List[ArchitectureElement] = [child1, child2]

        component: Component = Component(
            name="UserService",
            description="Manages user data",
            childrens=children,
        )

        assert len(component.childrens) == 2
        assert child1 in component.childrens
        assert child2 in component.childrens

    def test_add_child(self) -> None:
        """
        Test adding a child element to Component.

        Verifies that child elements are properly added.
        """
        component: Component = Component(
            name="UserService", description="Manages user data"
        )
        child: Code = Code(name="User", description="User model")

        component.add_child(child)

        assert len(component.childrens) == 1
        assert component.childrens[0] == child

    def test_add_multiple_children(self) -> None:
        """
        Test adding multiple child elements to Component.

        Verifies that multiple children can be added sequentially.
        """
        component: Component = Component(
            name="UserService", description="Manages user data"
        )
        child1: Code = Code(name="User", description="User model")
        child2: Code = Code(name="Repository", description="Data repository")
        child3: Code = Code(name="Service", description="Business logic")

        component.add_child(child1)
        component.add_child(child2)
        component.add_child(child3)

        assert len(component.childrens) == 3
        assert child1 in component.childrens
        assert child2 in component.childrens
        assert child3 in component.childrens

    def test_remove_child(self) -> None:
        """
        Test removing a child element from Component.

        Verifies that children are properly removed.
        """
        component: Component = Component(
            name="UserService", description="Manages user data"
        )
        child: Code = Code(name="User", description="User model")

        component.add_child(child)
        assert len(component.childrens) == 1

        component.remove_child(child)
        assert len(component.childrens) == 0

    def test_remove_child_not_found(self) -> None:
        """
        Test removing a child that doesn't exist.

        Verifies that ValueError is raised when removing non-existent child.
        """
        component: Component = Component(
            name="UserService", description="Manages user data"
        )
        child: Code = Code(name="User", description="User model")

        with pytest.raises(ValueError):
            component.remove_child(child)

    def test_get_childrens(self) -> None:
        """
        Test retrieving all children from Component.

        Verifies that all child elements are returned correctly.
        """
        component: Component = Component(
            name="UserService", description="Manages user data"
        )
        child1: Code = Code(name="User", description="User model")
        child2: Code = Code(name="Repository", description="Data repository")

        component.add_child(child1)
        component.add_child(child2)

        children: List[ArchitectureElement] = component.get_childrens()
        assert len(children) == 2
        assert child1 in children
        assert child2 in children

    def test_change_technologies(self) -> None:
        """
        Test changing technologies list for Component.

        Verifies that technologies can be updated.
        """
        component: Component = Component(
            name="UserService",
            description="Manages user data",
            technologies=["Python"],
        )

        new_techs: List[str] = ["Python", "FastAPI", "PostgreSQL"]
        component.change_technologies(new_techs)

        assert component.technologies == new_techs
        assert len(component.technologies) == 3

    def test_get_technologies(self) -> None:
        """
        Test retrieving technologies from Component.

        Verifies that technologies list is returned correctly.
        """
        techs: List[str] = ["Python", "FastAPI", "PostgreSQL"]
        component: Component = Component(
            name="UserService",
            description="Manages user data",
            technologies=techs,
        )

        retrieved_techs: List[str] = component.get_technologies()
        assert retrieved_techs == techs
        assert len(retrieved_techs) == 3

    def test_to_json_basic(self) -> None:
        """
        Test JSON serialization of basic Component.

        Verifies that toJSON() returns correct structure.
        """
        component: Component = Component(
            name="UserService", description="Manages user data"
        )

        json_data: Dict[str, Any] = component.toJSON()
        assert json_data["name"] == "UserService"
        assert json_data["description"] == "Manages user data"
        assert json_data["technologies"] == []
        assert json_data["childrens"] == []

    def test_to_json_with_technologies_and_children(self) -> None:
        """
        Test JSON serialization with technologies and children.

        Verifies that toJSON() includes all nested data.
        """
        techs: List[str] = ["Python", "FastAPI"]
        child: Code = Code(name="User", description="User model")

        component: Component = Component(
            name="UserService",
            description="Manages user data",
            technologies=techs,
            childrens=[child],
        )

        json_data: Dict[str, Any] = component.toJSON()
        assert json_data["technologies"] == techs
        assert len(json_data["childrens"]) == 1
        assert json_data["childrens"][0]["name"] == "User"

    def test_inheritance_methods(self) -> None:
        """
        Test that Component properly inherits ArchitectureElement methods.

        Verifies that inherited methods work correctly.
        """
        component: Component = Component(
            name="UserService", description="Manages user data"
        )
        other: Component = Component(
            name="AuthService", description="Manages authentication"
        )

        rel: Relationship = Relationship(
            source=component, target=other, description="uses"
        )
        component.add_relationship(rel)

        assert len(component.get_relationships()) == 1


class TestContainer:
    """Test suite for Container class."""

    def test_initialization_basic(self) -> None:
        """
        Test basic initialization of Container.

        Verifies that Container can be initialized with minimal parameters.
        """
        container: Container = Container(
            name="Database", description="Stores application data"
        )

        assert container.name == "Database"
        assert container.description == "Stores application data"
        assert container.technologies == []
        assert container.childrens == []

    def test_initialization_with_all_parameters(self) -> None:
        """
        Test Container initialization with all parameters.

        Verifies that all properties are set correctly.
        """
        techs: List[str] = ["PostgreSQL", "Redis"]
        child: Code = Code(name="Table", description="Database table")
        container: Container = Container(
            name="Database",
            description="Stores application data",
            technologies=techs,
            childrens=[child],
        )

        assert container.name == "Database"
        assert container.technologies == techs
        assert len(container.childrens) == 1

    def test_add_child(self) -> None:
        """
        Test adding a child to Container.

        Verifies that child elements are properly added.
        """
        container: Container = Container(
            name="Database", description="Stores application data"
        )
        child: Code = Code(name="Table", description="Database table")

        container.add_child(child)

        assert len(container.childrens) == 1
        assert container.childrens[0] == child

    def test_remove_child(self) -> None:
        """
        Test removing a child from Container.

        Verifies that children are properly removed.
        """
        container: Container = Container(
            name="Database", description="Stores application data"
        )
        child: Code = Code(name="Table", description="Database table")

        container.add_child(child)
        container.remove_child(child)

        assert len(container.childrens) == 0

    def test_get_childrens(self) -> None:
        """
        Test retrieving all children from Container.

        Verifies that all children are returned correctly.
        """
        container: Container = Container(
            name="Database", description="Stores application data"
        )
        child1: Code = Code(name="Table1", description="Table 1")
        child2: Code = Code(name="Table2", description="Table 2")

        container.add_child(child1)
        container.add_child(child2)

        children: List[ArchitectureElement] = container.get_childrens()
        assert len(children) == 2
        assert child1 in children
        assert child2 in children

    def test_change_technologies(self) -> None:
        """
        Test changing technologies for Container.

        Verifies that technologies list is updated.
        """
        container: Container = Container(
            name="Database",
            description="Stores application data",
            technologies=["PostgreSQL"],
        )

        new_techs: List[str] = ["PostgreSQL", "Redis", "MongoDB"]
        container.change_technologies(new_techs)

        assert container.technologies == new_techs

    def test_get_technologies(self) -> None:
        """
        Test retrieving technologies from Container.

        Verifies that technologies list is returned.
        """
        techs: List[str] = ["PostgreSQL", "Redis"]
        container: Container = Container(
            name="Database",
            description="Stores application data",
            technologies=techs,
        )

        retrieved_techs: List[str] = container.get_technologies()
        assert retrieved_techs == techs

    def test_to_json(self) -> None:
        """
        Test JSON serialization of Container.

        Verifies that toJSON() returns correct structure.
        """
        techs: List[str] = ["PostgreSQL"]
        child: Code = Code(name="Table", description="Database table")

        container: Container = Container(
            name="Database",
            description="Stores application data",
            technologies=techs,
            childrens=[child],
        )

        json_data: Dict[str, Any] = container.toJSON()
        assert json_data["name"] == "Database"
        assert json_data["technologies"] == techs
        assert len(json_data["childrens"]) == 1


class TestSystemContext:
    """Test suite for SystemContext class."""

    def test_initialization_basic(self) -> None:
        """
        Test basic initialization of SystemContext.

        Verifies that SystemContext can be initialized with minimal parameters.
        """
        system: SystemContext = SystemContext(
            name="ECommerce System", description="Online shopping system"
        )

        assert system.name == "ECommerce System"
        assert system.description == "Online shopping system"
        assert system.childrens == []

    def test_initialization_with_children(self) -> None:
        """
        Test SystemContext initialization with children.

        Verifies that child elements are properly assigned.
        """
        child1: Container = Container(
            name="WebApp", description="Web application"
        )
        child2: Container = Container(
            name="Database", description="Database"
        )

        system: SystemContext = SystemContext(
            name="ECommerce System",
            description="Online shopping system",
            childrens=[child1, child2],
        )

        assert len(system.childrens) == 2
        assert child1 in system.childrens
        assert child2 in system.childrens

    def test_add_child(self) -> None:
        """
        Test adding a child to SystemContext.

        Verifies that child elements are properly added.
        """
        system: SystemContext = SystemContext(
            name="ECommerce System", description="Online shopping system"
        )
        child: Container = Container(
            name="WebApp", description="Web application"
        )

        system.add_child(child)

        assert len(system.childrens) == 1
        assert system.childrens[0] == child

    def test_add_multiple_children(self) -> None:
        """
        Test adding multiple children to SystemContext.

        Verifies that multiple children can be added sequentially.
        """
        system: SystemContext = SystemContext(
            name="ECommerce System", description="Online shopping system"
        )
        child1: Container = Container(
            name="WebApp", description="Web application"
        )
        child2: Container = Container(
            name="Database", description="Database"
        )
        child3: Container = Container(
            name="Cache", description="Cache layer"
        )

        system.add_child(child1)
        system.add_child(child2)
        system.add_child(child3)

        assert len(system.childrens) == 3
        assert child1 in system.childrens
        assert child2 in system.childrens
        assert child3 in system.childrens

    def test_remove_child(self) -> None:
        """
        Test removing a child from SystemContext.

        Verifies that children are properly removed.
        """
        system: SystemContext = SystemContext(
            name="ECommerce System", description="Online shopping system"
        )
        child: Container = Container(
            name="WebApp", description="Web application"
        )

        system.add_child(child)
        assert len(system.childrens) == 1

        system.remove_child(child)
        assert len(system.childrens) == 0

    def test_remove_child_not_found(self) -> None:
        """
        Test removing a child that doesn't exist.

        Verifies that ValueError is raised.
        """
        system: SystemContext = SystemContext(
            name="ECommerce System", description="Online shopping system"
        )
        child: Container = Container(
            name="WebApp", description="Web application"
        )

        with pytest.raises(ValueError):
            system.remove_child(child)

    def test_get_childrens(self) -> None:
        """
        Test retrieving all children from SystemContext.

        Verifies that all children are returned correctly.
        """
        system: SystemContext = SystemContext(
            name="ECommerce System", description="Online shopping system"
        )
        child1: Container = Container(
            name="WebApp", description="Web application"
        )
        child2: Container = Container(
            name="Database", description="Database"
        )

        system.add_child(child1)
        system.add_child(child2)

        children: List[ArchitectureElement] = system.get_childrens()
        assert len(children) == 2
        assert child1 in children
        assert child2 in children

    def test_to_json_basic(self) -> None:
        """
        Test JSON serialization of basic SystemContext.

        Verifies that toJSON() returns correct structure.
        """
        system: SystemContext = SystemContext(
            name="ECommerce System", description="Online shopping system"
        )

        json_data: Dict[str, Any] = system.toJSON()
        assert json_data["name"] == "ECommerce System"
        assert json_data["description"] == "Online shopping system"
        assert json_data["childrens"] == []

    def test_to_json_with_children(self) -> None:
        """
        Test JSON serialization with children.

        Verifies that toJSON() includes all children in output.
        """
        child1: Container = Container(
            name="WebApp", description="Web application"
        )
        child2: Container = Container(
            name="Database", description="Database"
        )

        system: SystemContext = SystemContext(
            name="ECommerce System",
            description="Online shopping system",
            childrens=[child1, child2],
        )

        json_data: Dict[str, Any] = system.toJSON()
        assert len(json_data["childrens"]) == 2
        assert json_data["childrens"][0]["name"] == "WebApp"
        assert json_data["childrens"][1]["name"] == "Database"

    def test_to_json_with_nested_children(self) -> None:
        """
        Test JSON serialization with nested children.

        Verifies that toJSON() properly serializes deeply nested structures.
        """
        code: Code = Code(name="UserModel", description="User data model")
        component: Component = Component(
            name="UserComponent", description="User management", childrens=[code]
        )
        system: SystemContext = SystemContext(
            name="ECommerce System",
            description="Online shopping system",
            childrens=[component],
        )

        json_data: Dict[str, Any] = system.toJSON()
        assert len(json_data["childrens"]) == 1
        assert "childrens" in json_data["childrens"][0]

    def test_hierarchy_building(self) -> None:
        """
        Test building a complete hierarchy of architecture elements.

        Verifies that a multi-level hierarchy can be constructed and navigated.
        """
        # Create Code elements
        user_model: Code = Code(name="User", description="User model")
        product_model: Code = Code(name="Product", description="Product model")

        # Create Components
        user_component: Component = Component(
            name="UserComponent",
            description="User management",
            childrens=[user_model],
            technologies=["Python"],
        )
        product_component: Component = Component(
            name="ProductComponent",
            description="Product management",
            childrens=[product_model],
            technologies=["Python"],
        )

        # Create Containers
        app_container: Container = Container(
            name="WebApplication",
            description="Main web app",
            childrens=[user_component, product_component],
            technologies=["FastAPI", "PostgreSQL"],
        )
        db_container: Container = Container(
            name="Database",
            description="Data store",
            technologies=["PostgreSQL"],
        )

        # Create SystemContext
        system: SystemContext = SystemContext(
            name="ECommerce System",
            description="Online shopping platform",
            childrens=[app_container, db_container],
        )

        # Verify hierarchy
        assert len(system.childrens) == 2
        assert len(app_container.childrens) == 2
        assert len(user_component.childrens) == 1

    def test_relationships_across_hierarchy(self) -> None:
        """
        Test creating relationships between elements across hierarchy.

        Verifies that relationships can be created between different hierarchy levels.
        """
        user_component: Component = Component(
            name="UserComponent", description="User management"
        )
        product_component: Component = Component(
            name="ProductComponent", description="Product management"
        )

        # Create relationship between components
        rel: Relationship = Relationship(
            source=user_component,
            target=product_component,
            description="fetches products for user",
        )
        user_component.add_relationship(rel)

        # Verify relationship
        relationships: List[Relationship] = user_component.get_relationships()
        assert len(relationships) == 1
        assert relationships[0].description == "fetches products for user"
