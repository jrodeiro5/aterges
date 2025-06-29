#!/usr/bin/env python3
"""
Repository Health Dashboard - Interactive Version
Quick overview of repository status with user-friendly pausing
"""

import os
import subprocess
import sys
import time
from datetime import datetime

def pause_for_user(message="Press Enter to continue..."):
    """Pause and wait for user input."""
    try:
        input(f"\n{message}")
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)

def print_header():
    """Print dashboard header."""
    print("🏥 ATERGES REPOSITORY HEALTH DASHBOARD")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def check_repository_size():
    """Check current repository size."""
    print("📊 REPOSITORY SIZE ANALYSIS")
    print("-" * 30)
    
    try:
        # Get repository size information
        result = subprocess.run(['git', 'count-objects', '-v'], 
                              capture_output=True, text=True, cwd='.')
        
        if result.returncode != 0:
            print("❌ Error: Not in a git repository or git not available")
            return 0
        
        lines = result.stdout.strip().split('\n')
        size_kb = 0
        for line in lines:
            if line.startswith('size '):
                size_kb = int(line.split()[1])
                break
        
        size_mb = size_kb / 1024
        
        # Status indicators
        if size_mb < 5:
            status = "🟢 EXCELLENT"
        elif size_mb < 10:
            status = "🟡 GOOD"
        elif size_mb < 25:
            status = "🟠 WARNING"
        else:
            status = "🔴 CRITICAL"
        
        print(f"Repository size: {size_mb:.1f} MB")
        print(f"Status: {status}")
        
        if size_mb > 10:
            print("⚠️  Action needed: Repository too large")
            print("   Recommendation: Run cleanup_repository.py")
        else:
            print("✅ Size is within acceptable range")
        
        return size_mb
        
    except Exception as e:
        print(f"❌ Error checking size: {e}")
        return 0

def check_file_organization():
    """Check file organization quality."""
    print("\n📁 FILE ORGANIZATION")
    print("-" * 30)
    
    try:
        # Count root directory files (excluding hidden files)
        root_files = [f for f in os.listdir('.') 
                      if os.path.isfile(f) and not f.startswith('.')]
        
        print(f"Root directory files: {len(root_files)}")
        
        if len(root_files) > 15:
            print("🔴 TOO MANY - Should be <10")
            print("   Recommendation: Move files to subdirectories")
            print("   📋 Root files:")
            for i, file in enumerate(sorted(root_files)[:10]):
                print(f"      {i+1}. {file}")
            if len(root_files) > 10:
                print(f"      ... and {len(root_files) - 10} more")
        elif len(root_files) > 10:
            print("🟡 MODERATE - Consider organizing")
        else:
            print("🟢 GOOD - Well organized")
        
        # Check for proper directory structure
        expected_dirs = ['docs', 'scripts', 'config', 'backend', 'components']
        existing_dirs = [d for d in expected_dirs if os.path.isdir(d)]
        
        print(f"Standard directories: {len(existing_dirs)}/{len(expected_dirs)}")
        print(f"   Existing: {', '.join(existing_dirs) if existing_dirs else 'None'}")
        
        if len(existing_dirs) < 3:
            print("🟡 Missing standard directories")
            missing = [d for d in expected_dirs if d not in existing_dirs]
            print(f"   Missing: {', '.join(missing)}")
            
    except Exception as e:
        print(f"❌ Error checking organization: {e}")

def check_security_issues():
    """Check for security issues."""
    print("\n🔒 SECURITY SCAN")
    print("-" * 30)
    
    try:
        # Check for sensitive files
        sensitive_patterns = [
            'secret', 'key', 'password', 'credential', 'token'
        ]
        
        issues = []
        for root, dirs, files in os.walk('.'):
            # Skip .git directory
            if '.git' in root:
                continue
            for file in files:
                file_lower = file.lower()
                for pattern in sensitive_patterns:
                    if pattern in file_lower and not file.endswith('.example'):
                        issues.append(os.path.join(root, file))
        
        if issues:
            print(f"🔴 Found {len(issues)} potential security issues:")
            for i, issue in enumerate(issues[:5]):  # Show first 5
                print(f"   {i+1}. ⚠️  {issue}")
            if len(issues) > 5:
                print(f"   ... and {len(issues) - 5} more")
            print("\n   📋 Recommendation: Remove these files or add to .gitignore")
        else:
            print("🟢 No obvious security issues found")
            
    except Exception as e:
        print(f"❌ Error checking security: {e}")

