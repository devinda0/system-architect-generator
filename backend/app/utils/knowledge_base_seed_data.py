"""
Knowledge Base Seeding Data

This module contains curated architectural knowledge for initial seeding
of the knowledge base, including patterns, technologies, design principles,
and best practices.
"""

from datetime import datetime
from app.schemas.knowledge_base import KnowledgeDocumentCreate, KnowledgeDocumentMetadata


# Architectural Patterns
ARCHITECTURAL_PATTERNS = [
    KnowledgeDocumentCreate(
        category="architectural_pattern",
        title="Microservices Architecture",
        content="""Microservices is an architectural style that structures an application as a collection of loosely coupled services. Each service is self-contained, implements a single business capability, and can be deployed independently. Services communicate through well-defined APIs, typically using HTTP/REST or message queues.""",
        use_cases=[
            "Large-scale web applications with complex business domains",
            "Applications requiring independent scaling of components",
            "Systems with multiple development teams",
            "Applications that need to support multiple platforms and devices"
        ],
        advantages=[
            "Independent deployment and scaling of services",
            "Technology diversity - different services can use different tech stacks",
            "Improved fault isolation and resilience",
            "Better organized around business capabilities",
            "Enables continuous deployment and delivery"
        ],
        disadvantages=[
            "Increased operational complexity",
            "Network latency and reliability concerns",
            "Data consistency challenges (distributed transactions)",
            "Requires sophisticated DevOps practices",
            "Testing complexity increases"
        ],
        implementation_notes="""Requires robust infrastructure including service discovery, API gateway, distributed tracing, centralized logging, and container orchestration (e.g., Kubernetes). Consider starting with a modular monolith and evolving to microservices as needed.""",
        related_patterns=["Event-Driven Architecture", "CQRS", "API Gateway", "Service Mesh"],
        anti_patterns=["Distributed Monolith", "Shared Database"],
        metadata=KnowledgeDocumentMetadata(
            source="Martin Fowler - Microservices Resource Guide",
            author="Martin Fowler",
            url="https://martinfowler.com/microservices/",
            tags=["architecture", "distributed-systems", "scalability"],
            quality_score=0.95,
            is_verified=True
        )
    ),
    
    KnowledgeDocumentCreate(
        category="architectural_pattern",
        title="Event-Driven Architecture",
        content="""Event-Driven Architecture (EDA) is a software design pattern where the flow of the program is determined by events. Components communicate through the production, detection, and consumption of events. An event represents a significant change in state or an occurrence within the system.""",
        use_cases=[
            "Real-time data processing and analytics",
            "Decoupled microservices communication",
            "IoT and sensor data processing",
            "User activity tracking and notifications",
            "Order processing and inventory management"
        ],
        advantages=[
            "Loose coupling between components",
            "High scalability and responsiveness",
            "Asynchronous processing improves performance",
            "Better support for event sourcing and CQRS",
            "Natural fit for reactive systems"
        ],
        disadvantages=[
            "Complexity in debugging and tracing event flows",
            "Eventual consistency challenges",
            "Potential for message duplication or loss",
            "Requires robust message broker infrastructure",
            "Difficult to understand overall system behavior"
        ],
        implementation_notes="""Use message brokers like Apache Kafka, RabbitMQ, or cloud services like AWS EventBridge. Implement idempotent consumers to handle message duplication. Consider event schemas and versioning strategy from the start.""",
        related_patterns=["CQRS", "Event Sourcing", "Microservices", "Pub-Sub"],
        tech_stack_compatibility=["Apache Kafka", "RabbitMQ", "AWS EventBridge", "Google Pub/Sub"],
        metadata=KnowledgeDocumentMetadata(
            source="AWS Architecture Center",
            url="https://aws.amazon.com/event-driven-architecture/",
            tags=["architecture", "events", "messaging", "asynchronous"],
            quality_score=0.92,
            is_verified=True
        )
    ),
    
    KnowledgeDocumentCreate(
        category="architectural_pattern",
        title="Monolithic Architecture",
        content="""A monolithic architecture is a traditional unified model where all components of an application are interconnected and interdependent. The entire application is built as a single, self-contained unit with all functionality packaged together.""",
        use_cases=[
            "Small to medium-sized applications",
            "Startups and MVPs requiring rapid development",
            "Applications with straightforward business logic",
            "Teams with limited DevOps resources"
        ],
        advantages=[
            "Simpler development and deployment",
            "Easier debugging and testing",
            "Better performance for simple applications",
            "Less operational overhead",
            "Straightforward transactions and data consistency"
        ],
        disadvantages=[
            "Difficult to scale specific components independently",
            "Long-term maintainability challenges as codebase grows",
            "Technology stack lock-in",
            "Slower deployment cycles",
            "Risk of entire system failure from single bug"
        ],
        implementation_notes="""Consider modular monolith approach - organize code into well-defined modules with clear boundaries. This provides benefits of monolith while enabling future migration to microservices if needed.""",
        related_patterns=["Modular Monolith", "Layered Architecture"],
        anti_patterns=["Big Ball of Mud", "Spaghetti Code"],
        metadata=KnowledgeDocumentMetadata(
            source="Software Architecture Patterns - O'Reilly",
            tags=["architecture", "monolith", "traditional"],
            quality_score=0.88,
            is_verified=True
        )
    ),
    
    KnowledgeDocumentCreate(
        category="architectural_pattern",
        title="Serverless Architecture",
        content="""Serverless architecture is a cloud computing execution model where the cloud provider dynamically manages the allocation and provisioning of servers. Applications are broken down into individual functions that are invoked in response to events.""",
        use_cases=[
            "APIs and backends with variable traffic",
            "Data processing and ETL pipelines",
            "Scheduled tasks and batch jobs",
            "Real-time file processing",
            "Chatbots and IoT backends"
        ],
        advantages=[
            "No server management required",
            "Automatic scaling based on demand",
            "Pay only for actual usage",
            "Faster time to market",
            "Built-in high availability"
        ],
        disadvantages=[
            "Cold start latency issues",
            "Vendor lock-in concerns",
            "Limited execution duration",
            "Debugging and monitoring complexity",
            "Potential for higher costs at scale"
        ],
        implementation_notes="""Use AWS Lambda, Azure Functions, or Google Cloud Functions. Design functions to be stateless and idempotent. Implement proper monitoring and observability from the start. Consider warm-up strategies for critical paths.""",
        related_patterns=["Event-Driven Architecture", "BFF (Backend for Frontend)"],
        tech_stack_compatibility=["AWS Lambda", "Azure Functions", "Google Cloud Functions", "Vercel Functions"],
        metadata=KnowledgeDocumentMetadata(
            source="Serverless Architecture Patterns - AWS",
            url="https://aws.amazon.com/serverless/",
            tags=["architecture", "serverless", "cloud", "faas"],
            quality_score=0.90,
            is_verified=True
        )
    )
]


