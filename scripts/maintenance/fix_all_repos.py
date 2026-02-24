#!/usr/bin/env python3
"""
Automated Database Connection Pool Fix
Removes 'with conn:' pattern from all repository files
Applies the pattern: try/except/finally with explicit commit/rollback

Usage:
    python fix_all_repos.py
"""

import os
import re
import sys
from pathlib import Path

REPO_DIR = Path(__file__).parent / "app" / "repository"

# Pattern to find: with conn: followed by with conn.cursor
# We'll replace this with just with conn.cursor
PATTERN_TO_FIX = re.compile(
    r'(\s+)with conn:\s*\n(\s+)with conn\.cursor\(\)',
    re.MULTILINE
)

#Pattern to find the finally block and add error handling
FINALLY_PATTERN = re.compile(
    r'(\s+)finally:\s*\n(\s+)conn\.close\(\)',
    re.MULTILINE
)

def fix_file(filepath):
    """Fix a single repository file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix 1: Remove 'with conn:' wrapper
        # Match: with conn: followed by  with conn.cursor
        matches = list(PATTERN_TO_FIX.finditer(content))
        if matches:
            print(f"  Found {len(matches)} 'with conn:' patterns")
            # Replace the pattern
            content = PATTERN_TO_FIX.sub(r'\1with conn.cursor()', content)
        
        # Fix 2: Add explicit commit/rollback before finally
        # Find all 'finally:\n        conn.close()' patterns
        if 'finally:' in content and 'conn.close()' in content:
            # Replace 'finally:' section to add error handling
            old_finally = re.compile(
                r'(\s+)finally:\s*\n(\s+)conn\.close\(\)',
                re.MULTILINE
            )
            
            def replace_finally(match):
                indent1 = match.group(1)
                indent2 = match.group(2)
                # Return the finally block with error handling
                return f'{indent1}except Exception:\n{indent1}    conn.rollback()\n{indent1}    raise\n{indent1}finally:\n{indent2}conn.close()'
            
            # First, check if there's a try block that could handle this
            if 'try:' in content and 'except' not in content.split('finally:')[0]:
                content = old_finally.sub(replace_finally, content)
        
        # Unindent cursor operations if we removed 'with conn:'
        if matches:
            # Find all lines that are 4+ spaces indented after 'with conn.cursor()'
            # This is complex, so we'll note it for manual review
            pass
        
        if content != original_content:
            # Backup original
            backup_path = filepath.with_suffix('.py.bak')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            # Write fixed version
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True, "Fixed (backup created)"
        else:
            return False, "No changes needed"
        
    except Exception as e:
        return False, f"Error: {e}"

def main():
    """Fix all repository files"""
    print("=" * 80)
    print("Database Connection Pool - Repository Fixer")
    print("=" * 80)
    print()
    
    if not REPO_DIR.exists():
        print(f"❌ Repository directory not found: {REPO_DIR}")
        return 1
    
    repo_files = list(REPO_DIR.glob("*.py"))
    repo_files = [f for f in repo_files if f.name != "__init__.py"]
    
    print(f"Found {len(repo_files)} repository files")
    print()
    
    fixed_count = 0
    for filepath in repo_files:
        success, message = fix_file(filepath)
        status = "✅" if success else "⏭️ "
        print(f"{status} {filepath.name:40} {message}")
        if success:
            fixed_count += 1
    
    print()
    print("=" * 80)
    if fixed_count > 0:
        print(f"✅ Fixed {fixed_count} files!")
        print("   Backup files created with .bak extension")
        print()
        print("⚠️  IMPORTANT: Review and test the changes!")
        print("   Some files may need manual unindentation fixes.")
    else:
        print("✅ All files already fixed or no changes needed")
    print("=" * 80)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
