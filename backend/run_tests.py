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
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Port configuration from environment variables
LIVE_PORT = int(os.getenv("FLASK_RUN_PORT", 5001))
TEST_PORT = int(os.getenv("FLASK_TEST_PORT", 5002))

# Test type constants
TEST_TYPE_UNIT = "unit"
TEST_TYPE_INTEGRATION = "integration"
TEST_TYPE_ALL = "all"

# Valid test types
VALID_TEST_TYPES = [TEST_TYPE_UNIT, TEST_TYPE_INTEGRATION, TEST_TYPE_ALL]


def check_for_live_server():
    """Check if Flask server is running on configured ports"""
    ports_to_check = [LIVE_PORT, TEST_PORT]
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
                f"   Please manually ensure no Flask servers are running on ports {LIVE_PORT}-{TEST_PORT}"
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


def run_tests(test_type=TEST_TYPE_ALL, verbose=False, stop_on_first_failure=False):
    """Run tests with safety checks"""

    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)

    print("🧪 Tournament Widget Test Runner")
    print("=" * 50)

    # Check for live servers
    servers_running, servers_info = check_for_live_server()
    test_port = TEST_PORT

    if servers_running:
        print("⚠️  WARNING: Live Flask server(s) detected:")
        for port, pid in servers_info:
            print(f"   Live server: Port {port} (PID: {pid})")

        print(f"📋 Test configuration:")
        print(f"   Tests will run on: Port {test_port}")
        print(f"   Tests use isolated databases (no data conflicts)")

        # Check if there's a port conflict
        live_ports = [port for port, _ in servers_info]
        has_conflict = test_port in live_ports

        if has_conflict:
            print(f"❌ PORT CONFLICT: Live server running on test port {test_port}!")
            default_choice = "y"
            prompt = "Do you want to stop the conflicting server? (Y/n): "
        else:
            print(
                f"✅ No port conflict detected (live: {live_ports}, test: {test_port})"
            )
            default_choice = "n"
            prompt = "Do you want to stop live servers anyway? (y/N): "

        response = input(prompt).strip().lower()

        # Use default if user just presses enter
        if not response:
            response = default_choice
            print(f"   Using default: {response}")

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
            if has_conflict:
                print("⚠️  WARNING: Proceeding with port conflict - tests may fail!")
            else:
                print("✅ Continuing with live servers running (safe - no conflicts)")
            print(f"   Tests will use isolated databases and port {test_port}")

    # Set test environment variables
    os.environ["TESTING"] = "true"
    os.environ["FLASK_ENV"] = "testing"
    os.environ["FLASK_RUN_PORT"] = str(TEST_PORT)  # Use test port from config

    # Build pytest command
    cmd = ["python", "-m", "pytest"]

    if verbose:
        cmd.append("-v")

    if stop_on_first_failure:
        cmd.append("-x")

    # Add test selection based on type
    if test_type == TEST_TYPE_UNIT:
        cmd.extend(["-m", "unit"])
        print("\n🔬 Running UNIT tests only...")
    elif test_type == TEST_TYPE_INTEGRATION:
        cmd.extend(["-m", "integration"])
        print("\n🔗 Running INTEGRATION tests only...")
    elif test_type == TEST_TYPE_ALL:
        cmd.append("tests/")
        print("\n🎯 Running ALL tests...")
    else:
        print(f"❌ Unknown test type: {test_type}")
        print(f"   Available options: {', '.join(VALID_TEST_TYPES)}")
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
        default=TEST_TYPE_ALL,
        choices=VALID_TEST_TYPES,
        help=f"Type of tests to run (default: {TEST_TYPE_ALL})",
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
