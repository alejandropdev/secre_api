#!/usr/bin/env python3
"""Test runner script with various options."""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, check=True, cwd=Path(__file__).parent.parent)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False
    except FileNotFoundError as e:
        print(f"❌ Command not found: {e}")
        return False


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run tests for Secre API")
    parser.add_argument(
        "--type", 
        choices=["all", "unit", "integration", "auth", "rls", "api", "contracts"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true",
        help="Run with coverage report"
    )
    parser.add_argument(
        "--watch", 
        action="store_true",
        help="Run in watch mode"
    )
    parser.add_argument(
        "--docker", 
        action="store_true",
        help="Run tests using Docker"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Base pytest command
    cmd = ["pytest", "tests/"]
    
    # Add verbosity
    if args.verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    # Add test type markers
    if args.type == "unit":
        cmd.extend(["-m", "unit"])
    elif args.type == "integration":
        cmd.extend(["-m", "integration"])
    elif args.type == "auth":
        cmd.extend(["-m", "auth"])
    elif args.type == "rls":
        cmd.extend(["-m", "rls"])
    elif args.type == "api":
        cmd.extend(["-m", "api"])
    elif args.type == "contracts":
        cmd.extend(["-m", "not (unit or integration or auth or rls or api)"])
    
    # Add coverage
    if args.coverage:
        cmd.extend([
            "--cov=backend/app",
            "--cov-report=html",
            "--cov-report=term-missing",
            "--cov-fail-under=80"
        ])
    
    # Add watch mode
    if args.watch:
        cmd.append("-f")
    
    # Add traceback
    cmd.extend(["--tb=short"])
    
    # Run with Docker if requested
    if args.docker:
        docker_cmd = [
            "docker-compose", 
            "-f", "docker-compose.test.yml", 
            "up", "--build", "--abort-on-container-exit"
        ]
        success = run_command(docker_cmd, f"Docker tests ({args.type})")
    else:
        success = run_command(cmd, f"Tests ({args.type})")
    
    if success:
        print(f"\n🎉 All {args.type} tests passed!")
        if args.coverage:
            print("📊 Coverage report generated in htmlcov/index.html")
    else:
        print(f"\n💥 {args.type} tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
