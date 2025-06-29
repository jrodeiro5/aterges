#!/usr/bin/env python3
"""
Repository Size Analyzer & Cleanup Tool
Identifies large files and provides cleanup recommendations
"""

import os
import subprocess
import json
from pathlib import Path

def get_repo_size_info():
    """Get information about repository size and large files."""
    print("🔍 REPOSITORY SIZE ANALYSIS")
    print("=" * 50)
    
    try:
        # Get total repository size
        result = subprocess.run(['git', 'count-objects', '-vH'], 
                              capture_output=True, text=True, cwd='.')
        print("📊 Repository Statistics:")
        print(result.stdout)
        
        # Find large files in git history
        print("\n🔍 Finding large files in git history...")
        large_files_cmd = [
            'git', 'rev-list', '--objects', '--all',
            '|', 'git', 'cat-file', '--batch-check="%(objecttype) %(objectname) %(objectsize) %(rest)"',
            '|', 'sed', '-n', 's/^blob //p',
            '|', 'sort', '--numeric-sort', '--key=2',
            '|', 'tail', '-n', '10'
        ]
        
        # Alternative approach for Windows
        try:
            result = subprocess.run(['git', 'ls-tree', '-r', '-t', '-l', '--full-name', 'HEAD'], 
                                  capture_output=True, text=True, cwd='.')
            lines = result.stdout.strip().split('\n')
            
            file_sizes = []
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 4 and parts[1] == 'blob':
                        try:
                            size = int(parts[3])
                            filename = ' '.join(parts[4:])
                            file_sizes.append((size, filename))
                        except (ValueError, IndexError):
                            continue
            
            # Sort by size and show largest files
            file_sizes.sort(reverse=True)
            print("\n📈 Largest files in repository:")
            for size, filename in file_sizes[:15]:
                size_mb = size / (1024 * 1024)
                if size_mb > 0.1:  # Show files larger than 100KB
                    print(f"   {size_mb:.2f} MB - {filename}")
                    
        except Exception as e:
            print(f"   Error analyzing file sizes: {e}")
        
    except Exception as e:
        print(f"Error getting repository info: {e}")

def check_gitignore_effectiveness():
    """Check if .gitignore is working properly."""
    print("\n🚫 GITIGNORE EFFECTIVENESS CHECK")
    print("=" * 50)
    
    # Check for files that should be ignored but aren't
    problematic_patterns = [
        'node_modules/',
        '.next/',
        'out/',
        '.env',
        '.env.local',
        '.env.production',
        '__pycache__/',
        '*.pyc',
        'venv/',
        '.venv/',
        'build/',
        'dist/',
        '.DS_Store',
        '*.log'
    ]
    
    print("Checking for files that should be ignored...")
    
    try:
        # Get list of tracked files
        result = subprocess.run(['git', 'ls-files'], capture_output=True, text=True, cwd='.')
        tracked_files = result.stdout.strip().split('\n')
        
        issues_found = []
        for pattern in problematic_patterns:
            for file in tracked_files:
                if pattern.replace('/', '') in file or pattern in file:
                    issues_found.append(f"   ⚠️  {file} (matches pattern: {pattern})")
        
        if issues_found:
            print("❌ Found files that should probably be ignored:")
            for issue in issues_found[:10]:  # Show first 10
                print(issue)
            if len(issues_found) > 10:
                print(f"   ... and {len(issues_found) - 10} more")
        else:
            print("✅ No obvious gitignore violations found")
            
    except Exception as e:
        print(f"Error checking gitignore: {e}")

def analyze_project_structure():
    """Analyze project structure for organization issues."""
    print("\n📁 PROJECT STRUCTURE ANALYSIS")
    print("=" * 50)
    
    # Count different file types
    file_types = {}
    large_dirs = {}
    root_files = []
    
    for root, dirs, files in os.walk('.'):
        # Skip .git directory
        if '.git' in root:
            continue
            
        # Count files in root
        if root == '.':
            root_files = files
            
        for file in files:
            file_path = os.path.join(root, file)
            try:
                size = os.path.getsize(file_path)
                ext = os.path.splitext(file)[1].lower()
                
                if ext not in file_types:
                    file_types[ext] = {'count': 0, 'size': 0}
                file_types[ext]['count'] += 1
                file_types[ext]['size'] += size
                
                # Track directory sizes
                dir_name = root.split(os.sep)[1] if len(root.split(os.sep)) > 1 else 'root'
                if dir_name not in large_dirs:
                    large_dirs[dir_name] = 0
                large_dirs[dir_name] += size
                
            except OSError:
                continue
    
    print("📊 File type distribution:")
    sorted_types = sorted(file_types.items(), key=lambda x: x[1]['size'], reverse=True)
    for ext, data in sorted_types[:10]:
        size_mb = data['size'] / (1024 * 1024)
        print(f"   {ext or 'no ext'}: {data['count']} files, {size_mb:.2f} MB")
    
    print(f"\n📂 Directory sizes:")
    sorted_dirs = sorted(large_dirs.items(), key=lambda x: x[1], reverse=True)
    for dir_name, size in sorted_dirs[:10]:
        size_mb = size / (1024 * 1024)
        if size_mb > 0.1:
            print(f"   {dir_name}: {size_mb:.2f} MB")
    
    print(f"\n📄 Root directory files ({len(root_files)} files):")
    if len(root_files) > 15:
        print("   ⚠️  Too many files in root directory!")
        print("   Consider organizing into subdirectories")
    for file in sorted(root_files)[:20]:
        print(f"   {file}")
    if len(root_files) > 20:
        print(f"   ... and {len(root_files) - 20} more")

