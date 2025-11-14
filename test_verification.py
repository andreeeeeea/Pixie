"""
Test script for verify_action_succeeded() function
"""

from tools import verify_action_succeeded
import subprocess
import time

print("=" * 50)
print("Testing Verification Function")
print("=" * 50)

# Test 1: Open notepad and verify
print("\n[Test 1] Opening Notepad...")
subprocess.Popen(['notepad.exe'])
time.sleep(2)  # Wait for notepad to open

print("Running verification...")
result = verify_action_succeeded("Opened Notepad application")

print(f"\nResult:")
print(f"  Success: {result['success']}")
print(f"  Explanation: {result['explanation']}")

# Wait for user to close notepad
input("\nClose Notepad and press Enter to continue...")

# Test 2: Verify when notepad is closed
print("\n[Test 2] Verifying Notepad is closed...")
result2 = verify_action_succeeded("Notepad is closed")

print(f"\nResult:")
print(f"  Success: {result2['success']}")
print(f"  Explanation: {result2['explanation']}")

print("\n" + "=" * 50)
print("Testing Complete!")
print("=" * 50)
