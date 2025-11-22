#!/usr/bin/env python
"""Run migrations, ignoring 'already exists' errors."""
import sys
import subprocess

result = subprocess.run(
    [sys.executable, 'manage.py', 'migrate', '--noinput'],
    capture_output=True,
    text=True
)

# Check if error is just "already exists" - that's okay
if result.returncode != 0:
    if 'already exists' not in result.stderr.lower():
        # Real error - exit with failure
        print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)
    # "Already exists" is fine - table exists, which is what we want
    print("Some tables already exist (this is okay)")
else:
    print(result.stdout)

sys.exit(0)

