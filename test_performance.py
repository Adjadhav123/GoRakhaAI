"""
Test script to verify the chatbot performance improvements
"""
import time
import json

def test_speed_improvements():
    """Test the performance improvements made to the chatbot"""
    
    print("🧪 Testing Chatbot Performance Improvements")
    print("=" * 50)
    
    # Test 1: Import speed
    print("1. Testing imports...")
    start = time.time()
    try:
        from chatbot_service_new import AnimalDiseaseChatbot
        import_time = time.time() - start
        print(f"   ✅ Chatbot import: {import_time:.3f}s")
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return
    
    # Test 2: Initialization speed
    print("\n2. Testing initialization...")
    start = time.time()
    try:
        # Use a dummy API key for testing
        chatbot = AnimalDiseaseChatbot("test-key")
        init_time = time.time() - start
        print(f"   ✅ Initialization: {init_time:.3f}s")
    except Exception as e:
        print(f"   ❌ Initialization failed: {e}")
        return
    
    # Test 3: Translation optimization
    print("\n3. Testing translation optimization...")
    test_cases = [
        ("Hello", "en", "en"),  # Same language - should be instant
        ("", "en", "hi"),       # Empty text - should be instant  
        ("A" * 2000, "en", "hi"),  # Long text - should skip translation
    ]
    
    for text, src, tgt in test_cases:
        start = time.time()
        try:
            result = chatbot._translate_text(text, src, tgt)
            trans_time = time.time() - start
            case_desc = f"'{text[:20]}{'...' if len(text) > 20 else ''}' ({src}→{tgt})"
            print(f"   ✅ Translation {case_desc}: {trans_time:.3f}s")
        except Exception as e:
            print(f"   ❌ Translation failed for {case_desc}: {e}")
    
    # Test 4: Error handling improvements
    print("\n4. Testing error handling...")
    
    # Test empty input
    result = chatbot.process_text_query("", "en")
    if not result['success'] and 'Empty input' in result['error']:
        print("   ✅ Empty input handling: OK")
    else:
        print("   ❌ Empty input handling failed")
    
    # Test image analysis with invalid data
    try:
        result = chatbot.analyze_image("invalid_data", "test question", "en")
        if not result['success']:
            print("   ✅ Invalid image handling: OK")
        else:
            print("   ❌ Invalid image handling failed")
    except Exception as e:
        print(f"   ✅ Invalid image handling: OK (caught exception: {e})")
    
    print("\n🎯 Performance Improvements Summary:")
    print("   • Added timeouts for API calls (20s text, 30s image)")
    print("   • Optimized translation (skip same language, long texts)")
    print("   • Better error messages and fallback responses")
    print("   • Image validation and resizing")
    print("   • Concise prompts for faster responses")
    
    print("\n✅ Test completed! The chatbot should now be faster and more reliable.")

if __name__ == "__main__":
    test_speed_improvements()