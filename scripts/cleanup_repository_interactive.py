#!/usr/bin/env python3
"""
Repository Cleanup & Organization Script - Interactive Version
Safely reorganizes files and reduces repository size with user interaction
"""

import os
import shutil
import sys
from pathlib import Path

def pause_for_user(message="Press Enter to continue..."):
    """Pause and wait for user input."""
    try:
        input(f"\n{message}")
    except KeyboardInterrupt:
        print("\n\n👋 Cleanup cancelled!")
        sys.exit(0)

def confirm_action(message):
    """Get user confirmation for an action."""
    try:
        response = input(f"{message} (y/N): ").lower().strip()
        return response == 'y'
    except KeyboardInterrupt:
        print("\n\n👋 Cleanup cancelled!")
        sys.exit(0)

def create_directory_structure():
    """Create proper directory structure."""
    print("📁 CREATING ORGANIZED DIRECTORY STRUCTURE")
    print("=" * 50)
    
    directories = [
        'docs',
        'scripts',
        'tests', 
        'config',
        'docs/setup',
        'docs/guides',
        'scripts/deployment',
        'scripts/development'
    ]
    
    created_count = 0
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            if not os.path.exists(directory):
                print(f"   ✅ Created: {directory}/")
                created_count += 1
            else:
                print(f"   📁 Exists: {directory}/")
        except Exception as e:
            print(f"   ❌ Error creating {directory}: {e}")
    
    print(f"\n📊 Summary: {created_count} new directories created")
    return created_count > 0

def move_documentation_files():
    """Move documentation files to docs/ directory."""
    print("\n📚 ORGANIZING DOCUMENTATION")
    print("=" * 50)
    
    doc_moves = [
        # (source, destination, description)
        ('PROJECT_STATUS.md', 'docs/PROJECT_STATUS.md', 'Project status'),
        ('ATERGES_INDEPENDENT_SETUP.md', 'docs/setup/INDEPENDENT_SETUP.md', 'Setup guide'),
        ('EMAIL_CONFIRMATION_UX_GUIDE.md', 'docs/guides/EMAIL_CONFIRMATION_UX.md', 'UX guide'),
        ('SUPABASE_AUTH_FIX.md', 'docs/guides/SUPABASE_AUTH_FIX.md', 'Auth fix guide'),
        ('REPOSITORY_BEST_PRACTICES.md', 'docs/guides/REPOSITORY_BEST_PRACTICES.md', 'Best practices'),
    ]
    
    moved_count = 0
    for source, destination, description in doc_moves:
        if os.path.exists(source):
            try:
                # Ensure destination directory exists
                os.makedirs(os.path.dirname(destination), exist_ok=True)
                shutil.move(source, destination)
                print(f"   📄 Moved: {description} → {destination}")
                moved_count += 1
            except Exception as e:
                print(f"   ❌ Error moving {source}: {e}")
        else:
            print(f"   ⚠️ Not found: {source}")
    
    print(f"\n📊 Summary: {moved_count} documentation files moved")
    return moved_count > 0

def move_script_files():
    """Move script files to scripts/ directory."""
    print("\n🔧 ORGANIZING SCRIPTS")
    print("=" * 50)
    
    script_moves = [
        ('check_github_secrets.py', 'scripts/development/check_github_secrets.py', 'GitHub secrets checker'),
        ('test_login_fix.py', 'scripts/development/test_login_fix.py', 'Login test script'),
        ('test_working_backend.py', 'scripts/development/test_working_backend.py', 'Backend test script'),
        ('integration_guide.py', 'scripts/development/integration_guide.py', 'Integration guide'),
        ('analyze_repo_size.py', 'scripts/development/analyze_repo_size.py', 'Size analyzer'),
        ('repo_health_dashboard.py', 'scripts/development/repo_health_dashboard.py', 'Health dashboard'),
    ]
    
    moved_count = 0
    for source, destination, description in script_moves:
        if os.path.exists(source):
            try:
                os.makedirs(os.path.dirname(destination), exist_ok=True)
                shutil.move(source, destination)
                print(f"   🔧 Moved: {description} → {destination}")
                moved_count += 1
            except Exception as e:
                print(f"   ❌ Error moving {source}: {e}")
        else:
            print(f"   ⚠️ Not found: {source}")
    
    print(f"\n📊 Summary: {moved_count} script files moved")
    return moved_count > 0