def check_gitignore_effectiveness():
    """Check if .gitignore is working properly."""
    print("\n🚫 GITIGNORE EFFECTIVENESS")
    print("-" * 30)
    
    try:
        # Check for commonly ignored files that might be tracked
        should_ignore = [
            'node_modules', '.next', 'out', '.env', '__pycache__',
            '.DS_Store', '*.log', 'dist', 'build'
        ]
        
        result = subprocess.run(['git', 'ls-files'], 
                              capture_output=True, text=True, cwd='.')
        
        if result.returncode != 0:
            print("❌ Error: Could not check git files")
            return
        
        tracked_files = result.stdout.strip().split('\n')
        
        violations = []
        for pattern in should_ignore:
            clean_pattern = pattern.replace('*', '')
            for file in tracked_files:
                if clean_pattern in file:
                    violations.append(file)
        
        if violations:
            print(f"🟡 Found {len(violations)} files that should probably be ignored:")
            for i, violation in enumerate(violations[:3]):
                print(f"   {i+1}. ⚠️  {violation}")
            if len(violations) > 3:
                print(f"   ... and {len(violations) - 3} more")
        else:
            print("🟢 .gitignore appears to be working well")
            
    except Exception as e:
        print(f"❌ Error checking gitignore: {e}")

def generate_recommendations(size_mb):
    """Generate actionable recommendations."""
    print("\n💡 RECOMMENDATIONS")
    print("-" * 30)
    
    if size_mb > 25:
        print("🚨 URGENT: Repository is critically large (>25MB)")
        print("   1. 🧹 Run: python cleanup_repository.py")
        print("   2. 🔒 Remove sensitive files immediately")
        print("   3. 📁 Reorganize file structure")
        print("   4. 🚫 Update .gitignore")
        
    elif size_mb > 10:
        print("⚠️  HIGH PRIORITY: Repository needs cleanup (>10MB)")
        print("   1. 🧹 Run: python cleanup_repository.py") 
        print("   2. 📁 Move files to proper directories")
        print("   3. 🚫 Update .gitignore")
        
    else:
        print("✅ MAINTENANCE: Keep current good practices")
        print("   1. 🔄 Regular cleanup routine")
        print("   2. 👀 Monitor for new issues")
    
    print("\n🛠️  Available Tools:")
    print("   • python analyze_repo_size.py    - Detailed analysis")
    print("   • python cleanup_repository.py   - Automated cleanup")
    print("   • bash setup_git_lfs.sh         - Large file handling")
    
    print("\n📚 Documentation:")
    print("   • REPOSITORY_BEST_PRACTICES.md  - Complete guide")

def show_quick_actions():
    """Show quick action commands."""
    print("\n🚀 QUICK ACTIONS")
    print("-" * 30)
    print("# Immediate cleanup:")
    print("python cleanup_repository.py")
    print()
    print("# Detailed analysis:")
    print("python analyze_repo_size.py")
    print()
    print("# After cleanup, commit:")
    print("git add .")
    print("git commit -m 'refactor: Repository cleanup and organization'")
    print("git push origin main")

def main():
    """Main dashboard function."""
    try:
        print_header()
        pause_for_user("Press Enter to start analysis...")
        
        size_mb = check_repository_size()
        pause_for_user("Press Enter to check file organization...")
        
        check_file_organization()
        pause_for_user("Press Enter to run security scan...")
        
        check_security_issues()
        pause_for_user("Press Enter to check .gitignore...")
        
        check_gitignore_effectiveness()
        pause_for_user("Press Enter to see recommendations...")
        
        generate_recommendations(size_mb)
        show_quick_actions()
        
        print("\n" + "=" * 60)
        print("🎯 GOAL: Keep repository <10 MB and well-organized")
        print("📈 IMPACT: Better performance, security, and maintainability")
        
        print("\n🏁 ANALYSIS COMPLETE!")
        
        # Ask if user wants to run cleanup
        if size_mb > 10:
            print("\n🤔 Your repository is larger than 10MB.")
            response = input("Would you like to run the cleanup script now? (y/N): ").lower().strip()
            if response == 'y':
                print("\n🧹 Running cleanup script...")
                os.system("python cleanup_repository.py")
            else:
                print("💡 You can run 'python cleanup_repository.py' later")
        
    except KeyboardInterrupt:
        print("\n\n👋 Analysis cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("🔧 Try running from command prompt or check your Python installation")
    
    finally:
        pause_for_user("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
