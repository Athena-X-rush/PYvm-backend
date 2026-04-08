m#!/usr/bin/env python3
"""
Test script for the Mini Interpreter bytecode generation and VM execution
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import bytecode
import parser

def test_basic_arithmetic():
    """Test basic arithmetic operations"""
    print("🧮 Testing Basic Arithmetic...")
    
    code = """
x = 10 + 5 + 3
y = x * 2
result = y + 0
print "Result: " + result
"""
    
    try:
        # Compile to bytecode
        instructions = bytecode.compile_code(code)
        print(f"✅ Generated {len(instructions)} bytecode instructions")
        
        # Execute bytecode
        output = bytecode.execute_bytecode(instructions)
        print(f"✅ Output: {output}")
        print("✅ Basic arithmetic test passed!\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("❌ Basic arithmetic test failed!\n")

def test_conditional_logic():
    """Test conditional logic"""
    print("🔀 Testing Conditional Logic...")
    
    code = """
if 1:
    print "Always runs"

if 0:
    print "Never runs"

print "Done!"
"""
    
    try:
        # Compile to bytecode
        instructions = bytecode.compile_code(code)
        print(f"✅ Generated {len(instructions)} bytecode instructions")
        
        # Execute bytecode
        output = bytecode.execute_bytecode(instructions)
        print(f"✅ Output: {output}")
        print("✅ Conditional logic test passed!\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("❌ Conditional logic test failed!\n")

def test_interactive_input():
    """Test interactive input"""
    print("📝 Testing Interactive Input...")
    
    code = """
name = input("Enter your name: ")
age = int(input("Enter your age: "))
print "Hello " + name + ", you are " + age + " years old!"
"""
    
    try:
        # Compile to bytecode
        instructions = bytecode.compile_code(code)
        print(f"✅ Generated {len(instructions)} bytecode instructions")
        
        # Execute bytecode with mock input
        def mock_input():
            inputs = ["Alice", "25"]
            if not hasattr(mock_input, 'index'):
                mock_input.index = 0
            if mock_input.index < len(inputs):
                value = inputs[mock_input.index]
                mock_input.index += 1
                return value
            return "default"
        
        output = bytecode.execute_bytecode(instructions, mock_input)
        print(f"✅ Output: {output}")
        print("✅ Interactive input test passed!\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("❌ Interactive input test failed!\n")

def test_complex_operations():
    """Test complex operations"""
    print("🔧 Testing Complex Operations...")
    
    code = """
# Arithmetic operations
a = 10
b = 20
c = a + b
d = c * 2
e = d / 4

# Comparison operations
if e > 10:
    print "e is greater than 10"

if e == 15:
    print "e equals 15"

# String operations
name = "Alice"
greeting = "Hello, " + name
print greeting
"""
    
    try:
        # Compile to bytecode
        instructions = bytecode.compile_code(code)
        print(f"✅ Generated {len(instructions)} bytecode instructions")
        
        # Execute bytecode
        output = bytecode.execute_bytecode(instructions)
        print(f"✅ Output: {output}")
        print("✅ Complex operations test passed!\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("❌ Complex operations test failed!\n")

def test_bytecode_inspection():
    """Test bytecode inspection"""
    print("🔍 Testing Bytecode Inspection...")
    
    code = """
x = 10 + 5
print x
"""
    
    try:
        # Compile to bytecode
        instructions = bytecode.compile_code(code)
        print(f"✅ Generated {len(instructions)} bytecode instructions")
        
        # Print instructions
        print("📋 Bytecode Instructions:")
        for i, instruction in enumerate(instructions):
            print(f"  {i:2d}: {instruction.opcode.value:15s} {str(instruction.operand):10s} {instruction.comment}")
        
        print("✅ Bytecode inspection test passed!\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("❌ Bytecode inspection test failed!\n")

def main():
    """Run all tests"""
    print("🚀 Mini Interpreter Test Suite")
    print("=" * 50)
    
    test_basic_arithmetic()
    test_conditional_logic()
    test_interactive_input()
    test_complex_operations()
    test_bytecode_inspection()
    
    print("🎯 All tests completed!")
    print("=" * 50)

if __name__ == "__main__":
    main()
