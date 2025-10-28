


from asyncio.log import logger
from typing import Any, Dict
from .base_chain import BaseDesignChain
from app.prompts.role_playing import RolePlayingPrompts
from langchain_core.prompts import ChatPromptTemplate


class GetContextChain(BaseDesignChain):
    """Chain to get context for a given query."""

    def _create_prompt(self):
        
        system_prompt = RolePlayingPrompts.SYSTEM_ARCHITECT

        context_prompt = """You are an expert system architect. Given the following query, provide relevant context information that would help in designing the system.
        include system context, containers, components, and code level details as applicable.

        if query is not relevant to system architecture, respond with empty context.


        Query: {query}
        Current Context: {current_context}
        Output should be in json format with keys:

        {{
            "name": "system context name",
            "description": "system context description",
            "childrens": [
                {{
                    "name": "container name",
                    "description": "container description",
                    "technologies": ["tech1", "tech2"],
                    "children": [
                        {{
                            "name": "component name",
                            "description": "component description",
                            "responsibilities": ["responsibility1", "responsibility2"]
                            "children": [
                                {{
                                    "name": "Code name",
                                    "description": "code description",
                                    "responsibilities": ["responsibility1", "responsibility2"],
                                }}
                            ],
                        }}
                    ],
                }}
            ],
        }}
        """

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("user", context_prompt),
            ]
        )
        return prompt
    

    def _build_chain(self):
        """ Build the chain for getting context. """

        prompt = self._create_prompt()
        
        chain = (
            prompt
            | self.llm
            | self.output_parser
        )

        return chain
    

    async def get_context(self, query: str, current_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get context for a given query.

        Args:
            query: The query string to get context for.
        Returns:
            Dictionary containing the context information.
        """
        logger.info(f"Getting context for query: {query}")
        
        result = await self.ainvoke({
            "query": query,
            "current_context": current_context
        })
        
        return result