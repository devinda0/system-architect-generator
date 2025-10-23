# OOP Design: AI-Powered Software Engineering Workbench

This document outlines an object-oriented design for the system based on the provided architecture. The design focuses on encapsulating responsibilities within distinct classes that represent the system's core components.

## 1. Core Domain Model (C4 Architecture Elements)

```
+--------------------------+
| ArchitectureElement      | (Abstract)
+--------------------------+
| - id: String             |
| - name: String           |
| - description: String    |
| - relationships: List    |
+--------------------------+
| + toJSON(): Dict         |
| + addRelationship(): void|
+--------------------------+
         ^
         | (Inherits)
    +----+----+
    |         |
+---+--+  +---+--+
|System|  |Conta-|  +---+--+
|Cont. |  |iner  |  |Compo-|
+------+  +------+  |nent  |
         |Techno|  +------+
         |logy  |
         |Chldn |
         +------+
```

### Class Definitions

#### ArchitectureElement (Abstract Base Class)

**Purpose**: Defines the common properties and behaviors for all elements in the architectural model.

**Attributes**:
- `id`: A unique identifier.
- `name`: The name of the element (e.g., "Web Application", "Database").
- `description`: A detailed description of its purpose.
- `relationships`: A list of Relationship objects defining connections to other elements.

**Methods**:
- `toJSON()`: Serializes the element and its properties into a JSON-compatible dictionary for storage and API responses.
- `addRelationship(element, description)`: Creates a link to another ArchitectureElement.

#### SystemContext (inherits from ArchitectureElement)

**Purpose**: Represents the highest level of abstraction, the system itself.

**Attributes**:
- `children`: A list of Container objects within the system.

#### Container (inherits from ArchitectureElement)

**Purpose**: Represents a deployable unit like a web server, database, or microservice.

**Attributes**:
- `technology`: The primary technology used (e.g., "FastAPI", "PostgreSQL").
- `children`: A list of Component objects it contains.

#### Component (inherits from ArchitectureElement)

**Purpose**: Represents a logical module or a group of related functionalities within a container.

**Attributes**:
- `technology`: The primary technology or library used (e.g., "React Component", "Authentication Service").
- `children`: (Optional) Can be extended to include Code elements.

#### Relationship

**Purpose**: A simple data class to define the link between two ArchitectureElement objects.

**Attributes**:
- `targetId`: The ID of the element this relationship points to.
- `description`: The description of the interaction (e.g., "Sends API requests to", "Reads data from").

---

## 2. AI Design Engine (Iterative & On-Demand)

This design supports iterative generation. The DesignEngine holds multiple specialized LangChain chains, each callable on-demand for specific tasks on individual C4 nodes.

```
+-----------------------------+
|      DesignEngine           |
+-----------------------------+
| - initialGenerationChain    |
| - techSuggestionChain       |
| - decompositionChain        |
| - refactorChain             |
| - apiSuggestionChain        |
+-----------------------------+
| + generateInitialDesign()   |
| + suggestTechnology()       |
| + suggestSubComponents()    |
| + suggestApiEndpoints()     |
| + refactorElement()         |
+-----------------------------+
         |
         | (Uses one of many chains)
         v
+-----------------------------+        +--------------------------+
| SpecializedChain (LCEL)     |------->| ChatGemini (LangChain)   |
+-----------------------------+        +--------------------------+
| - promptTemplate            |        | - modelName: String      |
| - modelName: String         |        | - apiKey                 |
| - retriever: RAGRetriever   |        +--------------------------+
| - outputParser              |
+-----------------------------+
         |
         v
+-----------------------------+
| RAGRetriever (LangChain)    |
+-----------------------------+
| - kbService                 |
+-----------------------------+
| + getRelevantDocuments()    |
+-----------------------------+
         |
         v
+-----------------------------+
|KnowledgeBaseService         |
+-----------------------------+
| - vectorDB: VectorDB_Client |
| - metadataDB: PG_Client     |
+-----------------------------+
| + getContext(query)         |
+-----------------------------+
```

### Class/Component Definitions

#### DesignEngine

**Purpose**: The central orchestrator for AI-driven actions. It owns multiple, specialized chains to perform granular, on-demand tasks.

