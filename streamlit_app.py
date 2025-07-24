"""
AI-Powered SQL Dashboard - Streamlit Application
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from dotenv import load_dotenv
import os
import asyncio
from datetime import datetime
import time

# Load environment variables
load_dotenv()

# Import custom modules
from modules import PostgresDB, QueryProcessor, DataVisualizer, MCPClient

# Page configuration
st.set_page_config(
    page_title="AI-Powered SQL Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #666;
        text-align: center;
        margin-bottom: 3rem;
    }
    .metric-container {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
        color: #155724;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
        color: #721c24;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
        color: #0c5460;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'db_connected' not in st.session_state:
    st.session_state.db_connected = False
if 'query_history' not in st.session_state:
    st.session_state.query_history = []
if 'current_data' not in st.session_state:
    st.session_state.current_data = None

# Initialize components
@st.cache_resource
def init_components():
    """Initialize database, query processor, visualizer, and MCP client"""
    db = PostgresDB()
    processor = QueryProcessor()
    visualizer = DataVisualizer()
    mcp_client = MCPClient()
    return db, processor, visualizer, mcp_client

def main():
    """Main application function"""
    
    # Header
    st.markdown('<h1 class="main-header">🤖 AI-Powered SQL Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Transform natural language into powerful database insights</p>', unsafe_allow_html=True)
    
    # Initialize components
    db, processor, visualizer, mcp_client = init_components()
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Dashboard Controls")
        
        # Database Connection Section
        st.subheader("📊 Database Connection")
        
        if st.button("🔗 Connect to Database"):
            with st.spinner("Connecting to database..."):
                if db.connect():
                    st.session_state.db_connected = True
                    st.success("✅ Connected to PostgreSQL!")
                    
                    # Create sample data if needed
                    if st.checkbox("Create sample data"):
                        with st.spinner("Creating sample data..."):
                            if db.create_sample_data():
                                st.success("✅ Sample data created!")
                else:
                    st.error("❌ Failed to connect to database")
        
        if st.session_state.db_connected:
            st.success("🟢 Database Connected")
            
            # Test connection
            if st.button("🧪 Test Connection"):
                if db.test_connection():
                    st.success("✅ Connection is healthy!")
                else:
                    st.error("❌ Connection failed!")
        else:
            st.warning("🔴 Database Disconnected")
            
        st.divider()
        
        # Query History
        st.subheader("📚 Query History")
        if st.session_state.query_history:
            for i, (timestamp, query, sql) in enumerate(reversed(st.session_state.query_history[-5:])):
                with st.expander(f"Query {len(st.session_state.query_history)-i}"):
                    st.write(f"**Time:** {timestamp}")
                    st.write(f"**Query:** {query}")
                    st.code(sql, language="sql")
        else:
            st.info("No queries yet")
            
        # Clear history
        if st.button("🗑️ Clear History"):
            st.session_state.query_history = []
            st.rerun()
    
    # Main content area
    if not st.session_state.db_connected:
        st.warning("⚠️ Please connect to the database first using the sidebar.")
        
        # Show connection instructions
        st.subheader("📋 Setup Instructions")
        st.markdown("""
        1. **Install PostgreSQL** and create a database
        2. **Update your .env file** with database credentials
        3. **Click 'Connect to Database'** in the sidebar
        4. **Create sample data** (optional) for testing
        5. **Start querying** with natural language!
        """)
        
        # Show sample queries
        st.subheader("💡 Sample Queries to Try")
        sample_queries = [
            "Show me all sales data",
            "What are the total sales by category?",
            "Which region has the highest sales?",
            "Show me customer demographics",
            "What's the average age of customers?",
            "Show me top selling products"
        ]
        
        for query in sample_queries:
            st.code(query)
            
        return
    
    # Database Schema Information
    with st.expander("📋 Database Schema", expanded=False):
        table_info = db.get_table_info()
        if table_info:
            for table_name, columns in table_info.items():
                st.subheader(f"Table: {table_name}")
                df_schema = pd.DataFrame(columns)
                st.dataframe(df_schema, use_container_width=True)
        else:
            st.info("No tables found or unable to retrieve schema")
    
    # Query Interface
    st.header("🎯 Natural Language Query Interface")
    
    # Query suggestions
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Text input for natural language query
        user_query = st.text_area(
            "Enter your question in natural language:",
            placeholder="e.g., Show me total sales by category",
            height=100
        )
    
    with col2:
        st.subheader("💡 Quick Suggestions")
        suggestions = db.get_query_suggestions()
        
        for suggestion in suggestions[:5]:
            if st.button(suggestion, key=f"suggestion_{suggestion[:20]}"):
                user_query = suggestion
                st.rerun()
    
    # Query processing
    if st.button("🚀 Execute Query", type="primary"):
        if user_query.strip():
            with st.spinner("Processing your query..."):
                # Get table info for context
                table_info = db.get_table_info()
                processor.set_database_schema(table_info)
                
                # Convert natural language to SQL
                sql_query, method = processor.natural_language_to_sql(user_query)
                
                # Display the generated SQL
                st.subheader("🔍 Generated SQL Query")
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.code(sql_query, language="sql")
                    
                with col2:
                    st.info(f"**Method:** {method}")
                    explanation = processor.get_query_explanation(sql_query)
                    st.info(f"**Explanation:** {explanation}")
                
                # Execute the SQL query
                try:
                    result_df = db.execute_query(sql_query)
                    
                    if result_df is not None and not result_df.empty:
                        st.session_state.current_data = result_df
                        
                        # Add to query history
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        st.session_state.query_history.append((timestamp, user_query, sql_query))
                        
                        # Display results
                        st.header("📊 Query Results")
                        
                        # Show basic stats
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Rows Returned", len(result_df))
                        with col2:
                            st.metric("Columns", len(result_df.columns))
                        with col3:
                            execution_time = "< 1s"  # Placeholder
                            st.metric("Execution Time", execution_time)
                        
                        # Visualization section
                        st.subheader("📈 Data Visualization")
                        
                        # Auto-generate visualization
                        fig = visualizer.auto_visualize(result_df, user_query)
                        
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("Unable to create automatic visualization")
                        
                        # Custom visualization options
                        st.subheader("🎨 Custom Visualization")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            chart_types = visualizer.suggest_visualization_type(result_df)
                            selected_chart = st.selectbox("Chart Type", chart_types)
                        
                        with col2:
                            x_column = st.selectbox("X-axis", [""] + list(result_df.columns))
                        
                        with col3:
                            y_column = st.selectbox("Y-axis", [""] + list(result_df.columns))
                        
                        if st.button("Create Custom Chart"):
                            if selected_chart and (x_column or y_column):
                                custom_fig = visualizer.create_custom_visualization(
                                    result_df, selected_chart, x_column, y_column
                                )
                                if custom_fig:
                                    st.plotly_chart(custom_fig, use_container_width=True)
                        
                        # Raw data table
                        with st.expander("📋 Raw Data", expanded=False):
                            st.dataframe(result_df, use_container_width=True)
                            
                            # Download options
                            csv = result_df.to_csv(index=False)
                            st.download_button(
                                label="📥 Download as CSV",
                                data=csv,
                                file_name=f"query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )
                    
                    else:
                        st.warning("⚠️ Query executed successfully but returned no results")
                        
                except Exception as e:
                    st.error(f"❌ Query execution failed: {str(e)}")
                    
        else:
            st.warning("⚠️ Please enter a query first!")
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>🤖 AI-Powered SQL Dashboard | Built with Streamlit, PostgreSQL, and MCP</p>
        <p>Transform your data questions into actionable insights!</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()