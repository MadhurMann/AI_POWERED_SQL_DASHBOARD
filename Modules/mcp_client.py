"""
MCP (Model Context Protocol) Client Module
"""

import os
import json
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
import logging

class MCPClient:
    """Client for communicating with MCP server"""
    
    def __init__(self):
        """Initialize MCP client"""
        self.host = os.getenv('MCP_SERVER_HOST', 'localhost')
        self.port = os.getenv('MCP_SERVER_PORT', '8000')
        self.base_url = f"http://{self.host}:{self.port}"
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    async def send_request(self, endpoint: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send request to MCP server"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/{endpoint}"
                
                async with session.post(
                    url,
                    json=data,
                    headers={'Content-Type': 'application/json'},
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        return result
                    else:
                        self.logger.error(f"MCP server error: {response.status}")
                        return None
                        
        except asyncio.TimeoutError:
            self.logger.error("MCP server request timeout")
            return None
        except Exception as e:
            self.logger.error(f"MCP client error: {e}")
            return None
            
    async def process_nl_query(self, query: str, schema_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process natural language query through MCP server"""
        try:
            request_data = {
                "query": query,
                "schema": schema_info,
                "task": "nl_to_sql"
            }
            
            result = await self.send_request("process", request_data)
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to process NL query: {e}")
            return None
            
    async def validate_sql(self, sql_query: str) -> bool:
        """Validate SQL query through MCP server"""
        try:
            request_data = {
                "sql": sql_query,
                "task": "validate_sql"
            }
            
            result = await self.send_request("validate", request_data)
            return result.get("valid", False) if result else False
            
        except Exception as e:
            self.logger.error(f"Failed to validate SQL: {e}")
            return False
            
    async def get_query_suggestions(self, context: str) -> List[str]:
        """Get query suggestions from MCP server"""
        try:
            request_data = {
                "context": context,
                "task": "suggest_queries"
            }
            
            result = await self.send_request("suggest", request_data)
            return result.get("suggestions", []) if result else []
            
        except Exception as e:
            self.logger.error(f"Failed to get suggestions: {e}")
            return []
            
    def sync_process_nl_query(self, query: str, schema_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Synchronous wrapper for process_nl_query"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.process_nl_query(query, schema_info))
            loop.close()
            return result
        except Exception as e:
            self.logger.error(f"Sync process failed: {e}")
            return None