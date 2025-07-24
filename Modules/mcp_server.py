"""
MCP Server for AI-Powered SQL Dashboard
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import uvicorn
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import your modules
from modules.query_processor import QueryProcessor

app = FastAPI(title="AI SQL Dashboard MCP Server", version="1.0.0")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize query processor
query_processor = QueryProcessor()

class QueryRequest(BaseModel):
    query: str
    schema: Dict[str, Any]
    task: str

class ValidationRequest(BaseModel):
    sql: str
    task: str

class SuggestionRequest(BaseModel):
    context: str
    task: str

@app.on_startup
async def startup_event():
    """Initialize server components"""
    logger.info("MCP Server starting up...")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "AI SQL Dashboard MCP Server is running", "status": "healthy"}

@app.post("/process")
async def process_query(request: QueryRequest):
    """Process natural language query and convert to SQL"""
    try:
        if request.task != "nl_to_sql":
            raise HTTPException(status_code=400, detail="Invalid task type")
            
        # Set database schema context
        query_processor.set_database_schema(request.schema)
        
        # Convert natural language to SQL
        sql_query, method = query_processor.natural_language_to_sql(request.query)
        
        # Validate the generated SQL
        is_valid = query_processor.validate_sql(sql_query)
        
        # Get explanation
        explanation = query_processor.get_query_explanation(sql_query)
        
        return {
            "sql": sql_query,
            "method": method,
            "valid": is_valid,
            "explanation": explanation,
            "original_query": request.query
        }
        
    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/validate")
async def validate_sql(request: ValidationRequest):
    """Validate SQL query"""
    try:
        if request.task != "validate_sql":
            raise HTTPException(status_code=400, detail="Invalid task type")
            
        is_valid = query_processor.validate_sql(request.sql)
        
        return {
            "valid": is_valid,
            "sql": request.sql
        }
        
    except Exception as e:
        logger.error(f"SQL validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/suggest")
async def get_suggestions(request: SuggestionRequest):
    """Get query suggestions based on context"""
    try:
        if request.task != "suggest_queries":
            raise HTTPException(status_code=400, detail="Invalid task type")
            
        # Generate suggestions based on context
        suggestions = [
            "Show me all sales data",
            "What are the total sales by category?",
            "Show me sales trends over time",
            "Which region has the highest sales?",
            "Show me customer demographics",
            "What's the average age of customers?",
            "Show me top selling products",
            "What are the sales by region?",
            "Show me recent sales transactions",
            "What's the total revenue this month?"
        ]
        
        return {
            "suggestions": suggestions,
            "context": request.context
        }
        
    except Exception as e:
        logger.error(f"Suggestion generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "server": "MCP Server",
        "version": "1.0.0",
        "components": {
            "query_processor": "ready",
            "database": "available"
        }
    }

if __name__ == "__main__":
    port = int(os.getenv('MCP_SERVER_PORT', '8000'))
    uvicorn.run(
        "mcp_server:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )