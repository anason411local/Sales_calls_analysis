"""
Test script to verify the Sales Variables Extractor setup
Run this to ensure all components are working correctly
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import pandas
        print("✓ pandas")
    except ImportError as e:
        print(f"✗ pandas: {e}")
        return False
    
    try:
        import google.generativeai
        print("✓ google.generativeai")
    except ImportError as e:
        print(f"✗ google.generativeai: {e}")
        return False
    
    try:
        from langgraph.graph import StateGraph
        print("✓ langgraph")
    except ImportError as e:
        print(f"✗ langgraph: {e}")
        return False
    
    try:
        from pydantic import BaseModel
        print("✓ pydantic")
    except ImportError as e:
        print(f"✗ pydantic: {e}")
        return False
    
    print("\nAll imports successful!\n")
    return True


def test_config():
    """Test configuration settings"""
    print("Testing configuration...")
    
    try:
        from config.settings import (
            GEMINI_API_KEY,
            INPUT_CSV,
            OUTPUT_CSV,
            SEASONALITY_CSV
        )
        
        if not GEMINI_API_KEY:
            print("✗ GEMINI_API_KEY not set in environment")
            return False
        else:
            print(f"✓ GEMINI_API_KEY configured (prefix: {GEMINI_API_KEY[:10]}...)")
        
        if not INPUT_CSV.exists():
            print(f"✗ Input CSV not found: {INPUT_CSV}")
            return False
        else:
            print(f"✓ Input CSV found: {INPUT_CSV}")
        
        if not SEASONALITY_CSV.exists():
            print(f"⚠ Seasonality CSV not found: {SEASONALITY_CSV} (optional)")
        else:
            print(f"✓ Seasonality CSV found: {SEASONALITY_CSV}")
        
        print(f"✓ Output will be saved to: {OUTPUT_CSV}")
        
        print("\nConfiguration valid!\n")
        return True
        
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False


def test_schemas():
    """Test Pydantic schemas"""
    print("Testing schemas...")
    
    try:
        from schemas.variable_schemas import (
            LGSExtractedVariables,
            OMCExtractedVariables,
            SalesVariablesExtraction
        )
        
        print("✓ LGSExtractedVariables schema")
        print("✓ OMCExtractedVariables schema")
        print("✓ SalesVariablesExtraction schema")
        
        print("\nSchemas loaded successfully!\n")
        return True
        
    except Exception as e:
        print(f"✗ Schema error: {e}")
        return False


def test_data_handler():
    """Test data handler"""
    print("Testing data handler...")
    
    try:
        from data.data_handler import DataHandler
        
        handler = DataHandler()
        print("✓ DataHandler initialized")
        
        # Try loading input data
        df = handler.load_input_data()
        print(f"✓ Input data loaded: {len(df)} rows")
        
        # Try loading seasonality data
        seasonality_df = handler.load_seasonality_data()
        if not seasonality_df.empty:
            print(f"✓ Seasonality data loaded: {len(seasonality_df)} categories")
        else:
            print("⚠ Seasonality data not loaded (optional)")
        
        # Test getting row data
        if len(df) > 0:
            row_data = handler.get_row_data(0)
            print(f"✓ Sample row data retrieved: Lead ID = {row_data.get('lead_id', 'N/A')}")
        
        print("\nData handler working correctly!\n")
        return True
        
    except Exception as e:
        print(f"✗ Data handler error: {e}")
        return False


def test_gemini_client():
    """Test Gemini client"""
    print("Testing Gemini client...")
    
    try:
        from llm.gemini_client import GeminiClient
        
        client = GeminiClient()
        print("✓ GeminiClient initialized")
        
        model_info = client.get_model_info()
        print(f"✓ Model: {model_info['model']}")
        print(f"✓ API Key Configured: {model_info['api_key_configured']}")
        
        # Test connection
        print("\nTesting API connection (this may take a few seconds)...")
        success = client.test_connection()
        
        if success:
            print("✓ API connection successful!")
        else:
            print("✗ API connection failed!")
            return False
        
        print("\nGemini client working correctly!\n")
        return True
        
    except Exception as e:
        print(f"✗ Gemini client error: {e}")
        return False


def test_graph():
    """Test LangGraph workflow"""
    print("Testing LangGraph workflow...")
    
    try:
        from graph.extraction_graph import create_extraction_graph
        
        graph = create_extraction_graph()
        print("✓ Extraction graph created")
        
        print("\nLangGraph workflow configured correctly!\n")
        return True
        
    except Exception as e:
        print(f"✗ Graph error: {e}")
        return False


def main():
    """Run all tests"""
    print("="*80)
    print("SALES VARIABLES EXTRACTOR - SETUP TEST")
    print("="*80)
    print()
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Schemas", test_schemas),
        ("Data Handler", test_data_handler),
        ("Gemini Client", test_gemini_client),
        ("LangGraph Workflow", test_graph)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n✗ {test_name} test failed with exception: {e}\n")
            results[test_name] = False
    
    # Summary
    print("="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name:.<50} {status}")
    
    print("="*80)
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n[SUCCESS] All tests passed! The agent is ready to use.")
        print("\nNext steps:")
        print("  1. Run: python main.py --test-connection")
        print("  2. Run: python main.py --run")
    else:
        print("\n[WARNING] Some tests failed. Please fix the issues before running the agent.")
        print("\nCommon fixes:")
        print("  - Install missing packages: pip install -r requirements.txt")
        print("  - Set GEMINI_API_KEY in .env file")
        print("  - Ensure input_data/mergeed_for_test.csv exists")
    
    print()


if __name__ == "__main__":
    main()