# Technologies
TECHNOLOGIES = [
    KnowledgeDocumentCreate(
        category="technology",
        title="FastAPI",
        content="""FastAPI is a modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints. It provides automatic API documentation, data validation, and serialization out of the box.""",
        use_cases=[
            "RESTful API development",
            "Microservices backends",
            "Machine learning model serving",
            "Real-time applications with WebSocket support"
        ],
        advantages=[
            "Excellent performance comparable to NodeJS and Go",
            "Automatic interactive API documentation (Swagger/OpenAPI)",
            "Type hints provide automatic data validation",
            "Async/await support for concurrent operations",
            "Easy to learn and use"
        ],
        disadvantages=[
            "Smaller ecosystem compared to Flask/Django",
            "Less mature for complex web applications",
            "Fewer third-party plugins available"
        ],
        implementation_notes="""Best suited for API-first applications. Use Pydantic models for request/response validation. Leverage async capabilities for I/O-bound operations. Combine with Celery for background tasks.""",
        programming_languages=["Python"],
        tech_stack_compatibility=["PostgreSQL", "MongoDB", "Redis", "Docker", "Kubernetes"],
        metadata=KnowledgeDocumentMetadata(
            source="FastAPI Official Documentation",
            url="https://fastapi.tiangolo.com/",
            tags=["python", "web-framework", "api", "async"],
            quality_score=0.94,
            is_verified=True
        )
    ),
    
    KnowledgeDocumentCreate(
        category="technology",
        title="Next.js",
        content="""Next.js is a React framework that enables functionality such as server-side rendering and static site generation. It provides an excellent developer experience with features like automatic code splitting, optimized performance, and built-in routing.""",
        use_cases=[
            "SEO-critical web applications",
            "E-commerce platforms",
            "Content management systems",
            "Marketing websites and landing pages",
            "Full-stack web applications"
        ],
        advantages=[
            "Server-side rendering improves SEO and initial load time",
            "Automatic code splitting and optimization",
            "Built-in routing and API routes",
            "Excellent developer experience",
            "Strong TypeScript support",
            "Incremental Static Regeneration (ISR)"
        ],
        disadvantages=[
            "Learning curve for SSR concepts",
            "Can be overkill for simple SPAs",
            "Vendor lock-in with Vercel for some features"
        ],
        implementation_notes="""Use App Router for new projects (Next.js 13+). Leverage server components for better performance. Use static generation where possible, SSR where necessary. Implement proper caching strategies.""",
        programming_languages=["JavaScript", "TypeScript"],
        tech_stack_compatibility=["React", "Vercel", "Node.js", "Tailwind CSS"],
        metadata=KnowledgeDocumentMetadata(
            source="Next.js Official Documentation",
            url="https://nextjs.org/docs",
            tags=["javascript", "react", "framework", "ssr", "frontend"],
            quality_score=0.96,
            is_verified=True
        )
    ),
    
    KnowledgeDocumentCreate(
        category="technology",
        title="PostgreSQL",
        content="""PostgreSQL is a powerful, open-source object-relational database system with a strong reputation for reliability, feature robustness, and performance. It supports both SQL and JSON querying.""",
        use_cases=[
            "OLTP (Online Transaction Processing) systems",
            "Data warehousing and analytics",
            "Geospatial applications (with PostGIS)",
            "Applications requiring complex queries and transactions",
            "Multi-tenant SaaS applications"
        ],
        advantages=[
            "ACID compliant with strong data integrity",
            "Extensive feature set including advanced indexing",
            "Support for JSON/JSONB for semi-structured data",
            "Excellent performance for complex queries",
            "Active community and ecosystem",
            "Free and open source"
        ],
        disadvantages=[
            "Can be resource-intensive",
            "Steeper learning curve than simpler databases",
            "Replication setup more complex than some alternatives"
        ],
        implementation_notes="""Use connection pooling (PgBouncer) for high-traffic applications. Implement proper indexing strategies. Use JSONB for flexible schema requirements. Consider partitioning for large tables. Regular VACUUM and ANALYZE for performance.""",
        tech_stack_compatibility=["Django", "FastAPI", "Node.js", "Java Spring", "Rails"],
        metadata=KnowledgeDocumentMetadata(
            source="PostgreSQL Official Documentation",
            url="https://www.postgresql.org/docs/",
            tags=["database", "sql", "relational", "postgres"],
            quality_score=0.95,
            is_verified=True
        )
    ),
    
    KnowledgeDocumentCreate(
        category="technology",
        title="MongoDB",
        content="""MongoDB is a source-available cross-platform document-oriented database program. It stores data in flexible, JSON-like documents, making it ideal for applications that require a flexible schema.""",
        use_cases=[
            "Content management systems",
            "Real-time analytics and logging",
            "Product catalogs with varying attributes",
            "Mobile and web applications",
            "IoT and time-series data"
        ],
        advantages=[
            "Flexible schema design",
            "Horizontal scalability through sharding",
            "Rich query language and aggregation framework",
            "High performance for read-heavy workloads",
            "Easy to start and develop with"
        ],
        disadvantages=[
            "No ACID transactions across multiple documents (before 4.0)",
            "Can consume more storage than relational databases",
            "Joins are less efficient than in SQL databases",
            "Potential for data duplication"
        ],
        implementation_notes="""Design schema based on access patterns, not relationships. Use embedded documents for one-to-few relationships. Use references for one-to-many and many-to-many. Implement proper indexing. Use aggregation pipeline for complex queries.""",
        tech_stack_compatibility=["Node.js", "Python", "Java", "Express", "Mongoose"],
        metadata=KnowledgeDocumentMetadata(
            source="MongoDB Official Documentation",
            url="https://docs.mongodb.com/",
            tags=["database", "nosql", "document-db", "mongodb"],
            quality_score=0.92,
            is_verified=True
        )
    )
]


