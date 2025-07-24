import os
import pandas as pd
import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, List, Optional, Tuple
import logging

class PostgresDB:
    """PostgreSQL database connection and operations handler"""
    
    def __init__(self):
        """Initialize database connection"""
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = os.getenv('DB_PORT', '5432')
        self.database = os.getenv('DB_NAME', 'ai_dashboard')
        self.user = os.getenv('DB_USER', 'dashboard_user')
        self.password = os.getenv('DB_PASSWORD', '')
        
        self.connection_string = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        self.engine = None
        self.connection = None
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def connect(self) -> bool:
        """Establish database connection"""
        try:
            self.engine = create_engine(self.connection_string)
            self.connection = self.engine.connect()
            self.logger.info("Successfully connected to PostgreSQL database")
            return True
        except SQLAlchemyError as e:
            self.logger.error(f"Failed to connect to database: {e}")
            return False
            
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.logger.info("Database connection closed")
            
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            if not self.connection:
                return self.connect()
            
            result = self.connection.execute(text("SELECT 1"))
            return result.fetchone()[0] == 1
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
            
    def execute_query(self, query: str) -> Optional[pd.DataFrame]:
        """Execute SQL query and return results as pandas DataFrame"""
        try:
            if not self.connection:
                if not self.connect():
                    return None
                    
            # Clean and validate query
            query = query.strip()
            if not query:
                raise ValueError("Empty query provided")
                
            # Execute query
            result = pd.read_sql(query, self.connection)
            self.logger.info(f"Query executed successfully. Returned {len(result)} rows")
            return result
            
        except Exception as e:
            self.logger.error(f"Query execution failed: {e}")
            return None
            
    def get_table_info(self) -> Dict[str, List[Dict]]:
        """Get information about all tables in the database"""
        try:
            # Get all table names
            tables_query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            """
            
            tables_df = self.execute_query(tables_query)
            if tables_df is None:
                return {}
                
            table_info = {}
            
            for table_name in tables_df['table_name']:
                # Get column information for each table
                columns_query = f"""
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
                """
                
                columns_df = self.execute_query(columns_query)
                if columns_df is not None:
                    table_info[table_name] = columns_df.to_dict('records')
                    
            return table_info
            
        except Exception as e:
            self.logger.error(f"Failed to get table info: {e}")
            return {}
            
    def create_sample_data(self):
        """Create sample tables and data for demonstration"""
        try:
            sample_queries = [
                """
                CREATE TABLE IF NOT EXISTS sales (
                    id SERIAL PRIMARY KEY,
                    product_name VARCHAR(100),
                    category VARCHAR(50),
                    price DECIMAL(10,2),
                    quantity INTEGER,
                    sale_date DATE,
                    region VARCHAR(50)
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS customers (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100),
                    email VARCHAR(100),
                    age INTEGER,
                    city VARCHAR(50),
                    registration_date DATE
                )
                """,
                """
                INSERT INTO sales (product_name, category, price, quantity, sale_date, region)
                VALUES 
                    ('Laptop', 'Electronics', 999.99, 2, '2024-01-15', 'North'),
                    ('Phone', 'Electronics', 699.99, 5, '2024-01-16', 'South'),
                    ('Desk Chair', 'Furniture', 299.99, 1, '2024-01-17', 'East'),
                    ('Monitor', 'Electronics', 399.99, 3, '2024-01-18', 'West'),
                    ('Table', 'Furniture', 499.99, 2, '2024-01-19', 'North')
                ON CONFLICT DO NOTHING
                """,
                """
                INSERT INTO customers (name, email, age, city, registration_date)
                VALUES 
                    ('John Doe', 'john@email.com', 28, 'New York', '2024-01-10'),
                    ('Jane Smith', 'jane@email.com', 34, 'Los Angeles', '2024-01-11'),
                    ('Bob Johnson', 'bob@email.com', 45, 'Chicago', '2024-01-12'),
                    ('Alice Brown', 'alice@email.com', 29, 'Houston', '2024-01-13'),
                    ('Charlie Wilson', 'charlie@email.com', 52, 'Phoenix', '2024-01-14')
                ON CONFLICT DO NOTHING
                """
            ]
            
            for query in sample_queries:
                self.connection.execute(text(query))
                self.connection.commit()
                
            self.logger.info("Sample data created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create sample data: {e}")
            return False
            
    def get_query_suggestions(self) -> List[str]:
        """Get sample query suggestions based on available tables"""
        suggestions = [
            "Show me all sales data",
            "What are the total sales by category?",
            "Show me sales trends by month",
            "Which region has the highest sales?",
            "Show me customer demographics",
            "What's the average age of customers?",
            "Show me top selling products",
            "What are the sales by region?",
            "Show me recent sales",
            "What's the total revenue?"
        ]
        return suggestions