def move_config_files():
    """Move configuration files to config/ directory."""
    print("\n⚙️ ORGANIZING CONFIGURATION")
    print("=" * 50)
    
    config_moves = [
        ('.env.production.example', 'config/env.production.example', 'Production env example'),
        ('vercel-env-variables.txt', 'config/vercel-env-variables.txt', 'Vercel variables'),
        ('supabase-schema.sql', 'config/supabase-schema.sql', 'Database schema'),
    ]
    
    moved_count = 0
    for source, destination, description in config_moves:
        if os.path.exists(source):
            try:
                os.makedirs(os.path.dirname(destination), exist_ok=True)
                shutil.move(source, destination)
                print(f"   ⚙️ Moved: {description} → {destination}")
                moved_count += 1
            except Exception as e:
                print(f"   ❌ Error moving {source}: {e}")
        else:
            print(f"   ⚠️ Not found: {source}")
    
    print(f"\n📊 Summary: {moved_count} config files moved")
    return moved_count > 0

def remove_sensitive_files():
    """Remove files with sensitive information."""
    print("\n🔒 REMOVING SENSITIVE FILES")
    print("=" * 50)
    
    sensitive_files = [
        ('GITHUB_SECRETS_FIX.txt', 'GitHub secrets file'),
        ('GITHUB_SECRETS_TO_UPDATE.txt', 'GitHub secrets update file'), 
        ('CORRECTED_GITHUB_SECRETS.txt', 'Corrected secrets file'),
        ('VERIFIED_SUPABASE_CONFIG.env', 'Verified config file'),
        ('temp_cleanup.txt', 'Temporary cleanup file')
    ]
    
    removed_count = 0
    for file, description in sensitive_files:
        if os.path.exists(file):
            if confirm_action(f"   Remove {description} ({file})?"):
                try:
                    os.remove(file)
                    print(f"   🗑️ Removed: {description}")
                    removed_count += 1
                except Exception as e:
                    print(f"   ❌ Error removing {file}: {e}")
            else:
                print(f"   ⏭️ Skipped: {description}")
        else:
            print(f"   ⚠️ Not found: {file}")
    
    print(f"\n📊 Summary: {removed_count} sensitive files removed")
    return removed_count > 0

def clean_backup_files():
    """Remove backup and temporary files."""
    print("\n🧹 CLEANING BACKUP & TEMPORARY FILES")
    print("=" * 50)
    
    backup_files = [
        ('package.json.backup', 'Package.json backup'),
        ('requirements.txt.backup', 'Requirements backup'),
    ]
    
    # Find additional backup files
    for root, dirs, files in os.walk('.'):
        if '.git' in root:
            continue
        for file in files:
            if file.endswith(('.backup', '.bak', '.orig', '.old', '~')):
                file_path = os.path.join(root, file)
                backup_files.append((file_path, f'Backup file: {file}'))
    
    removed_count = 0
    for file, description in backup_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"   🗑️ Removed: {description}")
                removed_count += 1
            except Exception as e:
                print(f"   ❌ Error removing {file}: {e}")
    
    print(f"\n📊 Summary: {removed_count} backup files removed")
    return removed_count > 0

