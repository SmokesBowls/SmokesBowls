import subprocess
from pathlib import Path
from datetime import datetime
import time

TEST_DIR = Path("zwx-test-suite")
ZWX_FILES = sorted(TEST_DIR.rglob("*.zwx"))
LOG_PATH = Path("zw_mcp/logs/orbit_test_results.log")
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

def determine_expectation(file_path: Path) -> str:
    name = file_path.name.lower()
    return "fail" if name.startswith("invalid_") else "pass"

def log_result(file_path: Path, passed: bool, expected: str, result_code: int, stdout: str, stderr: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with LOG_PATH.open("a", encoding="utf-8") as log:
        log.write(f"[{timestamp}] {file_path} | Expected: {expected.upper()} | "
                  f"Result: {'PASS' if passed else 'FAIL'} | Exit Code: {result_code}\n")
        if not passed:
            log.write(f"STDOUT:\n{stdout}\nSTDERR:\n{stderr}\n{'-'*60}\n")

def run_all_tests():
    print(f"🔍 Running {len(ZWX_FILES)} tests in '{TEST_DIR}'\n")
    summary = {
        "total": 0,
        "expected_pass": 0,
        "expected_fail": 0,
        "actual_pass": 0,
        "actual_fail": 0,
    }

    for file_path in ZWX_FILES:
        expected = determine_expectation(file_path)
        print(f"🧪 {file_path.relative_to(TEST_DIR)} (expect {expected.upper()})")

        result = subprocess.run(
            ["python3", "tools/engain_orbit.py", str(file_path)],
            capture_output=True,
            text=True
        )

        passed = (result.returncode != 0 if expected == "fail" else result.returncode == 0)
        outcome = "✅ PASS" if passed else "❌ FAIL"
        print(f"→ {outcome} (exit code {result.returncode})\n")

        # Log it
        log_result(file_path, passed, expected, result.returncode, result.stdout, result.stderr)

        summary["total"] += 1
        summary["expected_pass" if expected == "pass" else "expected_fail"] += 1
        summary["actual_pass" if passed else "actual_fail"] += 1
        time.sleep(0.2)

    # Print summary
    print("📊 Test Summary:")
    print(f"  Total:          {summary['total']}")
    print(f"  Expected Pass:  {summary['expected_pass']}")
    print(f"  Expected Fail:  {summary['expected_fail']}")
    print(f"  Actual Pass:    {summary['actual_pass']}")
    print(f"  Actual Fail:    {summary['actual_fail']}")
    print(f"📁 Log written to: {LOG_PATH.resolve()}")

if __name__ == "__main__":
    run_all_tests()