# Design Principles
DESIGN_PRINCIPLES = [
    KnowledgeDocumentCreate(
        category="design_principle",
        title="SOLID Principles",
        content="""SOLID is an acronym for five design principles intended to make software designs more understandable, flexible, and maintainable. The principles are: Single Responsibility, Open-Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion.""",
        use_cases=[
            "Object-oriented programming and design",
            "Large codebases requiring maintainability",
            "Team development environments",
            "Long-lived applications"
        ],
        advantages=[
            "Improves code maintainability and readability",
            "Reduces coupling between components",
            "Facilitates testing and mocking",
            "Makes code more flexible to change",
            "Encourages better architecture"
        ],
        disadvantages=[
            "Can lead to over-engineering in simple cases",
            "Increases number of classes and interfaces",
            "Learning curve for junior developers"
        ],
        implementation_notes="""Apply pragmatically - not every class needs to follow all principles perfectly. Single Responsibility Principle (SRP) is often the most impactful. Use dependency injection to achieve Dependency Inversion Principle (DIP).""",
        related_patterns=["Dependency Injection", "Strategy Pattern", "Factory Pattern"],
        metadata=KnowledgeDocumentMetadata(
            source="Clean Code - Robert C. Martin",
            author="Robert C. Martin (Uncle Bob)",
            tags=["design-principles", "oop", "solid", "clean-code"],
            quality_score=0.97,
            is_verified=True
        )
    ),
    
    KnowledgeDocumentCreate(
        category="design_principle",
        title="DRY (Don't Repeat Yourself)",
        content="""The DRY principle states that every piece of knowledge must have a single, unambiguous, authoritative representation within a system. The principle is aimed at reducing repetition and duplication in code.""",
        use_cases=[
            "All software development projects",
            "Code refactoring initiatives",
            "Building reusable components and libraries"
        ],
        advantages=[
            "Easier maintenance - changes in one place",
            "Reduced code size",
            "Fewer bugs from inconsistent duplicates",
            "Improved code clarity"
        ],
        disadvantages=[
            "Can lead to premature abstraction",
            "May reduce code readability if over-applied",
            "Shared code creates coupling"
        ],
        implementation_notes="""Balance DRY with readability. Don't abstract too early - wait until you have 3 instances before abstracting. Consider WET (Write Everything Twice) for unrelated duplications. Use functions, classes, and modules to eliminate duplication.""",
        related_patterns=["Abstraction", "Composition"],
        metadata=KnowledgeDocumentMetadata(
            source="The Pragmatic Programmer",
            author="Andy Hunt and Dave Thomas",
            tags=["design-principles", "dry", "best-practices"],
            quality_score=0.93,
            is_verified=True
        )
    ),
    
    KnowledgeDocumentCreate(
        category="design_principle",
        title="Separation of Concerns",
        content="""Separation of Concerns is a design principle for separating a computer program into distinct sections, each addressing a separate concern. A concern is a set of information that affects the code of a program.""",
        use_cases=[
            "Large application architecture",
            "MVC/MVVM pattern implementations",
            "Microservices design",
            "Modular system design"
        ],
        advantages=[
            "Improves code organization and clarity",
            "Enables parallel development",
            "Facilitates testing of individual concerns",
            "Reduces coupling between components",
            "Easier to modify and extend"
        ],
        disadvantages=[
            "Can increase code complexity with too many layers",
            "May impact performance with excessive abstraction",
            "Requires careful interface design"
        ],
        implementation_notes="""Implement through layered architecture (presentation, business logic, data access). Use MVC or similar patterns for UI applications. In microservices, each service should address a specific concern. Avoid mixing business logic with UI or data access code.""",
        related_patterns=["MVC", "Layered Architecture", "Microservices"],
        metadata=KnowledgeDocumentMetadata(
            source="Software Engineering Principles",
            tags=["design-principles", "architecture", "separation-of-concerns"],
            quality_score=0.91,
            is_verified=True
        )
    )
]


