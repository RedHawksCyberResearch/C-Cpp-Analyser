import clang.cindex
import re
import sys
import difflib

# This function parses a C/C++ source code file using Clang and returns a translation unit.


def analyze_function(file_name):
    index = clang.cindex.Index.create()
    tu = index.parse(file_name)
    return tu


# Using regex, extracts the function name, parameter type (as list), return type
def extract_parameters_and_return(cursor):
    func_name = cursor.displayname
    # parameter list
    params = re.findall(r"\((.*?)\)", func_name)
    # extracts the function name by removing the brackets and the parameters
    func_name = re.sub(r"\(.*?\)", "", func_name)
    # cursor.result_type.spelling - provides the spelling of the return type of the function
    return func_name, params, cursor.result_type.spelling

#  Recursively calls functions called within a function


def print_called_functions(cursor):
    # iterating over the cursor children to get the spelling of the function that has been called. compares to the kind of cursor that corresponds to a function call
    for child in cursor.get_children():
        if child.kind == clang.cindex.CursorKind.CALL_EXPR:
            print(f"{child.spelling}")
        # Recursion to iterate over
        print_called_functions(child)

# function body extraction


def extract_function_body(cursor):
    source_code = ""
    for token in cursor.get_tokens():
        source_code += token.spelling

    return source_code

# function comparison


def compare_functions(func1, func2, funcN1, funcN2):
    # compare two function bodies and generate differences
    differ = difflib.Differ()
    diff = list(differ.compare(func1.splitlines(), func2.splitlines()))

    # print the differences
    print(f"Differences between Function Sequence 1 and Function Sequence 2:")
    for line in diff:
        if line.startswith('- '):
            print("----------")
            print(f"Line Unique to Function {funcN1}: {line[2:]}")
        elif line.startswith('+ '):
            print("----------")
            print(f"Line Unique to Function {funcN2}: {line[2:]}")
        elif line.startswith('  '):
            print("----------")
            print(f"Line Common: {line[2:]}")
        elif line.startswith('? '):
            print("----------")
            print(f"line not present in either input: {line[2:]}")


if __name__ == "__main__":
    # gather filename from argument for easier usage
    fileName = sys.argv[1]
    translation_unit = analyze_function(fileName)

    # Counter for the number of functions
    count = 0

    functions = []  # Store function bodies for comparison
    # Start iteration over the main translation unit
    for func_cursor in translation_unit.cursor.get_children():
        # filters out cursors that are not function declarations. skips non function cursors
        if func_cursor.kind != clang.cindex.CursorKind.FUNCTION_DECL:
            continue

        count += 1
        print("-----------")
        print(f"Function Number: {count}")

        # Q1: For each function, identify function name, parameter types and returned value types
        func_name, params, return_type = extract_parameters_and_return(
            func_cursor)

        print(f"Function Name: {func_name}")
        for param in params:
            print(f"Parameter Type: {param}")
        print(f"Return Value: {return_type}")

        # Q2: For each function, what other functions it has called
        print(f"Functions Called:")
        print_called_functions(func_cursor)

        # Q3: For each function, output start and end line
        print(
            f"Start: {func_cursor.extent.start} | End: {func_cursor.extent.end}")

        # Storing the function body for comparison
        function_body = extract_function_body(func_cursor)
        if function_body:
            functions.append(function_body)

    # Q4: For any two functions, output the differences
    if len(functions) >= 2:
        while True:
            try:
                functionNum1 = int(input("Desired Function Number 1: "))
                functionNum2 = int(input("Desired Function Number 2: "))
                if functionNum1 > 0 and functionNum2 and functionNum1 != functionNum2 and functionNum1 < len(functions) and functionNum2 < len(functions):
                    break
            except ValueError:
                print("Invalid input. Please enter a valid function number.")
        # -1 because list starts from 0
        compare_functions(
            functions[functionNum1-1], functions[functionNum2-1], functionNum1, functionNum2)
