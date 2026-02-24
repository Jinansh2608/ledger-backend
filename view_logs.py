#!/usr/bin/env python3
"""
Live log viewer for NexGen Finance API
Shows real-time logs as requests come in
"""
import os
import sys
import time
from pathlib import Path
from datetime import datetime

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def tail_file(filepath, num_lines=50):
    """Read last N lines from a file"""
    if not os.path.exists(filepath):
        return []
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    return lines[-num_lines:] if lines else []

def print_header(title):
    """Print a formatted header"""
    width = 80
    print("\n" + "="*width)
    print(f"  {title}")
    print("="*width + "\n")

def view_live_logs():
    """View logs in real-time (tail mode)"""
    log_file = Path("logs/app.log")
    
    if not log_file.exists():
        print("❌ No logs found yet. Start the server first:")
        print("   python run.py")
        return
    
    print("\n📊 Watching live logs... (Ctrl+C to stop)")
    print("="*80)
    
    # Get initial position
    last_size = os.path.getsize(log_file)
    
    try:
        while True:
            current_size = os.path.getsize(log_file)
            
            if current_size >= last_size:
                # File grew or same, read from last position
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    f.seek(last_size)
                    new_lines = f.readlines()
                    
                for line in new_lines:
                    # Colorize log levels
                    if 'ERROR' in line or '[40m' in line:
                        print(f"\033[91m{line.rstrip()}\033[0m")  # Red
                    elif 'WARNING' in line:
                        print(f"\033[93m{line.rstrip()}\033[0m")  # Yellow
                    elif 'INFO' in line:
                        print(f"\033[92m{line.rstrip()}\033[0m")   # Green
                    elif 'DEBUG' in line:
                        print(f"\033[94m{line.rstrip()}\033[0m")   # Blue
                    else:
                        print(line.rstrip())
                
                last_size = current_size
            else:
                # File was rotated
                last_size = 0
            
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n\n✋ Log viewing stopped")
        return

def view_recent_logs(num_lines=100):
    """View recent logs (one-time view)"""
    log_file = Path("logs/app.log")
    
    if not log_file.exists():
        print("❌ No logs found. Start the server first: python run.py")
        return
    
    print_header(f"📋 Last {num_lines} Log Entries")
    lines = tail_file(str(log_file), num_lines)
    
    for line in lines:
        # Colorize
        if 'ERROR' in line:
            print(f"\033[91m{line.rstrip()}\033[0m")
        elif 'WARNING' in line:
            print(f"\033[93m{line.rstrip()}\033[0m")
        elif 'GET ' in line or 'POST ' in line or 'PUT ' in line or 'DELETE ' in line:
            print(f"\033[92m{line.rstrip()}\033[0m")
        else:
            print(line.rstrip())

def view_error_logs(num_lines=50):
    """View error logs"""
    log_file = Path("logs/error.log")
    
    if not log_file.exists():
        print("✅ No errors logged yet!")
        return
    
    print_header(f"⚠️  Last {num_lines} Errors")
    lines = tail_file(str(log_file), num_lines)
    
    for line in lines:
        print(f"\033[91m{line.rstrip()}\033[0m")

def view_api_calls(num_lines=50):
    """Filter and show only API calls"""
    log_file = Path("logs/app.log")
    
    if not log_file.exists():
        print("❌ No logs found.")
        return
    
    print_header(f"🔌 Last {num_lines} API Calls")
    
    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
        all_lines = f.readlines()
    
    api_calls = [line for line in all_lines 
                 if any(method in line for method in ['GET ', 'POST ', 'PUT ', 'DELETE '])]
    
    api_calls = api_calls[-num_lines:]
    
    for line in api_calls:
        if '200' in line or '201' in line:
            print(f"\033[92m{line.rstrip()}\033[0m")  # Green for success
        elif '400' in line or '422' in line:
            print(f"\033[93m{line.rstrip()}\033[0m")  # Yellow for client errors
        elif '500' in line:
            print(f"\033[91m{line.rstrip()}\033[0m")  # Red for server errors
        else:
            print(line.rstrip())

def show_log_stats():
    """Show statistics about logs"""
    log_file = Path("logs/app.log")
    error_file = Path("logs/error.log")
    
    print_header("📊 Log Statistics")
    
    if log_file.exists():
        size_mb = log_file.stat().st_size / (1024*1024)
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = len(f.readlines())
        print(f"📄 App Logs:")
        print(f"   • File: logs/app.log")
        print(f"   • Lines: {lines:,}")
        print(f"   • Size: {size_mb:.2f} MB")
        print(f"   • Max: 10 MB (rotates when full)")
    
    if error_file.exists():
        size_mb = error_file.stat().st_size / (1024*1024)
        with open(error_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = len(f.readlines())
        print(f"\n❌ Error Logs:")
        print(f"   • File: logs/error.log")
        print(f"   • Lines: {lines:,}")
        print(f"   • Size: {size_mb:.2f} MB")
        print(f"   • Max: 10 MB (rotates when full)")

def show_menu():
    """Show interactive menu"""
    while True:
        print("\n" + "="*80)
        print("  📊 NexGen Finance API - Log Viewer")
        print("="*80)
        print("\n1. 📊 View live logs (real-time)")
        print("2. 📋 View recent logs (last 100 lines)")
        print("3. 🔌 View API calls only (last 50)")
        print("4. ⚠️  View error logs (last 50)")
        print("5. 📈 View log statistics")
        print("6. 🔄 Clear logs and start fresh")
        print("7. ❌ Exit")
        print("\n" + "-"*80)
        
        choice = input("\nSelect option (1-7): ").strip()
        
        if choice == "1":
            view_live_logs()
        elif choice == "2":
            view_recent_logs(100)
        elif choice == "3":
            view_api_calls(50)
        elif choice == "4":
            view_error_logs(50)
        elif choice == "5":
            show_log_stats()
        elif choice == "6":
            if input("\n⚠️  Clear all logs? (y/n): ").lower() == 'y':
                for f in ["logs/app.log", "logs/error.log"]:
                    if os.path.exists(f):
                        os.remove(f)
                print("✅ Logs cleared")
        elif choice == "7":
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid option")

if __name__ == "__main__":
    # Check for command-line arguments
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        
        if cmd == "live" or cmd == "-l":
            view_live_logs()
        elif cmd == "api" or cmd == "-a":
            view_api_calls(50)
        elif cmd == "errors" or cmd == "-e":
            view_error_logs(50)
        elif cmd == "stats" or cmd == "-s":
            show_log_stats()
        elif cmd == "recent" or cmd == "-r":
            num = int(sys.argv[2]) if len(sys.argv) > 2 else 100
            view_recent_logs(num)
        elif cmd == "help" or cmd == "-h":
            print("""
Usage: python view_logs.py [COMMAND]

Commands:
  live              View logs in real-time
  api               View only API calls
  errors            View errors only
  stats             Show log statistics
  recent [N]        View last N lines (default 100)
  help              Show this help

Examples:
  python view_logs.py live              # Real-time log streaming
  python view_logs.py api               # API calls only
  python view_logs.py recent 200        # Last 200 lines
  python view_logs.py --help            # This page
            """)
        else:
            print(f"❌ Unknown command: {cmd}")
            print("Run: python view_logs.py --help")
    else:
        # Interactive menu
        show_menu()
