#!/usr/bin/env python3
"""
Test script to verify bitmap icon integration in beanOS.
This script tests that all icon bitmaps are properly loaded and accessible.
"""

import sys

def test_icon_import():
    """Test that icon_bitmaps module can be imported"""
    try:
        from icon_bitmaps import ICON_MAP
        print("✅ Successfully imported icon_bitmaps module")
        return ICON_MAP
    except ImportError as e:
        print(f"❌ Failed to import icon_bitmaps: {e}")
        sys.exit(1)

def test_icon_count(icon_map):
    """Test that all expected icons are present"""
    expected_icons = [
        "#1", "#10", "#50", "#100", "#500", "#1000",  # Milestones
        "=7", "=30",  # Streaks
        "~", "o", "%",  # Special drinks
        "<>", "[]",  # Maintenance
        ">>", "^^",  # Experimental
        "★"  # General
    ]
    
    print(f"\n📊 Icon count: {len(icon_map)} icons")
    print(f"Expected: {len(expected_icons)} icons")
    
    missing_icons = []
    for icon in expected_icons:
        if icon not in icon_map:
            missing_icons.append(icon)
            print(f"❌ Missing icon: {icon}")
        else:
            print(f"✅ Found icon: {icon}")
    
    if missing_icons:
        print(f"\n❌ Test failed: Missing {len(missing_icons)} icons")
        return False
    else:
        print(f"\n✅ All {len(expected_icons)} icons present")
        return True

def test_bitmap_data(icon_map):
    """Test that bitmap data is valid"""
    print("\n🔍 Verifying bitmap data structure...")
    
    all_valid = True
    for symbol, bitmap in icon_map.items():
        # Each 32x32 icon should have 128 bytes (4 bytes per row * 32 rows)
        expected_size = 128
        actual_size = len(bitmap)
        
        if actual_size != expected_size:
            print(f"❌ Icon '{symbol}': Expected {expected_size} bytes, got {actual_size}")
            all_valid = False
        else:
            # Check if bitmap has any actual data (not all zeros or all ones)
            unique_bytes = set(bitmap)
            if len(unique_bytes) == 1 and (0 in unique_bytes or 255 in unique_bytes):
                print(f"⚠️  Icon '{symbol}': Bitmap appears to be all {list(unique_bytes)[0]:02x} (might be blank)")
            else:
                print(f"✅ Icon '{symbol}': Valid bitmap with {len(unique_bytes)} unique byte values")
    
    if all_valid:
        print("\n✅ All bitmap data structures are valid")
    else:
        print("\n❌ Some bitmap data structures are invalid")
    
    return all_valid

def test_bitmap_rendering():
    """Test ASCII rendering of a sample bitmap"""
    from icon_bitmaps import ICON_MAP
    
    print("\n🎨 Sample icon rendering (★ - Achievement Star):")
    print("=" * 40)
    
    star_bitmap = ICON_MAP.get("★")
    if not star_bitmap:
        print("❌ Star icon not found")
        return False
    
    # Render as ASCII art
    for row in range(32):
        line = ""
        for col in range(32):
            byte_idx = row * 4 + (col // 8)
            bit_idx = 7 - (col % 8)
            pixel_value = (star_bitmap[byte_idx] >> bit_idx) & 1
            line += "█" if pixel_value else " "
        print(line)
    
    print("=" * 40)
    return True

def main():
    """Run all tests"""
    print("🧪 beanOS Bitmap Icon Integration Tests")
    print("=" * 50)
    
    # Test 1: Import
    icon_map = test_icon_import()
    
    # Test 2: Icon count
    count_ok = test_icon_count(icon_map)
    
    # Test 3: Bitmap data
    data_ok = test_bitmap_data(icon_map)
    
    # Test 4: Rendering
    render_ok = test_bitmap_rendering()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"   Import: {'✅' if icon_map else '❌'}")
    print(f"   Icon count: {'✅' if count_ok else '❌'}")
    print(f"   Bitmap data: {'✅' if data_ok else '❌'}")
    print(f"   Rendering: {'✅' if render_ok else '❌'}")
    
    if icon_map and count_ok and data_ok and render_ok:
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
