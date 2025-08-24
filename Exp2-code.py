import requests
import importlib.util
import sys
import os
import tempfile
from tabulate import tabulate

# Download and import .so module from GitHub
url = "https://github.com/Lab2Phys/module-kvlkcl/raw/refs/heads/main/module_kvlkcl.so"

try:
    r = requests.get(url)
    r.raise_for_status()
    
    # Save to temp file
    with tempfile.NamedTemporaryFile(suffix='.so', delete=False) as f:
        f.write(r.content)
        temp_path = f.name
    
    # Load module
    spec = importlib.util.spec_from_file_location("module_kvlkcl", temp_path)
    module_kvlkcl = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module_kvlkcl)
    
    print("Module loaded successfully")
    
except Exception as e:
    print(f"✗ Error: {e}")
    try:
        import ctypes
        module_kvlkcl = ctypes.CDLL(temp_path)
        print("Module loaded with ctypes")
    except:
        sys.exit(1)

# Configuration
decimal_precision = 3
num_nodes = 8
num_loops = 6

# Define circuit
R = 1000
e1 = 6
e2 = 5
e3 = 12

edges = [
    (1, 2, R), (1, 3, 2*R), (1, 6, 2*R),
    (2, 4, R), (2, 5, R), (2, 7, 0),
    (3, 4, R), (3, 8, R), (4, 7, R),
    (5, 6, R), (5, 8, R), (6, 8, R), (7, 8, R)
]

voltage_sources = {(1, 3): -e1, (1, 6): -e2, (2, 7): -e3}

loops = [
    [1, 2, 4, 3],
    [1, 2, 5, 6],
    [3, 4, 7, 8],
    [2, 4, 7],
    [2, 5, 8, 7],
    [5, 6, 8]
]

# Run analysis and display results
try:
    node_voltage_pairs, branch_currents, node_voltage_dict, branch_dict = module_kvlkcl.run_analysis(
        num_nodes, num_loops, edges, voltage_sources, loops, decimal_precision, show_widgets=False
    )
    
    print("\nNode Voltage Differences (V)")
    print(tabulate(node_voltage_pairs, headers=["Nodes", "Voltage (V)"], tablefmt="fancy_grid"))
    
    print("\nBranch Currents (mA)")
    print(tabulate(branch_currents, headers=["Branch", "Current (mA)", "Direction"], tablefmt="fancy_grid"))
    
    print("\nResults saved in Exp.pdf")
    
    # Interactive Widgets
    if hasattr(module_kvlkcl, 'create_interactive_widgets'):
        module_kvlkcl.create_interactive_widgets(node_voltage_dict, branch_dict)
    
except Exception as e:
    print(f"✗ Analysis error: {e}")

# Cleanup
try:
    os.unlink(temp_path)
except:
    pass