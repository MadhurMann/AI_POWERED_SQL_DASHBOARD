"""
Database Management Utility
"""

import sys
import os
from dotenv import load_dotenv
from modules.postgres import PostgresDB
import argparse

# Load environment variables
load_dotenv()

def main():
    parser = argparse.ArgumentParser(description='Database Management Utility')
    parser.add_argument('--action', choices=['test', 'create-sample', 'schema', 'clear'], 
                       required=True, help='Action to perform')
    parser.add_argument('--table', help='Specific table name (for clear action)')
    
    args = parser.parse_args()
    
    # Initialize database
    db = PostgresDB()
    
    if not db.connect():
        print("❌ Failed to connect to database")
        sys.exit(1)
    
    print("✅ Connected to database successfully")
    
    if args.action == 'test':
        if db.test_connection():
            print("✅ Database connection test passed")
        else:
            print("❌ Database connection test failed")
            
    elif args.action == 'create-sample':
        print("🏗️ Creating sample data...")
        if db.create_sample_data():
            print("✅ Sample data created successfully")
        else:
            print("❌ Failed to create sample data")
            
    elif args.action == 'schema':
        print("📋 Database Schema:")
        table_info = db.get_table_info()
        
        if table_info:
            for table_name, columns in table_info.items():
                print(f"\n🏷️ Table: {table_name}")
                print("-" * 50)
                for col in columns:
                    nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                    default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
                    print(f"  {col['column_name']:<20} {col['data_type']:<15} {nullable}{default}")
        else:
            print("No tables found")
            
    elif args.action == 'clear':
        table_name = args.table
        if table_name:
            confirm = input(f"⚠️ Are you sure you want to clear table '{table_name}'? (yes/no): ")
            if confirm.lower() == 'yes':
                try:
                    db.execute_query(f"DELETE FROM {table_name}")
                    print(f"✅ Table '{table_name}' cleared successfully")
                except Exception as e:
                    print(f"❌ Failed to clear table: {e}")
        else:
            print("❌ Please specify a table name with --table")
    
    db.disconnect()

if __name__ == "__main__":
    main()