"""
Bug fixer for Breaking Point MCP Agent
Identifies and fixes common issues in the codebase
"""

import os
import sys
import inspect
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

# Configure logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("BPAgent.Fixer")

class Issue:
    """Represents a code issue that needs fixing"""
    
    def __init__(self, file_path: str, line_number: int, issue_type: str, 
                description: str, fix_suggestion: str, severity: str = "warning"):
        self.file_path = file_path
        self.line_number = line_number
        self.issue_type = issue_type
        self.description = description
        self.fix_suggestion = fix_suggestion
        self.severity = severity  # "info", "warning", "error", "critical"
    
    def __str__(self) -> str:
        return f"{self.severity.upper()}: {self.issue_type} in {os.path.basename(self.file_path)}:{self.line_number} - {self.description}"

def find_project_files(directory: str, pattern: str = r'\.py$') -> List[str]:
    """Find all files matching pattern in directory"""
    files = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if re.search(pattern, filename):
                files.append(os.path.join(root, filename))
    return files

def check_import_errors(file_path: str) -> List[Issue]:
    """Check for potential import errors"""
    issues = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Check for circular imports
    imported_modules = []
    for i, line in enumerate(lines):
        match = re.match(r'^\s*from\s+\.(\w+)\s+import', line)
        if match:
            module_name = match.group(1)
            imported_modules.append(module_name)
    
    file_name = os.path.basename(file_path)
    module_name = os.path.splitext(file_name)[0]
    
    if module_name in imported_modules:
        issues.append(Issue(
            file_path,
            0,
            "Circular Import",
            f"Module {module_name} imports itself, which may cause circular import issues",
            "Restructure imports to avoid circular dependencies",
            "error"
        ))
    
    # Check for wildcard imports
    for i, line in enumerate(lines):
        if re.search(r'^\s*from\s+[\.\w]+\s+import\s+\*', line):
            issues.append(Issue(
                file_path,
                i + 1,
                "Wildcard Import",
                "Using wildcard import (import *) can lead to namespace pollution",
                "Explicitly import only the required names",
                "warning"
            ))
    
    return issues

def check_error_handling(file_path: str) -> List[Issue]:
    """Check for issues with error handling"""
    issues = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Check for bare except clauses
    in_try_block = False
    has_except = False
    bare_except_line = None
    
    for i, line in enumerate(lines):
        # Check for try statement
        if re.search(r'^\s*try\s*:', line):
            in_try_block = True
            has_except = False
            continue
        
        # Check for except statement
        if in_try_block and re.search(r'^\s*except\s*:', line):
            bare_except_line = i + 1
            has_except = True
            continue
        
        # Check for except with exception types
        if in_try_block and re.search(r'^\s*except\s+\w+', line):
            has_except = True
            continue
        
        # Check for end of try block
        if in_try_block and re.search(r'^\s*\w+', line) and not line.strip().startswith(('except', 'finally', '#')):
            # End of try-except block
            if has_except and bare_except_line is not None:
                issues.append(Issue(
                    file_path,
                    bare_except_line,
                    "Bare Except",
                    "Using bare 'except:' without specifying exception types can mask errors",
                    "Specify the exception types to catch",
                    "warning"
                ))
            in_try_block = False
            has_except = False
            bare_except_line = None
    
    # Check for raising string exceptions
    for i, line in enumerate(lines):
        if re.search(r'^\s*raise\s+[\'"]', line):
            issues.append(Issue(
                file_path,
                i + 1,
                "String Exception",
                "Raising string exceptions is deprecated",
                "Raise an instance of an exception class",
                "error"
            ))
    
    # Check for exception handling without logging
    in_except_block = False
    has_logging = False
    except_line = None
    
    for i, line in enumerate(lines):
        # Check for except statement
        if re.search(r'^\s*except\s+', line):
            in_except_block = True
            has_logging = False
            except_line = i + 1
            continue
        
        # Check for logging in except block
        if in_except_block and re.search(r'log(ger)?\.(\w+)\(', line):
            has_logging = True
            continue
        
        # Check for end of except block
        if in_except_block and re.search(r'^\s*\w+', line) and not line.strip().startswith(('#', 'if', 'else', 'elif', 'try', 'except', 'finally', 'raise')):
            # End of except block
            if not has_logging and except_line is not None:
                issues.append(Issue(
                    file_path,
                    except_line,
                    "No Logging In Except",
                    "Exception caught without logging",
                    "Log the exception to aid in debugging",
                    "info"
                ))
            in_except_block = False
            has_logging = False
            except_line = None
    
    return issues