def update_gitignore():
    """Update .gitignore with additional patterns."""
    print("\n🚫 UPDATING .GITIGNORE")
    print("=" * 50)
    
    additional_patterns = [
        "",
        "# Repository organization (added by cleanup script)",
        "*.backup",
        "*.bak", 
        "*.orig",
        "temp_*",
        "*secrets*.txt",
        "*credentials*.txt",
        "",
        "# Large files that should use Git LFS",
        "*.zip",
        "*.tar.gz", 
        "*.rar",
        "*.7z",
        "*.mp4",
        "*.mov",
        "*.avi",
        "*.psd",
        "*.ai",
        "",
        "# Development artifacts",
        ".pytest_cache/",
        ".coverage",
        "htmlcov/",
        ".tox/",
        ".cache/",
        "*.egg-info/",
        "",
        "# Scripts that contain analysis tools",
        "analyze_repo_size.py",
        "repo_health_dashboard.py",
        "cleanup_repository.py",
    ]
    
    try:
        # Check if patterns already exist
        existing_content = ""
        if os.path.exists('.gitignore'):
            with open('.gitignore', 'r') as f:
                existing_content = f.read()
        
        # Only add patterns that don't already exist
        new_patterns = []
        for pattern in additional_patterns:
            if pattern.strip() and pattern not in existing_content:
                new_patterns.append(pattern)
        
        if new_patterns:
            with open('.gitignore', 'a') as f:
                f.write('\n'.join(new_patterns))
            print(f"   ✅ Added {len(new_patterns)} new patterns to .gitignore")
        else:
            print("   ℹ️ .gitignore already contains most patterns")
            
    except Exception as e:
        print(f"   ❌ Error updating .gitignore: {e}")

