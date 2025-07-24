"""
Natural Language to SQL Query Processor Module
"""

import os
import re
import openai
from typing import Dict, List, Optional, Tuple
import logging
import json

class QueryProcessor:
    """Process natural language queries and convert them to SQL"""
    
    def __init__(self):
        """Initialize the query processor"""
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Sample database schema for context
        self.schema_context = ""
        
    def set_database_schema(self, table_info: Dict[str, List[Dict]]):
        """Set database schema context for better SQL generation"""
        schema_parts = []
        
        for table_name, columns in table_info.items():
            column_definitions = []
            for col in columns:
                col_def = f"{col['column_name']} ({col['data_type']})"
                if col['is_nullable'] == 'NO':
                    col_def += " NOT NULL"
                column_definitions.append(col_def)
                
            schema_parts.append(f"Table: {table_name}\nColumns: {', '.join(column_definitions)}")
            
        self.schema_context = "\n\n".join(schema_parts)
        self.logger.info("Database schema context updated")
        
    def clean_sql_query(self, sql_query: str) -> str:
        """Clean and validate SQL query"""
        # Remove markdown code blocks if present
        sql_query = re.sub(r'```sql\n?', '', sql_query)
        sql_query = re.sub(r'```\n?', '', sql_query)
        
        # Remove extra whitespace
        sql_query = ' '.join(sql_query.split())
        
        # Basic SQL injection prevention (simple checks)
        dangerous_keywords = [
            'DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE', 'TRUNCATE'
        ]
        
        sql_upper = sql_query.upper()
        for keyword in dangerous_keywords:
            if keyword in sql_upper and not sql_upper.startswith('SELECT'):
                raise ValueError(f"Potentially dangerous SQL operation detected: {keyword}")
                
        return sql_query.strip()
        
    def natural_language_to_sql(self, nl_query: str) -> Tuple[str, str]:
        """Convert natural language query to SQL"""
        try:
            # Fallback patterns for common queries when OpenAI is not available
            fallback_patterns = {
                r'(?i).*all sales.*': "SELECT * FROM sales ORDER BY sale_date DESC",
                r'(?i).*sales by category.*': "SELECT category, SUM(price * quantity) as total_sales FROM sales GROUP BY category ORDER BY total_sales DESC",
                r'(?i).*total sales.*': "SELECT SUM(price * quantity) as total_sales FROM sales",
                r'(?i).*customers.*': "SELECT * FROM customers ORDER BY registration_date DESC",
                r'(?i).*average age.*': "SELECT AVG(age) as average_age FROM customers",
                r'(?i).*sales by region.*': "SELECT region, SUM(price * quantity) as total_sales FROM sales GROUP BY region ORDER BY total_sales DESC",
                r'(?i).*top.*products.*': "SELECT product_name, SUM(quantity) as total_sold FROM sales GROUP BY product_name ORDER BY total_sold DESC LIMIT 10",
                r'(?i).*recent sales.*': "SELECT * FROM sales ORDER BY sale_date DESC LIMIT 10",
                r'(?i).*revenue.*': "SELECT SUM(price * quantity) as total_revenue FROM sales"
            }
            
            # Try pattern matching first
            for pattern, sql in fallback_patterns.items():
                if re.match(pattern, nl_query):
                    return sql, "Pattern matching"
                    
            # If OpenAI API key is available, use GPT
            if self.openai_api_key:
                return self._openai_to_sql(nl_query)
            else:
                return self._rule_based_to_sql(nl_query)
                
        except Exception as e:
            self.logger.error(f"Failed to convert natural language to SQL: {e}")
            return "SELECT 1 as error", f"Error: {str(e)}"
            
    def _openai_to_sql(self, nl_query: str) -> Tuple[str, str]:
        """Use OpenAI GPT to convert natural language to SQL"""
        try:
            system_prompt = f"""You are an expert SQL query generator. Convert natural language questions to PostgreSQL queries.

Database Schema:
{self.schema_context}

Rules:
1. Only generate SELECT queries (no INSERT, UPDATE, DELETE, DROP)
2. Use proper PostgreSQL syntax
3. Include appropriate JOINs when needed
4. Use meaningful aliases
5. Add ORDER BY clauses when logical
6. Return only the SQL query, no explanation
7. Ensure queries are safe and don't modify data

Examples:
- "Show all sales" → SELECT * FROM sales ORDER BY sale_date DESC
- "Total sales by category" → SELECT category, SUM(price * quantity) as total_sales FROM sales GROUP BY category ORDER BY total_sales DESC
"""

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": nl_query}
                ],
                max_tokens=200,
                temperature=0.1
            )
            
            sql_query = response.choices[0].message.content.strip()
            cleaned_sql = self.clean_sql_query(sql_query)
            
            return cleaned_sql, "OpenAI GPT"
            
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            return self._rule_based_to_sql(nl_query)
            
    def _rule_based_to_sql(self, nl_query: str) -> Tuple[str, str]:
        """Rule-based natural language to SQL conversion (fallback)"""
        nl_lower = nl_query.lower()
        
        # Define more comprehensive patterns
        patterns = [
            # Sales queries
            (r'(?i).*(all|show|display).*sales', "SELECT * FROM sales ORDER BY sale_date DESC"),
            (r'(?i).*total.*sales.*category', "SELECT category, SUM(price * quantity) as total_sales FROM sales GROUP BY category ORDER BY total_sales DESC"),
            (r'(?i).*sales.*region', "SELECT region, SUM(price * quantity) as total_sales FROM sales GROUP BY region ORDER BY total_sales DESC"),
            (r'(?i).*total.*sales', "SELECT SUM(price * quantity) as total_sales FROM sales"),
            (r'(?i).*revenue', "SELECT SUM(price * quantity) as total_revenue FROM sales"),
            (r'(?i).*(top|best).*products', "SELECT product_name, SUM(quantity) as total_sold, SUM(price * quantity) as revenue FROM sales GROUP BY product_name ORDER BY revenue DESC LIMIT 10"),
            (r'(?i).*recent.*sales', "SELECT * FROM sales ORDER BY sale_date DESC LIMIT 10"),
            
            # Customer queries  
            (r'(?i).*(all|show|display).*customers', "SELECT * FROM customers ORDER BY registration_date DESC"),
            (r'(?i).*average.*age', "SELECT AVG(age) as average_age FROM customers"),
            (r'(?i).*customers.*city', "SELECT city, COUNT(*) as customer_count FROM customers GROUP BY city ORDER BY customer_count DESC"),
            
            # General queries
            (r'(?i).*count.*sales', "SELECT COUNT(*) as total_sales_count FROM sales"),
            (r'(?i).*count.*customers', "SELECT COUNT(*) as total_customers FROM customers"),
        ]
        
        for pattern, sql in patterns:
            if re.search(pattern, nl_query):
                return sql, "Rule-based matching"
                
        # Default fallback
        return "SELECT * FROM sales LIMIT 10", "Default fallback"
        
    def validate_sql(self, sql_query: str) -> bool:
        """Basic SQL validation"""
        try:
            cleaned_sql = self.clean_sql_query(sql_query)
            
            # Must start with SELECT
            if not cleaned_sql.upper().startswith('SELECT'):
                return False
                
            # Basic syntax check
            if cleaned_sql.count('(') != cleaned_sql.count(')'):
                return False
                
            return True
            
        except Exception:
            return False
            
    def get_query_explanation(self, sql_query: str) -> str:
        """Generate explanation for the SQL query"""
        try:
            explanations = {
                'SELECT * FROM sales': "Retrieving all sales records",
                'SUM(price * quantity)': "Calculating total revenue (price × quantity)",
                'GROUP BY': "Grouping results by specified column(s)",
                'ORDER BY': "Sorting results by specified column(s)",
                'COUNT(*)': "Counting total number of records",
                'AVG(': "Calculating average value",
                'LIMIT': "Limiting number of results returned"
            }
            
            explanation_parts = []
            sql_upper = sql_query.upper()
            
            for pattern, explanation in explanations.items():
                if pattern.upper() in sql_upper:
                    explanation_parts.append(explanation)
                    
            if explanation_parts:
                return "This query is: " + ", ".join(explanation_parts)
            else:
                return "This query retrieves data from the database"
                
        except Exception:
            return "Query explanation not available"