**Attributes**:
- `initialGenerationChain`: A LangChain runnable for creating the initial SystemContext and high-level Containers.
- `techSuggestionChain`: A chain to suggest technology for a specific ArchitectureElement.
- `decompositionChain`: A chain that takes a Container and suggests child Component objects.
- `apiSuggestionChain`: A chain that suggests API endpoints for a Component.
- `refactorChain`: A chain that refactors an element based on a user request.

**Methods**:
- `generateInitialDesign(requirements)`: Invokes the initialGenerationChain to create the root SystemContext and its immediate Container children.
- `suggestTechnology(element)`: Invokes the techSuggestionChain for a given element.
- `suggestSubComponents(container)`: Invokes the decompositionChain to generate child components for a container.
- `suggestApiEndpoints(component)`: Invokes the apiSuggestionChain.
- `refactorElement(element, userRequest)`: Invokes the refactorChain.

#### SpecializedChain (LCEL)

**Purpose**: This is a pattern, not a single class. It represents any of the specialized chains (e.g., techSuggestionChain). Each is a unique composition of a PromptTemplate, RAGRetriever, the ChatGemini model, and an OutputParser (likely JsonOutputParser), all built using LangChain Expression Language (LCEL).

#### RAGRetriever (LangChain Retriever)

**Purpose**: Acts as the LangChain-compatible interface for fetching knowledge. It delegates the complex logic of hybrid search to the KnowledgeBaseService.

**Attributes**:
- `kbService`: An instance of KnowledgeBaseService.

**Methods**:
- `getRelevantDocuments(query)`: The core method used within the chain. It calls `kbService.getContext(query)` to get relevant data and formats it as LangChain Document objects.

#### KnowledgeBaseService

**Purpose**: Manages the hybrid knowledge base (Vector + Relational DB).

**Attributes**:
- `vectorDB`: Client connection (e.g., ChromaDB, Pinecone).
- `metadataDB`: Client connection (PostgreSQL).

**Methods**:
- `getContext(query)`: Performs hybrid search.

#### ChatGemini (LangChain LLM Wrapper)

**Purpose**: LangChain-native wrapper for the Google Gemini API.

**Attributes**:
- `modelName`: (e.g., 'gemini-pro' or 'gemini-flash').
- `apiKey`: API key.

---

## 3. Backend Services & Data Management (Iterative)

The controller is updated to expose endpoints for the granular, on-demand AI actions, mapping directly to the DesignEngine's methods.

```
+----------------------+    +-----------------------------+    +-------------------------+
| FastAPIServer        |    | ProjectController           |    | ProjectRepository       |
+----------------------+    +-----------------------------+    +-------------------------+
| - app: FastAPI       |--->| - designEngine: DesignEngine|    | - db: MongoDB_Client    |
| + start()            |    | - repository: ProjectRepo   |    +-------------------------+
+----------------------+    | + createProject(req)        |    | + saveDesign(design)    |
                            | + getDesign(id)             |    | + findDesignById(id)    |
                            | + invokeAIAction(id, action)|    | + updateElement(id, d)  |
                            +-----------------------------+    +-------------------------+
```

### Class Definitions

#### ProjectController

**Purpose**: Handles API requests for creating projects and performing iterative, on-demand AI operations on the design.

**Attributes**:
- `designEngine`: Instance of DesignEngine.
- `projectRepository`: Instance of ProjectRepository.

**Methods**:
- `createProject(requirements)`: Creates a project, calls `designEngine.generateInitialDesign()`, and saves the result using the projectRepository.
- `getDesign(projectId)`: Retrieves a full design tree from the repository.
- `invokeAIAction(elementId, actionRequest)`: The key method for iteration.
  - It finds the design and the specific elementId within it.
  - Based on `actionRequest.type` (e.g., "SUGGEST_TECH", "DECOMPOSE", "REFACTOR"), it calls the corresponding method on the designEngine (e.g., `designEngine.suggestTechnology(element)`).
  - It then saves the updated design tree back to the repository.

#### ProjectRepository

**Purpose**: An abstraction layer for all database operations.

**Attributes**:
- `db_connection`: A client connection to the MongoDB database.

**Methods**:
- `saveDesign(projectDesignTree)`: Creates or updates an entire project design document in MongoDB.
- `findDesignById(projectId)`: Retrieves a project's full design tree.
- `updateElement(elementId, data)`: (Alternative) A more granular update method that finds a specific element within a design document and updates its properties.
