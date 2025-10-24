"""
MongoDB Exception Classes

This module defines custom exception classes for MongoDB operations.
These exceptions provide more specific error handling for database operations.
"""

from typing import Optional, Any


class MongoDBException(Exception):
    """Base exception for all MongoDB-related errors."""
    
    def __init__(self, message: str, details: Optional[Any] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)
    
    def __str__(self):
        if self.details:
            return f"{self.message} - Details: {self.details}"
        return self.message


class DatabaseConnectionError(MongoDBException):
    """Raised when unable to connect to MongoDB."""
    
    def __init__(self, message: str = "Failed to connect to MongoDB", details: Optional[Any] = None):
        super().__init__(message, details)


class DatabaseOperationError(MongoDBException):
    """Raised when a database operation fails."""
    
    def __init__(self, operation: str, details: Optional[Any] = None):
        message = f"Database operation '{operation}' failed"
        super().__init__(message, details)


class DocumentNotFoundError(MongoDBException):
    """Raised when a requested document is not found."""
    
    def __init__(self, collection: str, identifier: str, details: Optional[Any] = None):
        message = f"Document not found in collection '{collection}' with identifier: {identifier}"
        super().__init__(message, details)


class DuplicateKeyError(MongoDBException):
    """Raised when attempting to insert a document with a duplicate key."""
    
    def __init__(self, collection: str, key: str, value: Any, details: Optional[Any] = None):
        message = f"Duplicate key error in collection '{collection}': {key}='{value}'"
        super().__init__(message, details)


class DocumentAlreadyExistsError(MongoDBException):
    """Raised when attempting to create a document that already exists."""
    
    def __init__(self, collection: str, identifier: str, details: Optional[Any] = None):
        message = f"Document already exists in collection '{collection}' with identifier: {identifier}"
        super().__init__(message, details)


class ValidationError(MongoDBException):
    """Raised when document validation fails."""
    
    def __init__(self, message: str = "Document validation failed", details: Optional[Any] = None):
        super().__init__(message, details)


class InvalidObjectIdError(MongoDBException):
    """Raised when an invalid ObjectId is provided."""
    
    def __init__(self, object_id: str, details: Optional[Any] = None):
        message = f"Invalid ObjectId: {object_id}"
        super().__init__(message, details)


class CollectionNotFoundError(MongoDBException):
    """Raised when a requested collection does not exist."""
    
    def __init__(self, collection_name: str, details: Optional[Any] = None):
        message = f"Collection not found: {collection_name}"
        super().__init__(message, details)


class TransactionError(MongoDBException):
    """Raised when a transaction operation fails."""
    
    def __init__(self, message: str = "Transaction failed", details: Optional[Any] = None):
        super().__init__(message, details)


class QueryError(MongoDBException):
    """Raised when a query operation fails."""
    
    def __init__(self, message: str = "Query operation failed", details: Optional[Any] = None):
        super().__init__(message, details)


class IndexCreationError(MongoDBException):
    """Raised when index creation fails."""
    
    def __init__(self, collection: str, index_name: str, details: Optional[Any] = None):
        message = f"Failed to create index '{index_name}' on collection '{collection}'"
        super().__init__(message, details)


class BulkOperationError(MongoDBException):
    """Raised when a bulk operation partially or completely fails."""
    
    def __init__(
        self,
        operation: str,
        success_count: int,
        failure_count: int,
        details: Optional[Any] = None
    ):
        message = (
            f"Bulk {operation} completed with {success_count} successes "
            f"and {failure_count} failures"
        )
        super().__init__(message, details)


class UnauthorizedOperationError(MongoDBException):
    """Raised when attempting an operation without proper authorization."""
    
    def __init__(self, operation: str, details: Optional[Any] = None):
        message = f"Unauthorized to perform operation: {operation}"
        super().__init__(message, details)


class ConfigurationError(MongoDBException):
    """Raised when MongoDB configuration is invalid."""
    
    def __init__(self, message: str = "Invalid MongoDB configuration", details: Optional[Any] = None):
        super().__init__(message, details)
