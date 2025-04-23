import argparse
import sys
import os # Import os to check for file existence, although try/except would also work
from rembg import remove
from typing import BinaryIO # For more precise file type hinting

# Module-level docstring explaining the script's purpose
"""
Script for removing the background from an image using the rembg library.
Allows specifying input and output files via command-line arguments.
"""

def process_image(input_stream: BinaryIO, output_stream: BinaryIO) -> None:
    """
    Removes the background from an image by reading from input_stream
    and writing to output_stream.

    Args:
        input_stream: Stream for reading image data (opened in binary mode).
        output_stream: Stream for writing processed image data (opened in binary mode).

    Raises:
        Exception: If an error occurred while processing the image with the rembg library.
    """
    try:
        image_bytes: bytes = input_stream.read()
        output_bytes: bytes = remove(image_bytes)
        output_stream.write(output_bytes)
    except Exception as e:
        # Catch any errors that might occur inside the remove function
        raise Exception(f"Error processing image with rembg library: {e}")


def remove_background_cli(input_path: str, output_path: str) -> None:
    """
    Removes the background from an image using the specified file paths.

    This function is a wrapper for file handling, using the lower-level
    process_image function.

    Args:
        input_path: Path to the input image file.
        output_path: Path to save the output image file.

    Raises:
        FileNotFoundError: If the input file is not found.
        IOError: If a file reading or writing error occurred.
        Exception: For other potential errors, including rembg library errors.
    """
    print(f"Processing image: '{input_path}' -> '{output_path}'")
    try:
        # Check if the input file exists before attempting to open it
        if not os.path.exists(input_path):
             raise FileNotFoundError(f"Error: Input file not found at path '{input_path}'")

        with open(input_path, 'rb') as input_file:
            with open(output_path, 'wb') as output_file:
                process_image(input_file, output_file) # Pass the file streams

        print("Background successfully removed.")

    except FileNotFoundError as e:
        # Re-raise FileNotFoundError for main to handle it
        raise e
    except IOError as e:
         # Catch and re-raise I/O errors
         raise IOError(f"I/O error while working with files: {e}")
    except Exception as e:
        # Catch and re-raise any other processing errors
        raise e


def main():
    """
    Main function for parsing command-line arguments
    and starting the background removal process.
    """
    parser = argparse.ArgumentParser(
        description='Removes the background from an image using rembg.',
        formatter_class=argparse.RawTextHelpFormatter # To preserve help formatting
    )
    parser.add_argument(
        '-i', '--input',
        type=str,
        required=True,
        help='Path to the input image file (e.g., input.png)'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        required=True,
        help='Path to save the output image file (e.g., output.png)'
    )

    args = parser.parse_args()

    # Call the main processing logic within a try/except block
    try:
        remove_background_cli(args.input, args.output)
        sys.exit(0) # Exit with code 0 on success
    except (FileNotFoundError, IOError, Exception) as e:
        print(f"Error: {e}", file=sys.stderr) # Print the error to the standard error stream
        sys.exit(1) # Exit with code 1 on error


if __name__ == "__main__":
    main()