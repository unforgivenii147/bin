#!/data/data/com.termux/files/usr/bin/env python3
"""
Recursive extractor of top-level and nested classes, functions, and constants from Python scripts.
Useful for codebase analysis and refactoring.
"""

import ast
import multiprocessing as mp
import os
from typing import Dict, List, Tuple, Set

OUTPUT_DIR = "output"
EXCLUDE_DIRS = {"test", "tests", "examples", "output", ".git", "__pycache__"}


def is_python_script(path: str) -> bool:
    """
    Checks if a file is a Python script based on its extension or shebang.
    
    Args:
        path (str): The file path to check.
        
    Returns:
        bool: True if it's a Python script, False otherwise.
    """
    if path.endswith(".py"):
        return True
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            line = f.readline()
        return line.startswith("#!") and "python" in line.lower()
    except Exception:
        return False


def discover_python_files(root_dir: str = ".") -> List[str]:
    """
    Recursively finds all Python files in the given root directory, excluding specific folders.
    
    Args:
        root_dir (str): The starting directory for discovery.
        
    Returns:
        List[str]: A list of paths to discovered Python files.
    """
    files = []
    for root, dirs, fnames in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for fname in fnames:
            p = os.path.join(root, fname)
            if is_python_script(p):
                files.append(p)
    return files


def mark_parents(node: ast.AST):
    """
    Recursively marks each node with its parent node.
    
    Args:
        node (ast.AST): The current AST node.
    """
    for child in ast.iter_child_nodes(node):
        setattr(child, "_parent", node)
        mark_parents(child)


def is_constant_name(name: str) -> bool:
    """
    Checks if a variable name follows constant naming conventions (all uppercase).
    
    Args:
        name (str): The name to check.
        
    Returns:
        bool: True if the name is all uppercase, False otherwise.
    """
    return name.isupper()


def extract_from_file(
    path: str,
) -> Tuple[
    str,
    Dict[str, str],  # top-level classes
    Dict[str, str],  # top-level functions
    Dict[str, str],  # nested classes
    Dict[str, str],  # nested functions
    Dict[str, str],  # top-level constants
]:
    """
    Extracts structural elements (classes, functions, constants) from a single Python file.
    
    Args:
        path (str): Path to the Python file.
        
    Returns:
        A tuple containing the file path and dictionaries of extracted elements.
    """
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            source = f.read()
        tree = ast.parse(source)
    except Exception:
        return path, {}, {}, {}, {}, {}

    mark_parents(tree)

    tl_classes, tl_funcs = {}, {}
    nested_classes, nested_funcs = {}, {}
    consts = {}

    for node in ast.walk(tree):
        # ----- Classes & Functions -----
        if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
            try:
                src = ast.get_source_segment(source, node)
            except (ValueError, Exception):
                continue
            if not src:
                continue

            parent = getattr(node, "_parent", None)
            is_toplevel = isinstance(parent, ast.Module)

            if isinstance(node, ast.ClassDef):
                if is_toplevel:
                    tl_classes[node.name] = src
                else:
                    nested_classes[node.name] = src

            elif isinstance(node, ast.FunctionDef):
                if is_toplevel:
                    tl_funcs[node.name] = src
                else:
                    nested_funcs[node.name] = src

        # ----- Constants (top-level only) -----
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            parent = getattr(node, "_parent", None)
            if not isinstance(parent, ast.Module):
                continue

            if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                name = node.targets[0].id
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                name = node.target.id
            else:
                continue

            if not is_constant_name(name):
                continue

            try:
                src = ast.get_source_segment(source, node)
            except (ValueError, Exception):
                continue
            if src:
                consts[name] = src

    return path, tl_classes, tl_funcs, nested_classes, nested_funcs, consts


def write_output(path: str, data: Dict[str, str]) -> None:
    """
    Writes extracted source segments to a file.
    
    Args:
        path (str): Output file path.
        data (Dict[str, str]): Mapping of element names to their source code.
    """
    with open(path, "w", encoding="utf-8") as f:
        for name, src in sorted(data.items()):
            f.write(src.rstrip() + "\n\n")


def main():
    """
    Main execution logic for discovering files, extracting elements in parallel,
    and saving the results.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    files = discover_python_files()

    if not files:
        print("No Python files found.")
        return

    # Use multiprocessing for speed on large codebases
    with mp.Pool(mp.cpu_count()) as pool:
        results = pool.map(extract_from_file, files)

    tl_classes, tl_funcs = {}, {}
    nested_classes, nested_funcs = {}, {}
    const_map = {}

    for _, c, f, nc, nf, consts in results:
        tl_classes.update(c)
        tl_funcs.update(f)
        nested_classes.update(nc)
        nested_funcs.update(nf)
        const_map.update(consts)

    # Save to corresponding files
    write_output(os.path.join(OUTPUT_DIR, "classes.py"), tl_classes)
    write_output(os.path.join(OUTPUT_DIR, "functions.py"), tl_funcs)
    write_output(os.path.join(OUTPUT_DIR, "nested_classes.py"), nested_classes)
    write_output(os.path.join(OUTPUT_DIR, "nested_functions.py"), nested_funcs)
    write_output(os.path.join(OUTPUT_DIR, "const.py"), const_map)

    # Print summary
    categories = [
        ("Top-Level Classes", tl_classes),
        ("Top-Level Functions", tl_funcs),
        ("Nested Classes", nested_classes),
        ("Nested Functions", nested_funcs),
        ("Constants", const_map),
    ]

    for title, mapping in categories:
        print(f"\n=== {title} ===")
        for n in sorted(mapping):
            print(f" - {n}")

    print(f"\nOutputs saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
