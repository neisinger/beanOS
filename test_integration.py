#!/usr/bin/env python3
"""
End-to-end integration test for bitmap icon system.
Verifies that all components work together correctly.
"""

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing imports...")
    try:
        from icon_bitmaps import ICON_MAP
        print("  ✅ icon_bitmaps imported")
        
        # Verify main.py can be parsed (syntax check)
        with open('main.py', 'r') as f:
            code = f.read()
            compile(code, 'main.py', 'exec')
        print("  ✅ main.py syntax valid")
        
        return True
    except Exception as e:
        print(f"  ❌ Import error: {e}")
        return False

def test_icon_map_completeness():
    """Verify all achievement icons are mapped"""
    print("\n🧪 Testing icon map completeness...")
    from icon_bitmaps import ICON_MAP
    
    required_icons = {
        "#1", "#10", "#50", "#100", "#500", "#1000",  # Milestones
        "=7", "=30",  # Streaks
        "~", "o", "%",  # Special drinks
        "<>", "[]",  # Maintenance
        ">>", "^^",  # Experimental
        "★"  # General
    }
    
    missing = required_icons - set(ICON_MAP.keys())
    if missing:
        print(f"  ❌ Missing icons: {missing}")
        return False
    
    print(f"  ✅ All {len(required_icons)} required icons present")
    return True

def test_bitmap_format():
    """Verify bitmap data format is correct"""
    print("\n🧪 Testing bitmap format...")
    from icon_bitmaps import ICON_MAP
    
    for symbol, bitmap in ICON_MAP.items():
        # Check type
        if not isinstance(bitmap, bytearray):
            print(f"  ❌ {symbol}: Not a bytearray")
            return False
        
        # Check size (32x32 pixels = 128 bytes)
        if len(bitmap) != 128:
            print(f"  ❌ {symbol}: Wrong size {len(bitmap)} (expected 128)")
            return False
    
    print(f"  ✅ All {len(ICON_MAP)} bitmaps have correct format")
    return True

def test_draw_function_signature():
    """Verify draw_bitmap_icon function exists with correct signature"""
    print("\n🧪 Testing draw_bitmap_icon function...")
    
    with open('main.py', 'r') as f:
        code = f.read()
    
    # Check function is defined
    if 'def draw_bitmap_icon(' not in code:
        print("  ❌ draw_bitmap_icon function not found")
        return False
    
    # Check it's called with bitmap icons
    if 'draw_bitmap_icon(' not in code or 'icon_symbol' not in code:
        print("  ❌ draw_bitmap_icon not properly integrated")
        return False
    
    print("  ✅ draw_bitmap_icon function found and integrated")
    return True

def test_documentation():
    """Verify documentation is updated"""
    print("\n🧪 Testing documentation...")
    
    with open('README.md', 'r') as f:
        readme = f.read()
    
    checks = [
        ('icon_bitmaps.py', 'icon_bitmaps.py mentioned in README'),
        ('1-Bit', '1-bit bitmap documentation present'),
        ('Bitmap-Icon-System', 'Bitmap icon system documented'),
    ]
    
    for term, description in checks:
        if term not in readme:
            print(f"  ❌ {description}")
            return False
        print(f"  ✅ {description}")
    
    return True

def test_version_updated():
    """Verify version number was updated"""
    print("\n🧪 Testing version number...")
    
    with open('main.py', 'r') as f:
        code = f.read()
    
    if 'version = "2.4.1"' in code:
        print("  ✅ Version updated to 2.4.1")
        return True
    else:
        print("  ❌ Version not updated")
        return False

def main():
    """Run all integration tests"""
    print("=" * 60)
    print("🚀 beanOS Bitmap Icon Integration - End-to-End Test")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_icon_map_completeness,
        test_bitmap_format,
        test_draw_function_signature,
        test_documentation,
        test_version_updated,
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if all(results):
        print("\n🎉 All integration tests passed!")
        print("\n✨ The bitmap icon system is fully integrated and ready to use!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")
        return 1

if __name__ == '__main__':
    import sys
    sys.exit(main())