def check_resource_management(file_path: str) -> List[Issue]:
    """Check for issues with resource management"""
    issues = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Check for file operations without context managers
    for i, line in enumerate(lines):
        # Check for file open without with
        if re.search(r'^\s*\w+\s*=\s*open\(', line):
            # Look ahead for file.close()
            has_close = False
            for j in range(i+1, min(i+30, len(lines))):
                if re.search(r'\.close\(\)', lines[j]):
                    has_close = True
                    break
            
            if not has_close:
                issues.append(Issue(
                    file_path,
                    i + 1,
                    "Unclosed File",
                    "File opened without using context manager (with) and no close() call found",
                    "Use 'with open(...) as file:' to ensure the file is closed",
                    "warning"
                ))
    
    # Check for aiohttp session without proper cleanup
    if "aiohttp" in content:
        session_created = False
        session_closed = False
        session_line = None
        
        for i, line in enumerate(lines):
            # Check for session creation
            if re.search(r'^\s*\w+\s*=\s*aiohttp\.ClientSession\(', line) or re.search(r'^\s*self\.session\s*=\s*aiohttp\.ClientSession\(', line):
                session_created = True
                session_line = i + 1
                continue
            
            # Check for session close
            if session_created and (re.search(r'\.session\.close\(\)', line) or "await self.session.close()" in line):
                session_closed = True
            
            # Check for cleanup in __aexit__
            if "__aexit__" in line and "session" in content and ".close()" in content:
                session_closed = True
                
        if session_created and not session_closed and session_line is not None:
            issues.append(Issue(
                file_path,
                session_line,
                "Unclosed Session",
                "aiohttp ClientSession created without proper cleanup",
                "Ensure session is closed with 'await session.close()' or use async context manager",
                "warning"
            ))
    
    return issues

def check_async_issues(file_path: str) -> List[Issue]:
    """Check for issues with async/await"""
    issues = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Only check files with async code
    if "async def" not in content:
        return issues
    
    lines = content.split('\n')
    
    # Check for blocking calls in async functions
    in_async_func = False
    func_name = None
    func_line = None
    
    for i, line in enumerate(lines):
        # Check for async function definition
        match = re.search(r'^\s*async\s+def\s+(\w+)\s*\(', line)
        if match:
            in_async_func = True
            func_name = match.group(1)
            func_line = i + 1
            continue
        
        # Check for blocking calls in async function
        if in_async_func:
            if re.search(r'^\s*time\.sleep\(', line):
                issues.append(Issue(
                    file_path,
                    i + 1,
                    "Blocking Call",
                    f"Blocking call 'time.sleep()' in async function '{func_name}'",
                    "Use 'await asyncio.sleep()' instead of 'time.sleep()'",
                    "error"
                ))
            
            if re.search(r'^\s*requests\.', line):
                issues.append(Issue(
                    file_path,
                    i + 1,
                    "Blocking Call",
                    f"Blocking call to 'requests' library in async function '{func_name}'",
                    "Use 'aiohttp' for HTTP requests in async functions",
                    "error"
                ))
            
            if re.search(r'^\s*json\.load\(', line):
                issues.append(Issue(
                    file_path,
                    i + 1,
                    "Blocking Call",
                    f"Potentially blocking file I/O in async function '{func_name}'",
                    "Consider using aiofiles for file I/O in async functions",
                    "warning"
                ))
        
        # Check for end of async function
        if in_async_func and re.search(r'^\s*def\s+', line) or (i > 0 and re.search(r'^\S', line) and not re.search(r'^(class|def|async|@|#|""")', line)):
            in_async_func = False
            func_name = None
            func_line = None
    
    # Check for missing await
    for i, line in enumerate(lines):
        if re.search(r'^\s*(self\.)?_api_call\(', line) and "await" not in line and "async def" in content:
            issues.append(Issue(
                file_path,
                i + 1,
                "Missing Await",
                "Call to async function '_api_call' without 'await'",
                "Add 'await' before the call to the async function",
                "error"
            ))
    
    return issues