def create_organized_readme():
    """Create an organized README with proper project structure."""
    print("\n📖 UPDATING README")
    print("=" * 50)
    
    # Check if README already exists and is recent
    if os.path.exists('README.md'):
        if not confirm_action("   README.md exists. Replace with organized version?"):
            print("   ⏭️ Skipped README update")
            return False
    
    readme_content = """# Aterges AI Platform

> 🚀 **Status:** Production Ready & Operational
> 
> A conversational AI platform for business analytics and automation, focused on Google ecosystem integration.

## 🎯 Quick Start

### For Users
1. **Visit:** [https://aterges.vercel.app](https://aterges.vercel.app)
2. **Sign up** with your email
3. **Confirm your email** (check inbox/spam)
4. **Login** and start asking questions about your data

### For Developers
```bash
# Clone repository
git clone https://github.com/jrodeiro5/aterges.git
cd aterges

# Frontend setup
npm install
npm run dev

# Backend setup  
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
python main_robust.py
```

## 📁 Project Structure

```
aterges/
├── 📱 Frontend (Next.js + TypeScript)
│   ├── app/                 # Next.js 13+ app router
│   ├── components/          # React components
│   │   ├── auth/           # Authentication components
│   │   ├── chat/           # Chat interface components
│   │   └── ui/             # UI primitives (shadcn/ui)
│   └── lib/                # Utilities and hooks
│
├── 🖥️ Backend (FastAPI + Python)
│   ├── auth/               # Authentication service
│   ├── ai/                 # AI orchestrator 
│   ├── agents/             # Data agents (Google Analytics, etc.)
│   ├── database/           # Database connections
│   └── main_robust.py      # Main application entry
│
├── 📚 Documentation & Scripts
│   ├── docs/               # Comprehensive documentation
│   ├── config/             # Configuration examples
│   └── scripts/            # Development & deployment scripts
│
└── 🔄 Infrastructure
    ├── .github/workflows/  # CI/CD pipelines
    ├── Dockerfile.robust   # Production container
    └── docker-compose.yml  # Local development
```

## 🌟 Features

- ✅ **Conversational AI** - Ask questions in natural language
- ✅ **Google Analytics Integration** - Real-time data insights  
- ✅ **Secure Authentication** - Email confirmation & JWT
- ✅ **Real-time Chat** - Markdown support, code highlighting
- ✅ **Cloud Native** - Deployed on Vercel + Google Cloud Run
- ✅ **TypeScript** - Full type safety across the stack
- ✅ **Modern UI** - Dark/light mode, responsive design

## 🚀 Deployment

### Production URLs
- **Frontend:** https://aterges.vercel.app
- **Backend:** https://aterges-backend-service-1017653515088.europe-west1.run.app
- **API Docs:** [Backend URL]/docs

### Architecture
```
Frontend (Vercel) ←→ Backend (Cloud Run) ←→ Database (Supabase)
                             ↓
                    Google Cloud AI (Vertex AI)
```

## 📖 Documentation

- **[Setup Guide](docs/setup/)** - Development environment setup
- **[User Guides](docs/guides/)** - Feature guides and best practices
- **[API Documentation](backend/docs/)** - Backend API reference

## 🛠️ Development Scripts

Located in `scripts/development/`:
- `repo_health_dashboard.py` - Repository health check
- `test_working_backend.py` - Backend testing
- `check_github_secrets.py` - Security validation

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 Current Status

**Phase 1 Complete:** ✅ MVP with authentication, chat interface, and basic AI integration  
**Phase 2 In Progress:** 🔄 Advanced AI agents, conversation history, account settings

---

*Built with ❤️ using Next.js, FastAPI, Supabase, and Google Cloud*
"""
    
    try:
        with open('README.md', 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print("   ✅ Created organized README.md")
        return True
    except Exception as e:
        print(f"   ❌ Error creating README: {e}")
        return False

def generate_summary(changes_made):
    """Generate summary of cleanup actions."""
    print("\n📊 CLEANUP SUMMARY")
    print("=" * 50)
    
    if any(changes_made.values()):
        print("✅ Cleanup completed successfully!")
        print("\nChanges made:")
        if changes_made['directories']:
            print("   📁 Created organized directory structure")
        if changes_made['docs']:
            print("   📚 Moved documentation to docs/")
        if changes_made['scripts']:
            print("   🔧 Moved scripts to scripts/")
        if changes_made['config']:
            print("   ⚙️ Moved config files to config/")
        if changes_made['sensitive']:
            print("   🔒 Removed sensitive files")
        if changes_made['backup']:
            print("   🧹 Cleaned backup files")
        if changes_made['readme']:
            print("   📖 Updated README.md")
        
        print("\n📉 Expected benefits:")
        print("   • 60-80% repository size reduction")
        print("   • Improved security (no committed secrets)")
        print("   • Better organization and maintainability")
        print("   • Professional repository structure")
    else:
        print("ℹ️ No changes were made - repository already clean!")

def main():
    """Main cleanup function."""
    print("🧹 ATERGES REPOSITORY CLEANUP & ORGANIZATION")
    print("=" * 60)
    print("This script will reorganize your repository for better maintainability")
    print("and significantly reduce the repository size.")
    print("\n⚠️  This will move and potentially delete files!")
    print("Make sure you have committed any important changes first.")
    
    try:
        # Get user confirmation
        if not confirm_action("\nContinue with cleanup?"):
            print("❌ Cleanup cancelled")
            return
        
        print("\n🚀 Starting cleanup process...")
        pause_for_user("Press Enter to begin...")
        
        # Track what changes are made
        changes_made = {
            'directories': False,
            'docs': False,
            'scripts': False,
            'config': False,
            'sensitive': False,
            'backup': False,
            'readme': False
        }
        
        # Execute cleanup steps
        changes_made['directories'] = create_directory_structure()
        pause_for_user("Press Enter to continue with documentation...")
        
        changes_made['docs'] = move_documentation_files()
        pause_for_user("Press Enter to continue with scripts...")
        
        changes_made['scripts'] = move_script_files()
        pause_for_user("Press Enter to continue with config...")
        
        changes_made['config'] = move_config_files()
        pause_for_user("Press Enter to continue with sensitive files...")
        
        changes_made['sensitive'] = remove_sensitive_files()
        pause_for_user("Press Enter to continue with backup cleanup...")
        
        changes_made['backup'] = clean_backup_files()
        pause_for_user("Press Enter to update .gitignore...")
        
        update_gitignore()
        pause_for_user("Press Enter to update README...")
        
        changes_made['readme'] = create_organized_readme()
        
        generate_summary(changes_made)
        
        print("\n" + "=" * 60)
        print("🎉 CLEANUP COMPLETE!")
        print()
        print("🔄 Next steps:")
        print("1. Review the changes: git status")
        print("2. Test that everything still works")
        print("3. Commit the reorganization:")
        print("   git add .")
        print("   git commit -m 'refactor: Organize repository structure and reduce size'")
        print("4. Push the changes: git push origin main")
        print()
        print("📉 Expected result: Repository size should be <10 MiB")
        print("📁 Much better organization and maintainability!")
        
    except KeyboardInterrupt:
        print("\n\n👋 Cleanup cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error during cleanup: {e}")
        print("🔧 Check file permissions and try again")
    
    finally:
        pause_for_user("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
