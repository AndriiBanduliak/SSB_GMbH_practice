# Security Scan: World-Writable & Executable Files

This script scans directories to identify files that are both world-writable and executable. These files represent a potential security risk as they can be modified and executed by any user on the system.  It includes an optional `--delete` flag to remove identified risky files. **USE THE `--delete` FLAG WITH EXTREME CAUTION.** Deleting system files or files required by programs can cause system instability or failure.

## Overview

This script recursively scans specified directories, checking for files that have both world-writable permissions and executable permissions.  It then presents a list of these potentially risky files to the user. The `--delete` flag allows the user to automatically delete the identified files (again, with extreme caution).

## Prerequisites

*   Python 3
*   The `pandas` library (for potential future expansion - currently not used but included for possible future use)

## Installation

1.  Save the code as a Python file (e.g., `security_scan.py`).
2.  Make the script executable: `chmod +x security_scan.py`
3.  Run the script using: `./security_scan.py <directory1> <directory2> ...`

## Usage

```bash
./security_scan.py /path/to/directory1 /path/to/directory2 ...
```

*   Replace `/path/to/directory1`, `/path/to/directory2`, etc., with the directories you want to scan.  You can specify multiple directories.
*   To delete identified files, add the `--delete` flag: `./security_scan.py /path/to/directory1 --delete`

## Arguments

*   `<directory1> <directory2> ...`: One or more directories to scan recursively. (Required)
*   `--delete`:  Enables automatic deletion of identified risky files. **USE WITH EXTREME CAUTION.** (Optional)

## Code Explanation

The script is structured as follows:

1.  **Import Libraries:** Imports necessary modules (`os`, `stat`, `argparse`).
2.  **`is_world_writable(path)` Function:** Checks if a given file or directory is world-writable using the `st_mode` attribute and the `S_IWOTH` bit. Handles potential errors like `FileNotFoundError` and `PermissionError`.
3.  **`is_executable(path)` Function:** Checks if a file is executable using `os.access()` with `os.X_OK`. This function handles Windows-specific execution checks.
4.  **`scan_directory(path)` Function:** Recursively scans a directory, checking each file and subdirectory for world-writable and executable permissions. It uses `os.walk()` to traverse the directory tree. Includes error handling for permission issues during directory access.
5.  **`delete_file(file_path)` Function:** Attempts to delete a single file. Handles potential errors like `FileNotFoundError`, `PermissionError`, and OS-level errors.
6.  **`main()` Function:**
    *   Parses command-line arguments using `argparse`.
    *   Iterates through the specified directories, calling `scan_directory()` for each.
    *   If `--delete` is specified, it iterates through the identified risky files and calls `delete_file()` to remove them.
    *   Prints informative messages throughout the process.

## Contributing

Contributions are welcome! Please follow these guidelines:

1.  Fork the repository.
2.  Create a new branch for your changes: `git checkout -b my-feature`
3.  Make your changes and commit them: `git commit -m "Add my feature"`
4.  Push your branch to your fork: `git push origin my-feature`
5.  Submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE). See the `LICENSE` file for details.