def generate_cleanup_recommendations():
    """Generate specific cleanup recommendations."""
    print("\n🧹 CLEANUP RECOMMENDATIONS")
    print("=" * 50)
    
    recommendations = [
        {
            "priority": "HIGH",
            "issue": "Too many root-level files",
            "action": "Organize documentation and config files into subdirectories",
            "files": ["*.md files", "*.env files", "*.txt files", "test_*.py files"],
            "impact": "Better organization, easier navigation"
        },
        {
            "priority": "HIGH", 
            "issue": "Multiple environment files with secrets",
            "action": "Consolidate and secure environment configuration",
            "files": ["GITHUB_SECRETS_*.txt", "CORRECTED_GITHUB_SECRETS.txt", "VERIFIED_SUPABASE_CONFIG.env"],
            "impact": "Security risk reduction, smaller repo size"
        },
        {
            "priority": "MEDIUM",
            "issue": "Duplicate documentation files",
            "action": "Consolidate similar documentation",
            "files": ["Multiple setup guides", "Redundant status files"],
            "impact": "Cleaner repository, easier maintenance"
        },
        {
            "priority": "MEDIUM",
            "issue": "Test and script files in root",
            "action": "Move to scripts/ or tests/ directory",
            "files": ["test_*.py", "check_*.py", "*_guide.py"],
            "impact": "Better organization"
        },
        {
            "priority": "LOW",
            "issue": "Backup and temporary files",
            "action": "Remove or add to .gitignore",
            "files": ["*.backup", "temp_*.txt", "*.old"],
            "impact": "Cleaner repository"
        }
    ]
    
    for rec in recommendations:
        print(f"\n🔥 {rec['priority']} PRIORITY")
        print(f"   Issue: {rec['issue']}")
        print(f"   Action: {rec['action']}")
        print(f"   Files: {', '.join(rec['files'])}")
        print(f"   Impact: {rec['impact']}")

def suggest_best_practices():
    """Suggest best practices for repository management."""
    print("\n🏆 BEST PRACTICES RECOMMENDATIONS")
    print("=" * 50)
    
    practices = [
        "📁 Directory Structure",
        "   ├── docs/           # All documentation",
        "   ├── scripts/        # Utility scripts", 
        "   ├── tests/          # Test files",
        "   ├── .github/        # GitHub workflows",
        "   ├── backend/        # Backend code",
        "   ├── components/     # Frontend components",
        "   ├── lib/            # Utilities",
        "   └── app/            # Next.js app",
        "",
        "🔒 Security Practices",
        "   • Never commit secrets or API keys",
        "   • Use environment variables for configuration", 
        "   • Add comprehensive .gitignore patterns",
        "   • Review commits before pushing",
        "",
        "📦 Size Management",
        "   • Keep node_modules/ ignored",
        "   • Ignore build artifacts (.next/, out/, dist/)",
        "   • Use Git LFS for large binary files (>50MB)",
        "   • Regularly review repository size",
        "",
        "📚 Documentation",
        "   • Keep main README.md comprehensive but concise",
        "   • Move detailed docs to docs/ directory",
        "   • Use clear naming conventions",
        "   • Avoid duplicate documentation",
        "",
        "🔄 Development Workflow",
        "   • Use meaningful commit messages",
        "   • Keep commits focused and atomic",
        "   • Regular cleanup of temporary files",
        "   • Use branches for features"
    ]
    
    for practice in practices:
        print(practice)

def main():
    """Main analysis function."""
    print("🔍 ATERGES REPOSITORY ANALYSIS & CLEANUP GUIDE")
    print("=" * 60)
    print("Current push size: 76.27 MiB (too large!)")
    print("Target size: <10 MiB for optimal performance")
    print()
    
    get_repo_size_info()
    check_gitignore_effectiveness() 
    analyze_project_structure()
    generate_cleanup_recommendations()
    suggest_best_practices()
    
    print("\n" + "=" * 60)
    print("🎯 NEXT STEPS:")
    print("1. Run the cleanup script (coming next)")
    print("2. Reorganize file structure") 
    print("3. Update .gitignore if needed")
    print("4. Remove sensitive files from git history")
    print("5. Establish development guidelines")
    print("\n💡 Goal: Reduce repository to <10 MiB for better performance!")

if __name__ == "__main__":
    main()
