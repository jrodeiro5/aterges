#!/usr/bin/env python3
"""
EMERGENCY Repository Fix Script
Fixes critical issues found in health dashboard
"""

import os
import subprocess
import sys

def pause_for_user(message="Press Enter to continue..."):
    """Pause and wait for user input."""
    try:
        input(f"\n{message}")
    except KeyboardInterrupt:
        print("\n\n👋 Emergency fix cancelled!")
        sys.exit(0)

def run_git_command(command, description):
    """Run a git command with error handling."""
    try:
        print(f"🔧 {description}...")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ Success: {description}")
            return True
        else:
            print(f"   ❌ Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def emergency_fix():
    """Run emergency fixes for critical repository issues."""
    print("🚨 EMERGENCY REPOSITORY FIX")
    print("=" * 50)
    print("This will fix critical issues found in the health check:")
    print("1. Remove Python venv from git tracking")
    print("2. Remove sensitive files") 
    print("3. Update .gitignore")
    print("4. Clean up repository")
    print()
    
    response = input("Continue with emergency fix? (y/N): ").lower().strip()
    if response != 'y':
        print("❌ Emergency fix cancelled")
        return
    
    print("\n🚨 STARTING EMERGENCY FIX...")
    
    # Step 1: Remove venv from git tracking
    print("\n1️⃣ REMOVING PYTHON VENV FROM GIT")
    print("-" * 40)
    
    venv_paths = [
        "backend/venv",
        "backend/.venv", 
        "venv",
        ".venv"
    ]
    
    for venv_path in venv_paths:
        if os.path.exists(venv_path):
            print(f"🗑️ Removing {venv_path} from git tracking...")
            run_git_command(f'git rm -r --cached "{venv_path}"', f"Remove {venv_path} from git")
    
    # Step 2: Remove sensitive files
    print("\n2️⃣ REMOVING SENSITIVE FILES")
    print("-" * 40)
    
    sensitive_files = [
        "GITHUB_SECRETS_FIX.txt",
        "GITHUB_SECRETS_TO_UPDATE.txt", 
        "CORRECTED_GITHUB_SECRETS.txt",
        "VERIFIED_SUPABASE_CONFIG.env"
    ]
    
    for file in sensitive_files:
        if os.path.exists(file):
            print(f"🔒 Removing sensitive file: {file}")
            run_git_command(f'git rm --cached "{file}"', f"Remove {file} from git")
            try:
                os.remove(file)
                print(f"   🗑️ Deleted local file: {file}")
            except Exception as e:
                print(f"   ⚠️ Could not delete local file: {e}")
    
    # Step 3: Update .gitignore
    print("\n3️⃣ UPDATING .GITIGNORE")
    print("-" * 40)
    
    critical_gitignore_patterns = [
        "",
        "# CRITICAL: Python virtual environments (NEVER commit these!)",
        "venv/",
        ".venv/",
        "backend/venv/", 
        "backend/.venv/",
        "env/",
        ".env/",
        "",
        "# CRITICAL: Secret files (NEVER commit these!)",
        "*secret*",
        "*SECRET*",
        "*password*",
        "*PASSWORD*",
        "*key*",
        "*KEY*",
        "*token*",
        "*TOKEN*",
        "*credential*",
        "*CREDENTIAL*",
        "*.env",
        ".env.*",
        "",
        "# Python cache and build artifacts",
        "__pycache__/",
        "*.py[cod]",
        "*$py.class",
        "*.so",
        ".Python",
        "build/",
        "develop-eggs/",
        "dist/",
        "downloads/",
        "eggs/",
        ".eggs/",
        "lib/",
        "lib64/",
        "parts/",
        "sdist/",
        "var/",
        "wheels/",
        "pip-wheel-metadata/",
        "share/python-wheels/",
        "*.egg-info/",
        ".installed.cfg",
        "*.egg",
        "",
        "# Node.js (if not already covered)",
        "node_modules/",
        "npm-debug.log*",
        "yarn-debug.log*",
        "yarn-error.log*",
        "",
        "# Build outputs",
        ".next/",
        "out/",
        "dist/",
        "build/",
        "",
        "# OS files",
        ".DS_Store",
        ".DS_Store?",
        "._*",
        ".Spotlight-V100",
        ".Trashes",
        "ehthumbs.db",
        "Thumbs.db",
        "",
        "# IDE files",
        ".vscode/",
        ".idea/",
        "*.swp",
        "*.swo",
        "*~",
        "",
        "# Temporary files",
        "*.tmp",
        "*.temp",
        "temp_*",
        "*.backup",
        "*.bak",
        "*.orig",
        "*.old",
    ]
    
    try:
        # Read existing .gitignore
        existing_content = ""
        if os.path.exists('.gitignore'):
            with open('.gitignore', 'r') as f:
                existing_content = f.read()
        
        # Add new patterns that don't already exist
        new_patterns = []
        for pattern in critical_gitignore_patterns:
            if pattern.strip() and pattern not in existing_content:
                new_patterns.append(pattern)
        
        if new_patterns:
            with open('.gitignore', 'a') as f:
                f.write('\n' + '\n'.join(new_patterns))
            print(f"   ✅ Added {len(new_patterns)} critical patterns to .gitignore")
        else:
            print("   ℹ️ .gitignore already contains critical patterns")
            
    except Exception as e:
        print(f"   ❌ Error updating .gitignore: {e}")
    
    # Step 4: Check repository size
    print("\n4️⃣ CHECKING REPOSITORY SIZE")
    print("-" * 40)
    
    try:
        result = subprocess.run(['git', 'count-objects', '-v'], 
                              capture_output=True, text=True, cwd='.')
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line.startswith('size '):
                    size_kb = int(line.split()[1])
                    size_mb = size_kb / 1024
                    print(f"   📊 Current repository size: {size_mb:.1f} MB")
                    break
        else:
            print("   ⚠️ Could not check repository size")
    except Exception as e:
        print(f"   ❌ Error checking size: {e}")
    
    # Step 5: Show what to do next
    print("\n5️⃣ NEXT STEPS")
    print("-" * 40)
    print("🔄 You now need to commit these critical fixes:")
    print()
    print("git add .gitignore")
    print('git commit -m "fix: EMERGENCY - Remove venv and secrets, update .gitignore"')
    print("git push origin main")
    print()
    print("📉 This should dramatically reduce your repository size!")
    print("🔒 And remove security risks from committed secrets.")
    
    print("\n✅ EMERGENCY FIX COMPLETE!")
    print("=" * 50)
    print("⚠️  IMPORTANT: Run the git commands above to complete the fix!")

def main():
    """Main emergency fix function."""
    try:
        emergency_fix()
    except KeyboardInterrupt:
        print("\n\n👋 Emergency fix cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error during emergency fix: {e}")
    finally:
        pause_for_user("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
