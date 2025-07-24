"""
Configuration Checker for AI-Powered SQL Dashboard
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2
import openai

def check_env_file():
    """Check if .env file exists and has required variables"""
    print("🔍 Checking environment configuration...")
    
    if not os.path.exists('.env'):
        print("❌ .env file not found! Please create one from the template.")
        return False
    
    load_dotenv()
    
    required_vars = [
        'DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ Environment variables configured correctly")
    return True

def check_database_connection():
    """Check database connection"""
    print("🐘 Checking PostgreSQL connection...")
    
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        conn.close()
        print("✅ PostgreSQL connection successful")
        return True
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False

def check_openai_api():
    """Check OpenAI API key (optional)"""
    print("🤖 Checking OpenAI API configuration...")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️ OpenAI API key not found (optional - will use fallback methods)")
        return True
    
    try:
        openai.api_key = api_key
        # Simple API test
        response = openai.Model.list()
        print("✅ OpenAI API key is valid")
        return True
    except Exception as e:
        print(f"❌ OpenAI API key validation failed: {e}")
        return False

def check_python_packages():
    """Check if required Python packages are installed"""
    print("📦 Checking Python packages...")
    
    required_packages = [
        'streamlit', 'pandas', 'plotly', 'psycopg2', 
        'sqlalchemy', 'python-dotenv', 'fastapi', 'uvicorn'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are installed")
    return True

def check_file_structure():
    """Check if all required files exist"""
    print("📁 Checking file structure...")
    
    required_files = [
        'streamlit_app.py',
        'mcp_server.py', 
        'requirements.txt',
        'modules/__init__.py',
        'modules/postgres.py',
        'modules/query_processor.py',
        'modules/visualization.py',
        'modules/mcp_client.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files are present")
    return True

def main():
    """Run all configuration checks"""
    print("🚀 AI-Powered SQL Dashboard Configuration Checker")
    print("=" * 50)
    
    checks = [
        check_file_structure,
        check_python_packages,
        check_env_file,
        check_database_connection,
        check_openai_api
    ]
    
    all_passed = True
    
    for check in checks:
        try:
            if not check():
                all_passed = False
        except Exception as e:
            print(f"❌ Check failed with error: {e}")
            all_passed = False
        print()  # Add spacing between checks
    
    print("=" * 50)
    if all_passed:
        print("🎉 All checks passed! Your dashboard is ready to run.")
        print("\nTo start the dashboard:")
        print("1. python mcp_server.py (in one terminal)")
        print("2. streamlit run streamlit_app.py (in another terminal)")
    else:
        print("❌ Some checks failed. Please fix the issues above before running the dashboard.")
        sys.exit(1)

if __name__ == "__main__":
    main()