def check_api_issues(file_path: str) -> List[Issue]:
    """Check for issues specific to API handling"""
    issues = []
    
    # Only check API-related files
    if not any(name in file_path for name in ["api.py", "api_async.py"]):
        return issues
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Check for hardcoded credentials
    for i, line in enumerate(lines):
        if re.search(r'password\s*=\s*[\'"][^\'"]+[\'"]', line) and not re.search(r'password\s*=\s*[\'"][*]+[\'"]', line):
            issues.append(Issue(
                file_path,
                i + 1,
                "Hardcoded Credentials",
                "Hardcoded password in source code",
                "Use configuration or environment variables for credentials",
                "critical"
            ))
    
    # Check for missing error handling in API calls
    for i, line in enumerate(lines):
        if "requests." in line and "try" not in "".join(lines[max(0, i-5):i]):
            issues.append(Issue(
                file_path,
                i + 1,
                "Missing Error Handling",
                "API call without error handling",
                "Wrap API calls in try-except blocks",
                "warning"
            ))
    
    # Check for exception wrapping without context
    for i, line in enumerate(lines):
        if re.search(r'raise\s+API(Error|Exception)', line) and "from" not in line:
            issues.append(Issue(
                file_path,
                i + 1,
                "Exception Chaining",
                "API exception raised without chaining original exception",
                "Use 'raise APIError(...) from e' to preserve the exception chain",
                "info"
            ))
    
    return issues

def check_cache_issues(file_path: str) -> List[Issue]:
    """Check for issues with caching"""
    issues = []
    
    # Only check cache-related files
    if "cache" not in file_path:
        return issues
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Check for file writes without atomic operations
    for i, line in enumerate(lines):
        if re.search(r'with open\([^,]+, [\'"]w[\'"]', line):
            # Check for atomic write pattern
            has_atomic = False
            for j in range(max(0, i-10), i+10):
                if j < len(lines) and ("temp" in lines[j] or "tmp" in lines[j]) and ("rename" in lines[j] or "replace" in lines[j]):
                    has_atomic = True
                    break
            
            if not has_atomic:
                issues.append(Issue(
                    file_path,
                    i + 1,
                    "Non-Atomic Write",
                    "File write without atomic operation",
                    "Use a temporary file and rename to make writes atomic",
                    "warning"
                ))
    
    # Check for cache key generation
    if "get_cache_key" in content and "md5" not in content and "hash" not in content:
        for i, line in enumerate(lines):
            if "def get_cache_key" in line:
                issues.append(Issue(
                    file_path,
                    i + 1,
                    "Weak Cache Key",
                    "Cache key generation without hashing",
                    "Use a cryptographic hash function for cache keys",
                    "warning"
                ))
    
    # Check for missing cache directory creation
    has_mkdir = False
    for line in lines:
        if "makedirs" in line or "mkdir" in line:
            has_mkdir = True
            break
    
    if not has_mkdir:
        issues.append(Issue(
            file_path,
            0,
            "Missing Directory Creation",
            "Cache module doesn't create cache directory",
            "Add os.makedirs(cache_dir, exist_ok=True) to ensure directory exists",
            "warning"
        ))
    
    return issues

def check_plugin_issues(file_path: str) -> List[Issue]:
    """Check for issues with the plugin system"""
    issues = []
    
    # Only check plugin-related files
    if "plugin" not in file_path:
        return issues
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Check for plugin loading without error handling
    for i, line in enumerate(lines):
        if "import" in line and "importlib" in line:
            # Look for try-except around imports
            has_try = False
            for j in range(max(0, i-5), i+1):
                if j < len(lines) and "try" in lines[j]:
                    has_try = True
                    break
            
            if not has_try:
                issues.append(Issue(
                    file_path,
                    i + 1,
                    "Unsafe Plugin Import",
                    "Plugin importing without error handling",
                    "Wrap plugin imports in try-except blocks",
                    "warning"
                ))
    
    # Check for missing plugin registry initialization
    if "PluginManager" in content and "singleton" not in content.lower():
        issues.append(Issue(
            file_path,
            0,
            "Plugin Registry Pattern",
            "Plugin manager might not be using singleton pattern",
            "Implement singleton pattern for plugin manager",
            "info"
        ))
    
    return issues

