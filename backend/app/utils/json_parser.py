"""
JSON Output Parser Module

This module provides utilities for parsing JSON outputs from Gemini API
using LangChain's output parsers for structured responses.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Type, TypeVar
from pydantic import BaseModel, ValidationError
from langchain_core.output_parsers import JsonOutputParser, PydanticOutputParser
from langchain_core.exceptions import OutputParserException

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class JSONParserError(Exception):
    """Base exception for JSON parsing errors."""
    pass


class JSONValidationError(JSONParserError):
    """Exception raised when JSON validation fails."""
    pass


class GeminiJSONParser:
    """
    Parser for extracting and validating JSON from Gemini responses.
    
    Features:
    - Parse JSON from raw text responses
    - Validate against Pydantic schemas
    - Handle malformed JSON gracefully
    - Extract JSON from markdown code blocks
    """
    
    def __init__(self, schema: Optional[Type[BaseModel]] = None):
        """
        Initialize the JSON parser.
        
        Args:
            schema: Optional Pydantic model for validation
        """
        self.schema = schema
        if schema:
            self.pydantic_parser = PydanticOutputParser(pydantic_object=schema)
        else:
            self.json_parser = JsonOutputParser()
        
        logger.debug(f"JSON parser initialized with schema: {schema.__name__ if schema else 'None'}")
    
    def parse(self, text: str) -> Dict[str, Any]:
        """
        Parse JSON from text response.
        
        Args:
            text: Raw text response from Gemini
            
        Returns:
            Dict containing parsed JSON
            
        Raises:
            JSONParserError: If parsing fails
        """
        try:
            # Try to extract JSON from text
            json_text = self._extract_json(text)
            
            # Parse JSON
            if self.schema:
                # Validate against Pydantic schema
                result = self.pydantic_parser.parse(json_text)
                return result.model_dump()
            else:
                # Parse as generic JSON
                return self.json_parser.parse(json_text)
        
        except ValidationError as e:
            logger.error(f"Pydantic validation error: {e}")
            raise JSONValidationError(f"JSON validation failed: {e}")
        except OutputParserException as e:
            logger.error(f"LangChain parser error: {e}")
            # Check if it's a validation error
            if "validation error" in str(e).lower():
                raise JSONValidationError(f"JSON validation failed: {e}")
            raise JSONParserError(f"Failed to parse JSON: {e}")
        except Exception as e:
            logger.error(f"Unexpected parsing error: {e}")
            raise JSONParserError(f"Unexpected error during parsing: {e}")
    
    def parse_to_model(self, text: str, model: Type[T]) -> T:
        """
        Parse JSON and convert to Pydantic model.
        
        Args:
            text: Raw text response from Gemini
            model: Pydantic model class
            
        Returns:
            Instance of the Pydantic model
            
        Raises:
            JSONValidationError: If validation fails
        """
        try:
            json_text = self._extract_json(text)
            parser = PydanticOutputParser(pydantic_object=model)
            result = parser.parse(json_text)
            logger.info(f"Successfully parsed to {model.__name__}")
            return result
        
        except ValidationError as e:
            logger.error(f"Validation error for {model.__name__}: {e}")
            raise JSONValidationError(f"Failed to validate against {model.__name__}: {e}")
        except Exception as e:
            logger.error(f"Error parsing to model: {e}")
            raise JSONParserError(f"Failed to parse to model: {e}")
    
    def _extract_json(self, text: str) -> str:
        """
        Extract JSON from text, handling various formats.
        
        Handles:
        - Pure JSON strings
        - JSON in markdown code blocks
        - JSON with surrounding text
        
        Args:
            text: Raw text containing JSON
            
        Returns:
            Extracted JSON string
            
        Raises:
            JSONParserError: If JSON cannot be extracted
        """
        text = text.strip()
        
        # Try to find JSON in markdown code blocks
        if "```json" in text:
            start_idx = text.find("```json") + 7
            end_idx = text.find("```", start_idx)
            if end_idx > start_idx:
                json_text = text[start_idx:end_idx].strip()
                logger.debug("Extracted JSON from markdown code block")
                return json_text
        
        # Try to find JSON in generic code blocks
        if "```" in text:
            start_idx = text.find("```") + 3
            end_idx = text.find("```", start_idx)
            if end_idx > start_idx:
                json_text = text[start_idx:end_idx].strip()
                # Check if it's valid JSON
                try:
                    json.loads(json_text)
                    logger.debug("Extracted JSON from code block")
                    return json_text
                except json.JSONDecodeError:
                    pass
        
        # Try to find JSON object/array boundaries
        for start_char, end_char in [("{", "}"), ("[", "]")]:
            start_idx = text.find(start_char)
            if start_idx != -1:
                # Find matching closing bracket
                end_idx = text.rfind(end_char)
                if end_idx > start_idx:
                    json_text = text[start_idx:end_idx + 1]
                    try:
                        json.loads(json_text)
                        logger.debug(f"Extracted JSON using {start_char}{end_char} boundaries")
                        return json_text
                    except json.JSONDecodeError:
                        pass
        
        # If all else fails, try parsing the whole text as JSON
        try:
            json.loads(text)
            logger.debug("Using entire text as JSON")
            return text
        except json.JSONDecodeError as e:
            logger.error(f"Failed to extract valid JSON from text: {e}")
            raise JSONParserError(f"Could not extract valid JSON from response: {e}")
    
    def get_format_instructions(self) -> str:
        """
        Get instructions for formatting JSON output.
        
        Returns:
            Format instructions string
        """
        if self.schema:
            return self.pydantic_parser.get_format_instructions()
        else:
            return (
                "Please respond with valid JSON. "
                "Wrap your response in a JSON object or array."
            )


def parse_json_response(
    text: str,
    schema: Optional[Type[BaseModel]] = None
) -> Dict[str, Any]:
    """
    Convenience function to parse JSON from Gemini response.
    
    Args:
        text: Raw text response
        schema: Optional Pydantic schema for validation
        
    Returns:
        Parsed JSON as dictionary
    """
    parser = GeminiJSONParser(schema=schema)
    return parser.parse(text)


def parse_json_list(text: str) -> List[Dict[str, Any]]:
    """
    Parse a JSON array from text response.
    
    Args:
        text: Raw text response containing JSON array
        
    Returns:
        List of dictionaries
        
    Raises:
        JSONParserError: If parsing fails or result is not a list
    """
    parser = GeminiJSONParser()
    result = parser.parse(text)
    
    if not isinstance(result, list):
        raise JSONParserError("Expected JSON array but got object")
    
    return result
