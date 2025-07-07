#!/usr/bin/env python3
"""
Safe test runner script that prevents accidental testing against live servers
"""
import os
import signal
import subprocess
import sys
from pathlib import Path

import psutil


def check_for_live_server():
    """Check if Flask server is running on ports 5001 or 5002"""
    ports_to_check = [5001, 5002]
    servers_found = []

    try:
        for conn in psutil.net_connections():
            if conn.laddr.port in ports_to_check and conn.status == psutil.CONN_LISTEN:
                servers_found.append((conn.laddr.port, conn.pid))

        if servers_found:
            return True, servers_found
        return False, None
    except (psutil.AccessDenied, PermissionError):
        # On macOS, psutil might need special permissions
        # Fall back to using lsof command
        try:
            for port in ports_to_check:
                result = subprocess.run(
                    ["lsof", "-i", f":{port}", "-t"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode == 0 and result.stdout.strip():
                    pid = int(result.stdout.strip().split("\n")[0])
                    servers_found.append((port, pid))

            if servers_found:
                return True, servers_found
            return False, None
        except (subprocess.SubprocessError, ValueError, FileNotFoundError):
            # lsof not available or other error
            print("⚠️  Cannot check for live servers (permission denied)")
            print(
                "   Please manually ensure no Flask servers are running on ports 5001-5002"
            )
            return False, None


def kill_live_server(pid):
    """Kill the live server process"""
    try:
        os.kill(pid, signal.SIGTERM)
        print(f"✅ Killed live server process {pid}")
        return True
    except ProcessLookupError:
        print(f"⚠️  Process {pid} not found (may have already exited)")
        return True
    except PermissionError:
        print(f"❌ Permission denied to kill process {pid}")
        return False


def run_tests(test_type="all", verbose=False, stop_on_first_failure=False):
    """Run tests with safety checks"""

    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)

    print("🧪 Tournament Widget Test Runner")
    print("=" * 50)

    # Check for live servers
    servers_running, servers_info = check_for_live_server()
    if servers_running:
        print("⚠️  WARNING: Live Flask server(s) detected:")
        for port, pid in servers_info:
            print(f"   Port {port} (PID: {pid})")

        response = (
            input("Do you want to stop them before running tests? (y/N): ")
            .strip()
            .lower()
        )

        if response == "y":
            all_stopped = True
            for port, pid in servers_info:
                if kill_live_server(pid):
                    print(f"✅ Stopped server on port {port} (PID: {pid})")
                else:
                    print(f"❌ Failed to stop server on port {port} (PID: {pid})")
                    all_stopped = False

            if not all_stopped:
                print(
                    "❌ Some servers could not be stopped. Please stop them manually."
                )
                return False
        else:
            print("⚠️  Continuing with live server(s) running (not recommended)")
            print(
                "   Tests will use isolated test databases and port 5002, but be careful!"
            )

    # Set test environment variables
    os.environ["TESTING"] = "true"
    os.environ["FLASK_ENV"] = "testing"
    os.environ["FLASK_RUN_PORT"] = "5002"  # Use different port for tests

    # Build pytest command
    cmd = ["python", "-m", "pytest"]

    if verbose:
        cmd.append("-v")

    if stop_on_first_failure:
        cmd.append("-x")

    # Add test selection based on type
    if test_type == "unit":
        cmd.extend(["-m", "unit"])
        print("\n🔬 Running UNIT tests only...")
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
        print("\n🔗 Running INTEGRATION tests only...")
    elif test_type == "safe":
        cmd.extend(
            [
                "tests/test_app.py",
                "tests/test_integration_safe.py",
                "tests/test_odd_tournament.py",
                "tests/test_tournament_creation.py",
            ]
        )
        print("\n🛡️  Running SAFE tests (no live server dependencies)...")
    elif test_type == "all":
        cmd.append("tests/")
        print("\n🎯 Running ALL tests...")
    else:
        print(f"❌ Unknown test type: {test_type}")
        return False

    # Add coverage if available
    try:
        import coverage

        cmd.extend(["--cov=.", "--cov-report=term-missing"])
        print("📊 Coverage reporting enabled")
    except ImportError:
        print("📊 Coverage not available (install with: pip install pytest-cov)")

    print(f"\n🚀 Running command: {' '.join(cmd)}")
    print("-" * 50)

    # Run tests
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode == 0
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        return False
    finally:
        # Clean up environment variables
        os.environ.pop("TESTING", None)
        os.environ.pop("FLASK_ENV", None)
        os.environ.pop("FLASK_RUN_PORT", None)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Safe test runner for Tournament Widget"
    )
    parser.add_argument(
        "test_type",
        nargs="?",
        default="safe",
        choices=["unit", "integration", "safe", "all"],
        help="Type of tests to run (default: safe)",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument(
        "-x", "--stop-on-first", action="store_true", help="Stop on first failure"
    )

    args = parser.parse_args()

    success = run_tests(
        test_type=args.test_type,
        verbose=args.verbose,
        stop_on_first_failure=args.stop_on_first,
    )

    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
