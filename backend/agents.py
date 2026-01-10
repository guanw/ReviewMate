from langchain_core.tools import tool
import os
import re
import subprocess
import tempfile

# Tools
@tool
def analyze_code_quality(diff: str) -> str:
    """Analyze code for quality issues: function length, naming, complexity."""
    # Clean diff markers
    lines = [line.lstrip('+- ') for line in diff.split('\n')]
    code = '\n'.join(lines)
    lines = code.split('\n')
    issues = []

    # Check for long functions (simple heuristic)
    in_function = False
    func_lines = 0
    for line in lines:
        if re.match(r'\s*def\s+\w+', line):
            in_function = True
            func_lines = 0
        elif in_function and line.strip() == '':
            continue
        elif in_function and re.match(r'\s*def\s+', line):  # Next function
            if func_lines > 20:
                issues.append(f"Function too long ({func_lines} lines). Keep under 20.")
            func_lines = 0
        elif in_function:
            func_lines += 1

    # Check naming (snake_case for variables and functions)
    for line in lines:
        # Variables
        vars = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*=', line)
        for var in vars:
            if not re.match(r'^[a-z_][a-z0-9_]*$', var):
                issues.append(f"Variable '{var}' does not follow snake_case.")

        # Functions
        funcs = re.findall(r'\bdef\s+([a-zA-Z_][a-zA-Z0-9_]*)', line)
        for func in funcs:
            if not re.match(r'^[a-z_][a-z0-9_]*$', func):
                issues.append(f"Function '{func}' does not follow snake_case.")

    return '\n'.join(issues) if issues else "No major quality issues detected."

@tool
def analyze_security(diff: str) -> str:
    """Scan code for security vulnerabilities using Bandit."""
    # Clean diff markers
    lines = [line.lstrip('+- ') for line in diff.split('\n')]
    code = '\n'.join(lines)

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_file = f.name

    try:
        result = subprocess.run(['bandit', '-f', 'txt', temp_file], capture_output=True, text=True)
        issues = result.stdout
        if 'No issues identified' in issues or 'Test results:' in issues and 'Total lines analyzed:' in issues:
            return "No security issues detected."
        return issues
    except Exception as e:
        return f"Security scan failed: {str(e)}"
    finally:
        os.unlink(temp_file)

@tool
def analyze_performance(diff: str) -> str:
    """Check for performance issues: nested loops, inefficient patterns."""
    # Clean diff markers
    lines = [line.lstrip('+- ') for line in diff.split('\n')]
    code = '\n'.join(lines)
    lines = code.split('\n')
    issues = []

    loop_depth = 0
    for line in lines:
        if 'for ' in line or 'while ' in line:
            loop_depth += 1
            if loop_depth > 2:
                issues.append("Deeply nested loops detected. Consider optimizing.")
        elif line.strip() == '' or not line.startswith(' '):
            loop_depth = 0

    # Check for O(n^2) patterns (simplified)
    if re.search(r'for.*in.*for.*in', code):
        issues.append("Potential O(n^2) complexity with nested loops.")

    return '\n'.join(issues) if issues else "No performance issues detected."

# Orchestrator function (using tools directly for simplicity)
def run_agent_workflow(diff: str) -> str:
    """Run analysis tools in sequence: Quality -> Security -> Performance."""
    results = []

    # Quality check
    quality_issues = analyze_code_quality.invoke({"diff": diff})
    results.append(f"Quality: {quality_issues}")

    # Security check
    security_issues = analyze_security.invoke({"diff": diff})
    results.append(f"Security: {security_issues}")

    # Performance check
    perf_issues = analyze_performance.invoke({"diff": diff})
    results.append(f"Performance: {perf_issues}")

    return "\n".join(results)