def check_config_issues(file_path: str) -> List[Issue]:
    """Check for issues with configuration handling"""
    issues = []
    
    # Only check config-related files
    if "config" not in file_path:
        return issues
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Check for direct environment variable access
    for i, line in enumerate(lines):
        if re.search(r'os\.environ\[', line) and "get" not in line:
            issues.append(Issue(
                file_path,
                i + 1,
                "Direct Env Access",
                "Direct access to environment variable without get()",
                "Use os.environ.get() to avoid KeyError for missing variables",
                "warning"
            ))
    
    # Check for missing validation
    if "load" in content and "validate" not in content:
        for i, line in enumerate(lines):
            if "def load" in line:
                issues.append(Issue(
                    file_path,
                    i + 1,
                    "Missing Validation",
                    "Configuration loading without validation",
                    "Add validation for configuration values",
                    "info"
                ))
    
    # Check for type conversion of environment variables
    env_handling = False
    type_conversion = False
    
    for line in lines:
        if "os.environ" in line:
            env_handling = True
        if env_handling and any(type_name in line for type_name in ["int(", "float(", "bool("]):
            type_conversion = True
    
    if env_handling and not type_conversion:
        issues.append(Issue(
            file_path,
            0,
            "Environment Type Conversion",
            "Environment variables might not be converted to appropriate types",
            "Add type conversion for environment variables",
            "warning"
        ))
    
    return issues

def check_issues(directory: str) -> List[Issue]:
    """Check for issues in all project files"""
    issues = []
    
    # Find all Python files
    py_files = find_project_files(directory, r'\.py$')
    
    # Check each file for issues
    for file_path in py_files:
        logger.info(f"Checking {file_path}")
        
        # Run all checks
        issues.extend(check_import_errors(file_path))
        issues.extend(check_error_handling(file_path))
        issues.extend(check_resource_management(file_path))
        issues.extend(check_async_issues(file_path))
        issues.extend(check_api_issues(file_path))
        issues.extend(check_cache_issues(file_path))
        issues.extend(check_plugin_issues(file_path))
        issues.extend(check_config_issues(file_path))
    
    return issues

def fix_issues(issues: List[Issue], auto_fix: bool = False) -> None:
    """Fix or report issues"""
    critical = [i for i in issues if i.severity == "critical"]
    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]
    infos = [i for i in issues if i.severity == "info"]
    
    print(f"\nFound {len(issues)} potential issues:")
    print(f"  Critical: {len(critical)}")
    print(f"  Error: {len(errors)}")
    print(f"  Warning: {len(warnings)}")
    print(f"  Info: {len(infos)}")
    
    # Group by file
    issues_by_file = {}
    for issue in issues:
        if issue.file_path not in issues_by_file:
            issues_by_file[issue.file_path] = []
        issues_by_file[issue.file_path].append(issue)
    
    # Report issues by file
    for file_path, file_issues in issues_by_file.items():
        print(f"\n{os.path.basename(file_path)}:")
        for issue in sorted(file_issues, key=lambda i: i.line_number):
            print(f"  Line {issue.line_number}: [{issue.severity.upper()}] {issue.issue_type} - {issue.description}")
            print(f"    Fix: {issue.fix_suggestion}")

def main():
    """Check for issues in the project"""
    print("\n===============================")
    print("Breaking Point MCP Agent Fixer")
    print("===============================\n")
    
    # Get project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(project_dir, "src")
    
    print(f"Checking for issues in: {src_dir}\n")
    
    # Find and report issues
    issues = check_issues(src_dir)
    fix_issues(issues)
    
    print("\nIssue check completed.")
    
    # Provide summary
    if issues:
        print("\nConsider fixing the reported issues to improve code quality and reliability.")
    else:
        print("\nNo issues found. Code looks good!")

if __name__ == "__main__":
    main()
