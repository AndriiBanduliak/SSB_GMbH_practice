#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Scan directories to find files that are both world-writable and executable.
These files represent a potential security risk as they can be modified
and executed by any user on the system.

Includes an optional --delete flag to remove identified risky files.
USE THE --delete FLAG WITH EXTREME CAUTION. DELETING SYSTEM FILES
OR FILES REQUIRED BY PROGRAMS CAN CAUSE SYSTEM INSTABILITY OR FAILURE.
"""

import os
import stat
import argparse
from typing import List

def is_world_writable(path: str) -> bool:
    """
    Checks if a file or directory is world-writable.

    Args:
        path: The path to the file or directory.

    Returns:
        True if the path exists and is world-writable, False otherwise or on error.
    """
    try:
        # Get the mode of the file/directory
        mode = os.stat(path).st_mode
        # Check if the world-writable bit is set (for 'other' users)
        return bool(mode & stat.S_IWOTH)
    except FileNotFoundError:
        # Path does not exist, not world-writable
        return False
    except PermissionError:
        # Cannot access file info, assume not writable by 'other'
        # Or simply cannot determine, so return False (safer)
        # print(f"Warning: Permission denied to stat {path}") # Optional detailed warning
        return False
    except Exception:
        # Catch any other exceptions during stat
        # print(f"Error checking writability for {path}: {e}") # Optional detailed error
        return False

def is_executable(path: str) -> bool:
    """
    Checks if a file is executable.

    Uses os.access with os.X_OK. On Unix, checks execute permission bits.
    On Windows, this might check file extensions (.exe, .bat, etc.)
    and path settings rather than traditional permissions.
    The combination with world-writable is primarily a Unix/Linux security concept.

    Args:
        path: The path to the file.

    Returns:
        True if the path exists and is executable, False otherwise or on error.
    """
    try:
        # os.X_OK checks for execute permission
        # On Windows, this primarily checks if the file is recognized as executable
        # (based on extension and PATHEXT) and if the current user can access it.
        return os.access(path, os.X_OK)
    except FileNotFoundError:
        # Path does not exist, not executable
        return False
    except Exception:
        # Catch any other exceptions during access check
        # print(f"Error checking executability for {path}: {e}") # Optional detailed error
        return False

def scan_directory(path: str) -> List[str]:
    """
    Recursively scans a directory for files that are both world-writable and executable.

    Args:
        path: The starting directory path to scan.

    Returns:
        A list of full paths to files that are found to be world-writable and executable.
    """
    risky_files: List[str] = []
    if not os.path.isdir(path):
        print(f"Error: Path is not a valid directory or does not exist: {path}")
        return risky_files # Return empty list if not a directory

    # Use a set to keep track of directories we couldn't access to avoid repeated warnings
    skipped_dirs = set()

    try:
        # Use os.walk to traverse the directory tree
        # Setting followlinks=False might be safer on some systems to avoid loops
        for root, dirs, files in os.walk(path, followlinks=False):
            # Check for permission issues *before* trying to list files/dirs
            # This try-except handles os.walk itself failing on a directory
            try:
                # We iterate through a *copy* of the dirs list because we might
                # modify it in place if we skip a directory due to permissions.
                # Although in this logic, we just print a warning and os.walk
                # handles skipping the directory itself. The inner try/except
                # is more for processing individual files/dirs *within* the walk.

                for name in files:
                    full_path = os.path.join(root, name)
                    # Check if it's actually a file before checking permissions
                    # This avoids issues with directories having execute permissions
                    # Also check if it exists, as it might disappear during scan
                    if os.path.isfile(full_path):
                        if is_world_writable(full_path) and is_executable(full_path):
                            risky_files.append(full_path)

            except PermissionError:
                # This specific error within the walk loop catches failure
                # to process files/dirs inside 'root'. os.walk is usually
                # resilient and continues, but explicit handling is good.
                if root not in skipped_dirs:
                    print(f"Warning: Permission denied to access contents of directory: {root}")
                    skipped_dirs.add(root)
                # Continue processing other files in the current root or move to the next root
                continue
            except Exception as e:
                 # Catch any other unexpected errors during directory processing
                 print(f"Error processing entry in {root}: {e}")
                 continue # Try to continue with the next entry

    except PermissionError:
        print(f"Error: Permission denied to start scanning directory: {path}")
        # risky_files will be empty, which is correct
    except Exception as e:
        print(f"Error during scan of {path}: {e}")
        # risky_files will contain what was found before the error

    return risky_files

def delete_file(file_path: str) -> bool:
    """
    Attempts to delete a single file.

    Args:
        file_path: The path to the file to delete.

    Returns:
        True if deletion was successful, False otherwise.
    """
    try:
        os.remove(file_path)
        print(f"  - Deleted: {file_path}")
        return True
    except FileNotFoundError:
        print(f"  - Failed to delete (not found): {file_path}")
        return False
    except PermissionError:
        print(f"  - Failed to delete (permission denied): {file_path}")
        return False
    except OSError as e:
        # Catch other OS errors (e.g., file in use)
        print(f"  - Failed to delete (OS Error: {e}): {file_path}")
        return False
    except Exception as e:
        # Catch any other unexpected errors during deletion
        print(f"  - Failed to delete (Error: {e}): {file_path}")
        return False

def main():
    """
    Main function to parse arguments and initiate the scan and optional deletion.
    """
    parser = argparse.ArgumentParser(
        description="Scan directories for world-writable and executable files."
        " Optionally delete them using the --delete flag (USE WITH EXTREME CAUTION)."
    )
    # Define a required argument for directories to scan, allowing multiple paths
    parser.add_argument(
        "directories",
        metavar="DIRECTORY",
        type=str,
        nargs="+", # Requires one or more directory arguments
        help="One or more directories to scan recursively."
    )
    # Add a boolean flag for deletion. It's False by default.
    parser.add_argument(
        "--delete",
        action="store_true", # Stores True when the flag is present
        help="WARNING: Enable deletion of identified risky files. Use with extreme caution."
    )

    args = parser.parse_args()
    directories_to_scan = args.directories
    perform_deletion = args.delete

    print("--- Starting Security Scan ---")
    if perform_deletion:
        print("!!! DELETION MODE ENABLED - RISKY FILES WILL BE REMOVED !!!")
        print("!!! PROCEED WITH CAUTION !!!")

    all_risky_files: List[str] = []

    for directory in directories_to_scan:
        print(f"\n🔍 Scanning: {directory}") # Add a newline for better separation
        risky_in_dir = scan_directory(directory)

        if risky_in_dir:
            print(f"\n⚠️ Found potential risks in {directory} ({len(risky_in_dir)} files):")
            if perform_deletion:
                print(f"Attempting to delete {len(risky_in_dir)} files in {directory}...")
                deleted_count = 0
                for file_path in risky_in_dir:
                    if delete_file(file_path):
                         deleted_count += 1
                print(f"Deletion attempt finished for {directory}. Successfully deleted {deleted_count} files.")
            else:
                print("List of risky files (use --delete to remove):")
                for file_path in risky_in_dir:
                    print(f"  - {file_path}")
                all_risky_files.extend(risky_in_dir) # Only add to overall list if not deleting immediately

        else:
            print(f"✅ No potential risks found in {directory}.")

        print("-" * 30) # Separator for clarity

    print("--- Scan Complete ---")

    if not perform_deletion:
        # Show overall summary only if we weren't deleting during the scan loop
        if not all_risky_files:
            print("🥳 Overall: No world-writable and executable files found in the scanned directories.")
        else:
            print(f"Summary: Found {len(all_risky_files)} potential risks in total across all scanned directories (deletion was not enabled).")
    else:
         print("Deletion process finished. Review output above for individual deletion results.")


if __name__ == "__main__":
    main()