# Best Practices
BEST_PRACTICES = [
    KnowledgeDocumentCreate(
        category="best_practice",
        title="API Design - RESTful Conventions",
        content="""RESTful API design follows a set of conventions for creating web services that are scalable, maintainable, and easy to understand. Key principles include using HTTP methods correctly, proper resource naming, and stateless communication.""",
        use_cases=[
            "Web API development",
            "Microservices communication",
            "Mobile app backends",
            "Third-party integrations"
        ],
        advantages=[
            "Standardized approach understood by developers",
            "Stateless design improves scalability",
            "Cacheable responses improve performance",
            "Clear resource hierarchy",
            "HTTP methods provide semantic meaning"
        ],
        disadvantages=[
            "Not always ideal for complex operations",
            "Can lead to chattiness with multiple requests",
            "Rigid structure may not fit all use cases"
        ],
        implementation_notes="""Use nouns for resources (GET /users, not /getUsers). Use HTTP methods correctly (GET for read, POST for create, PUT/PATCH for update, DELETE for delete). Version your API (/v1/users). Use proper HTTP status codes. Implement pagination for collections. Provide clear error messages.""",
        related_patterns=["API Gateway", "BFF (Backend for Frontend)"],
        metadata=KnowledgeDocumentMetadata(
            source="REST API Design Rulebook - O'Reilly",
            url="https://restfulapi.net/",
            tags=["api", "rest", "best-practices", "web-services"],
            quality_score=0.94,
            is_verified=True
        )
    ),
    
    KnowledgeDocumentCreate(
        category="best_practice",
        title="Security - OWASP Top 10",
        content="""The OWASP Top 10 is a standard awareness document for developers and web application security. It represents a broad consensus about the most critical security risks to web applications.""",
        use_cases=[
            "Web application development",
            "Security audits and assessments",
            "Developer training",
            "Security requirement definition"
        ],
        advantages=[
            "Industry-standard security baseline",
            "Regularly updated with current threats",
            "Comprehensive coverage of common vulnerabilities",
            "Actionable mitigation strategies"
        ],
        disadvantages=[
            "Not exhaustive - doesn't cover all security issues",
            "Requires ongoing updates as threats evolve"
        ],
        implementation_notes="""Key areas: 1) Injection flaws (SQL, NoSQL, OS commands) 2) Broken authentication 3) Sensitive data exposure 4) XML External Entities (XXE) 5) Broken access control 6) Security misconfiguration 7) Cross-Site Scripting (XSS) 8) Insecure deserialization 9) Using components with known vulnerabilities 10) Insufficient logging and monitoring. Use parameterized queries, implement proper authentication, encrypt sensitive data, validate all inputs, use security headers, keep dependencies updated.""",
        related_patterns=["Defense in Depth", "Principle of Least Privilege"],
        metadata=KnowledgeDocumentMetadata(
            source="OWASP Foundation",
            url="https://owasp.org/www-project-top-ten/",
            tags=["security", "owasp", "best-practices", "web-security"],
            quality_score=0.98,
            is_verified=True
        )
    ),
    
    KnowledgeDocumentCreate(
        category="best_practice",
        title="Database Indexing Strategies",
        content="""Proper database indexing is crucial for query performance. An index is a data structure that improves the speed of data retrieval operations on a database table at the cost of additional writes and storage space.""",
        use_cases=[
            "Optimizing database query performance",
            "Large-scale data applications",
            "Reporting and analytics systems",
            "High-traffic web applications"
        ],
        advantages=[
            "Dramatically improves query performance",
            "Enables efficient sorting and filtering",
            "Supports unique constraints",
            "Improves join operations"
        ],
        disadvantages=[
            "Increases storage requirements",
            "Slows down write operations",
            "Requires maintenance and monitoring"
        ],
        implementation_notes="""Index columns used in WHERE clauses, JOIN conditions, and ORDER BY clauses. Use composite indexes for queries filtering on multiple columns. Consider covering indexes for frequently accessed queries. Monitor index usage and remove unused indexes. Use EXPLAIN/EXPLAIN ANALYZE to understand query execution. B-tree indexes for most use cases, hash indexes for equality comparisons, full-text indexes for text search.""",
        related_patterns=["Database Query Optimization", "Caching Strategies"],
        metadata=KnowledgeDocumentMetadata(
            source="Database Internals - O'Reilly",
            tags=["database", "performance", "indexing", "best-practices"],
            quality_score=0.92,
            is_verified=True
        )
    ),
    
    KnowledgeDocumentCreate(
        category="best_practice",
        title="Error Handling and Logging",
        content="""Proper error handling and logging are essential for building robust, maintainable applications. They enable debugging, monitoring, and provide visibility into application behavior and issues.""",
        use_cases=[
            "All software applications",
            "Distributed systems",
            "Production environments",
            "Customer-facing applications"
        ],
        advantages=[
            "Improves debugging and troubleshooting",
            "Enables proactive monitoring and alerting",
            "Provides audit trail for compliance",
            "Helps identify performance bottlenecks",
            "Improves user experience with graceful error handling"
        ],
        disadvantages=[
            "Can impact performance if not implemented efficiently",
            "Log storage costs",
            "Potential security risks from logging sensitive data"
        ],
        implementation_notes="""Use structured logging (JSON format). Implement log levels (DEBUG, INFO, WARN, ERROR). Never log sensitive data (passwords, tokens, PII). Use correlation IDs to track requests across services. Implement centralized logging in distributed systems. Use try-catch blocks appropriately. Return user-friendly error messages while logging detailed errors. Implement exponential backoff for retries. Use circuit breakers for external dependencies.""",
        related_patterns=["Circuit Breaker", "Retry Pattern", "Observability"],
        metadata=KnowledgeDocumentMetadata(
            source="Site Reliability Engineering - Google",
            tags=["error-handling", "logging", "observability", "best-practices"],
            quality_score=0.93,
            is_verified=True
        )
    )
]


# Combine all seeding data
ALL_SEED_DATA = (
    ARCHITECTURAL_PATTERNS +
    TECHNOLOGIES +
    DESIGN_PRINCIPLES +
    BEST_PRACTICES
)
