import sys
from pylint.lint import Run

args = [
    ".",                # Target directory (current directory)
    "--recursive=y",    # Check all subdirectories
    "--errors-only",    # Only check for syntax errors and fatal bugs (ignores style/warnings)
    "--ignore=venv"     # Skip virtual environment folders
]

try:
	results = Run(args, exit=False)

	if results.linter.msg_status != 0:
    		print("\nSyntax or critical errors found!\n")
    		sys.exit(results.linter.msg_status)
	else:
    		print("\nAll files passed syntax checks!")
except (KeyboardInterrupt, EOFError):
	pass
