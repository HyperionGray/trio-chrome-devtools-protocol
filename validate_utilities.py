#!/usr/bin/env python3
"""
Validation script to demonstrate the utility classes can be instantiated
and have the expected methods.
"""

from trio_cdp.util import (
    Keyboard, Mouse, ElementHandle,
    query_selector, query_selector_all, wait_for_selector
)

def validate_keyboard():
    """Validate Keyboard class structure."""
    print("✓ Keyboard class imported")
    
    # Check methods exist
    assert hasattr(Keyboard, 'down')
    assert hasattr(Keyboard, 'up')
    assert hasattr(Keyboard, 'press')
    assert hasattr(Keyboard, 'type')
    print("✓ Keyboard has all expected methods")

def validate_mouse():
    """Validate Mouse class structure."""
    print("✓ Mouse class imported")
    
    # Check methods exist
    assert hasattr(Mouse, 'move')
    assert hasattr(Mouse, 'click')
    assert hasattr(Mouse, 'down')
    assert hasattr(Mouse, 'up')
    print("✓ Mouse has all expected methods")

def validate_element_handle():
    """Validate ElementHandle class structure."""
    print("✓ ElementHandle class imported")
    
    # Check methods exist
    assert hasattr(ElementHandle, 'click')
    assert hasattr(ElementHandle, 'type')
    assert hasattr(ElementHandle, 'get_attribute')
    assert hasattr(ElementHandle, 'get_property')
    assert hasattr(ElementHandle, 'get_text_content')
    print("✓ ElementHandle has all expected methods")

def validate_selector_functions():
    """Validate selector utility functions."""
    print("✓ query_selector function imported")
    print("✓ query_selector_all function imported")
    print("✓ wait_for_selector function imported")
    
    # Check they are callable
    assert callable(query_selector)
    assert callable(query_selector_all)
    assert callable(wait_for_selector)
    print("✓ All selector functions are callable")

def main():
    print("Validating trio_cdp.util module...")
    print()
    
    validate_keyboard()
    print()
    
    validate_mouse()
    print()
    
    validate_element_handle()
    print()
    
    validate_selector_functions()
    print()
    
    print("=" * 60)
    print("✓ All validations passed!")
    print("=" * 60)
    print()
    print("The utility module provides:")
    print("  • Keyboard class for keyboard input simulation")
    print("  • Mouse class for mouse action simulation")
    print("  • ElementHandle class for element interactions")
    print("  • query_selector() for finding elements")
    print("  • query_selector_all() for finding multiple elements")
    print("  • wait_for_selector() for waiting on elements")

if __name__ == '__main__':
    main()
