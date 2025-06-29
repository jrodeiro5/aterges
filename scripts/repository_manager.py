#!/usr/bin/env python3
"""
Aterges Repository Management Launcher
Interactive menu to run various repository management tools
"""

import os
import sys
import subprocess

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the main header."""
    print("🚀 ATERGES REPOSITORY MANAGEMENT TOOLS")
    print("=" * 50)
    print("Choose a tool to help manage your repository:")
    print()

def show_menu():
    """Show the main menu options."""
    print("📊 1. Repository Health Dashboard")
    print("     Quick analysis of size, organization, and security")
    print()
    print("🧹 2. Repository Cleanup & Organization")
    print("     Automated cleanup and file organization")
    print()
    print("📈 3. Detailed Size Analysis")
    print("     In-depth analysis of what's taking up space")
    print()
    print("🔧 4. Git LFS Setup")
    print("     Configure Git LFS for large files")
    print()
    print("📚 5. View Best Practices Guide")
    print("     Open the repository best practices documentation")
    print()
    print("❌ 0. Exit")
    print()

def run_script(script_name, description):
    """Run a Python script with error handling."""
    print(f"\n🚀 Running {description}...")
    print("=" * 50)
    
    try:
        if script_name.endswith('.py'):
            result = subprocess.run([sys.executable, script_name], check=True)
        elif script_name.endswith('.sh'):
            result = subprocess.run(['bash', script_name], check=True)
        else:
            print(f"❌ Unknown script type: {script_name}")
            return False
        
        print(f"\n✅ {description} completed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error running {description}: {e}")
        return False
    except FileNotFoundError:
        print(f"\n❌ Script not found: {script_name}")
        print("Make sure you're running this from the repository root directory.")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

def open_documentation():
    """Open the best practices documentation."""
    doc_file = "REPOSITORY_BEST_PRACTICES.md"
    
    if not os.path.exists(doc_file):
        print(f"\n❌ Documentation not found: {doc_file}")
        return False
    
    try:
        # Try to open with default application
        if os.name == 'nt':  # Windows
            os.startfile(doc_file)
        elif os.name == 'posix':  # macOS and Linux
            subprocess.run(['open', doc_file], check=True)
        else:
            print(f"📖 Please open {doc_file} manually")
        
        print(f"\n📖 Opening {doc_file} with default application...")
        return True
        
    except Exception as e:
        print(f"\n❌ Could not open documentation: {e}")
        print(f"📖 Please open {doc_file} manually")
        return False

def pause_for_user():
    """Pause and wait for user input."""
    try:
        input("\nPress Enter to continue...")
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)

def main():
    """Main launcher function."""
    while True:
        try:
            clear_screen()
            print_header()
            show_menu()
            
            choice = input("Enter your choice (0-5): ").strip()
            
            if choice == '0':
                print("\n👋 Goodbye!")
                break
            
            elif choice == '1':
                run_script('repo_health_dashboard_interactive.py', 'Repository Health Dashboard')
                pause_for_user()
            
            elif choice == '2':
                print("\n⚠️  IMPORTANT: Repository Cleanup will move and reorganize files!")
                print("Make sure you have committed any important changes first.")
                confirm = input("\nContinue with cleanup? (y/N): ").lower().strip()
                if confirm == 'y':
                    run_script('cleanup_repository_interactive.py', 'Repository Cleanup')
                else:
                    print("❌ Cleanup cancelled")
                pause_for_user()
            
            elif choice == '3':
                run_script('analyze_repo_size.py', 'Detailed Size Analysis')
                pause_for_user()
            
            elif choice == '4':
                run_script('setup_git_lfs.sh', 'Git LFS Setup')
                pause_for_user()
            
            elif choice == '5':
                open_documentation()
                pause_for_user()
            
            else:
                print(f"\n❌ Invalid choice: {choice}")
                print("Please enter a number between 0 and 5")
                pause_for_user()
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            pause_for_user()

if __name__ == "__main__":
    main()
