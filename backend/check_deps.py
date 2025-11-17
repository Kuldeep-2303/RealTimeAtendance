from importlib.metadata import distributions
import re
from typing import List

def get_missing_packages(requirements_path: str) -> List[str]:
    """
    Reads a requirements.txt file and checks which packages are not installed
    in the current Python environment.

    Args:
        requirements_path: The path to the requirements.txt file.

    Returns:
        A list of requirement strings for packages that are missing.
    """
    missing_packages = []
    
    # Get a set of all installed packages' names for quick lookups
    installed_packages = {dist.metadata['name'].lower() for dist in distributions()}

    with open(requirements_path, 'r') as f:
        requirements = f.readlines()

    for req in requirements:
        req = req.strip()
        if not req or req.startswith('#'):
            continue

        # Extract the base package name (e.g., 'fastapi' from 'fastapi==0.104.1')
        # This regex handles '==', '>=', '<=', '[', and just the name.
        match = re.match(r'^[a-zA-Z0-9_-]+', req)
        if match:
            package_name = match.group(0).lower()
            if package_name not in installed_packages:
                missing_packages.append(req)

    return missing_packages

if __name__ == "__main__":
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    requirements_path = os.path.join(script_dir, 'requirements.txt')
    missing = get_missing_packages(requirements_path)
    if missing:
        print("The following required packages are not installed:")
        for pkg in missing:
            print(f"- {pkg}")
    else:
        print("All required packages are installed.")
