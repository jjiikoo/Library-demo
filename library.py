import argparse
from dataclasses import dataclass, field
import logging
import os
import sys

logging.basicConfig(
    filename="Library.log",
    encoding="utf-8",
    filemode="a",
    format="{asctime} - {levelname} - {message}",
    datefmt="%Y-%m-%d %H:%M:%S",
    style="{",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


MENU_BORDER = "*" * 15


def handle_error(error, message, log_level=logging.ERROR, exit_code=None):
    """
    Centralized error handling

    Args:
        error: The exception that was raised
        message: The error message to display/log
        log_level: Logging level (default: ERROR)
        exit_code: Exit the program with this code (if exists)

    Returns:
        None
    """

    print(f"{message}: {error}")

    if log_level == logging.CRITICAL:
        logger.critical(message, exc_info=True)
    elif log_level == logging.ERROR:
        logger.error(message, exc_info=True)
    elif log_level == logging.WARNING:
        logger.warning(message)
    else:
        logger.info(message)

    if exit_code is not None:
        sys.exit(exit_code)


@dataclass(order=True)
class Book:
    sort_index: int = field(init=False, repr=False, compare=True)
    title: str
    writer: str
    isbn: str
    publishing_year: str

    def __post_init__(self):
        self.sort_index = int(self.publishing_year)

    def __str__(self) -> str:
        return f"{self.title.upper()} ({self.publishing_year}) by {self.writer} [ISBN-13: {self.isbn}]"

    def file_line_format(self) -> str:
        return f"{self.title}/{self.writer}/{self.isbn}/{self.publishing_year}"


@dataclass
class Library:
    filename: str
    books: list[Book] = field(default_factory=list)

    def __post_init__(self):
        self.clean_database_file()
        self.load_file_contents()

    def clean_database_file(self) -> None:
        """
        Clean empty lines from the database file and rewrite the file

        Returns:
            None
        """
        # File doesn't exist so there are no lines to clean
        if not os.path.exists(self.filename):
            return

        try:
            with open(self.filename, "r") as file:
                lines = file.readlines()

            non_empty_lines = [line for line in lines if line.strip()]

            # Re-write the file with non-empty files
            with open(self.filename, "w") as file:
                file.writelines(non_empty_lines)

            # Total number of lines removed
            lines_removed = len(lines) - len(non_empty_lines)

            if lines_removed:
                log_msg = (
                    f"Removed {lines_removed} empty line(s) from the database file"
                )
                logger.info(log_msg)
                print(log_msg)

        except PermissionError as e:
            handle_error(
                e,
                f"ERROR: Cannot access the file '{self.filename}', please check the file permissions and try again",
                logging.CRITICAL,
                1,
            )
        except IOError as e:
            handle_error(
                e,
                f"ERROR: Failed to clean the database file '{self.filename}'",
                logging.CRITICAL,
                1,
            )

    def load_file_contents(self) -> None:
        """
        Load the book records from the database file into the array

        Returns:
            None
        """
        try:
            # Check if the provided file name exists - if not, create one
            if not os.path.exists(self.filename):
                try:
                    with open(self.filename, "w"):
                        pass
                    log_msg = f"New library database created: {self.filename}"
                    logger.info(log_msg)
                    print(log_msg)
                except (PermissionError, IOError) as e:
                    handle_error(
                        e,
                        f"ERROR: Failed to create database file '{self.filename}'",
                        logging.CRITICAL,
                        1,
                    )

            with open(self.filename) as f:
                for line_number, line in enumerate(f, 1):
                    # Skip all the empty lines in the file
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        book_parts = [part.strip() for part in line.split("/")]

                        # Line has less than 4 fields, ignore and continue
                        if len(book_parts) < 4:
                            log_msg = f"{self.filename}: Line {line_number} has {len(book_parts)} parts, expected 4, ignoring"
                            logger.warning(log_msg)
                            print(log_msg)
                            continue

                        title, writer, isbn, publishing_year = book_parts[:4]

                        # Publishing year doesn't have a valid [digit] value, ignore and continue
                        if not publishing_year.isdigit():
                            log_msg = f"{self.filename}: Line {line_number} has an invalid (non-digit) year: '{publishing_year}', ignoring"
                            logger.warning(log_msg)
                            print(log_msg)
                            continue

                        # isbn doesn't have a valid [digit] value, ignore and continue
                        if not isbn.isdigit():
                            log_msg = f"{self.filename}: Line {line_number} has an invalid (non-digit) ISBN-13: '{publishing_year}', ignoring"
                            logger.warning(log_msg)
                            print(log_msg)
                            continue

                        # Everything looks fine, add the book to the array
                        self.books.append(Book(title, writer, isbn, publishing_year))

                        # Warn if the line has more than 4 fields
                        if len(book_parts) > 4:
                            log_msg = f"{self.filename}: Line {line_number} has {len(book_parts)} parts, only first 4 are used"
                            logger.warning(log_msg)
                            print(log_msg)

                    except Exception as e:
                        handle_error(
                            e,
                            f"{self.filename}: Unexpected error on line {line_number} '{line}'",
                            logging.ERROR,
                        )

        except PermissionError as e:
            handle_error(
                e,
                f"ERROR: Cannot access the file '{self.filename}'. Please check the file permissions and try again",
                logging.CRITICAL,
                1,
            )
        except IOError as e:
            handle_error(
                e,
                f"ERROR: Failed to read the database file '{self.filename}'",
                logging.CRITICAL,
                1,
            )
        except Exception as e:
            handle_error(
                e,
                f"ERROR: Unexpected problem accessing the file '{self.filename}'",
                logging.CRITICAL,
                1,
            )

    def save_to_database(self, book: Book) -> None:
        """
        Save the book into the database

        Args:
            book: The Book object to save to the database

        Returns:
            None
        """
        try:
            with open(self.filename, "a") as f:
                f.write(f"{book.file_line_format()}\n")

            # Add the book to the array ONLY if it was successfully written to the database file
            self.books.append(book)
            log_msg = f"New book '{book}' successfully added to the database"
            print(log_msg)
            logger.debug(log_msg)
        except IOError as e:
            handle_error(
                e,
                f"ERROR: Failed to save the book to the file '{self.filename}'",
                logging.ERROR,
            )
        except Exception as e:
            handle_error(e, "ERROR: Unexpected error saving the book", logging.ERROR)

    def list_books(self) -> None:
        """
        List all the books in the database sorted by the publishing year

        Returns:
            None
        """

        print("")
        if len(self.books) == 0:
            print("Database doesn't contain any books")
            return

        print(f"Books in '{self.filename}' (sorted by year):")
        print("\n".join(f"\t{book}" for book in sorted(self.books)))
        print("")


# String validation
def read_str_input(prompt: str, min_length: int = 1, max_length: int = 100) -> str:
    """
    Read and validate (no empty values, min and max length) the user str input

    Args:
        prompt: The text prompt to display to the user
        min_length: Minimum length for input (default value: 1)
        max_length: Maximum length for input (default value: 100)

    Returns:
        Validated str input
    """

    field = prompt.replace(":", "").strip()

    while True:
        value = input(prompt).strip()
        if not value:
            print(f"'{field}' cannot be empty, please try again")
        elif len(value) < min_length or len(value) > max_length:
            if len(value) < min_length:
                print(f"'{field}' is too short, min length: {min_length} characters")
            else:
                print(f"'{field}' is too long, max length: {max_length} characters")
        else:
            return value


def read_isbn_input(prompt: str) -> str:
    """
    Read and validate ISBN-13 input. Accepts both numeric-only format (1234567890123) and hyphenated format (123-456-78901-2-3)

    Args:
        prompt: The text prompt to display to the user

    Returns:
        A validated ISBN-13 string (numeric only, hyphens removed)
    """
    field = prompt.replace(":", "").strip()

    while True:
        value = input(prompt).strip()
        if not value:
            print(f"'{field}' cannot be empty, please try again")
            continue

        # Remove hyphens for validation
        clean_value = value.replace("-", "")

        if len(clean_value) != 13:
            print(f"ISBN-13 must contain exactly 13 digits")
            continue

        # Cleaned value contains non-digit characters
        if not clean_value.isdigit():
            print(f"ISBN-13 must contain only digits and optional hyphens")
            continue

        return clean_value


def read_year_input(prompt: str) -> str:
    """
    Read and validate a 4-digit year input

    Args:
        prompt: The text prompt to display to the user

    Returns:
        A year string
    """
    field = prompt.replace(":", "").strip()

    while True:
        value = input(prompt).strip()
        if not value:
            print(f"'{field}' cannot be empty, please try again")
            continue

        if len(value) != 4:
            print(f"Year must be exactly 4 digits")
            continue

        if not value.isdigit():
            print(f"Year must only contain digits")
            continue

        return value


def create_new_book_item(library: Library) -> None:
    """
    Collect the book information from the user, create a new Book object,
    and add it to the database, if confirmed

    Args:
        library: The Library object where the book will be added

    Returns:
        None
    """

    print("*** Add New Book ***")
    title = read_str_input("Title: ")
    writer = read_str_input("Writer: ")
    isbn = read_isbn_input("ISBN-13: ")
    publishing_year = read_year_input("Publishing Year: ")

    print("\nDetails:")
    print(
        f"\tTitle: {title}\n\tWriter: {writer}\n\tISBN-13: {isbn}\n\tPublishing year: {publishing_year}"
    )

    while True:
        save_choice_input = (
            input("\nDo you want to add this book to the database (Y/N): ")
            .upper()
            .strip()
        )
        if save_choice_input == "Y":
            new_book = Book(title, writer, isbn, publishing_year)
            library.save_to_database(new_book)
            return
        elif save_choice_input == "N":
            return
        else:
            print("Invalid choice. Please enter Y or N")


def print_menu_commands() -> None:
    """
    Print available menu options

    Args:
        None

    Returns:
        None
    """

    print(MENU_BORDER)
    print("1) Add new book")
    print("2) Print current database contents")
    print("Q) Exit program")
    print(MENU_BORDER)


def execute_menu_command(library: Library) -> None:
    """
    Process the menu selection and execute the corresponding command
    - Gets user menu selection input
    - Validates the input against the available options (1, 2, Q)
    - Executes the appropriate function:
        - "1": Add a new book to the library
        - "2": List all the books in the library database
        - "Q": Exit the program
    - Returns to main menu if an invalid option is selected

    Args:
        library: The Library object containing the book collection

    Returns:
        None
    """

    menu_command = input("> ").strip().upper()
    if menu_command not in ["1", "2", "Q"]:
        log_msg = f"Unknown command: {menu_command}"
        print(f"{log_msg}, please try again")
        logger.warning(log_msg)
        return

    match menu_command:
        case "1":
            create_new_book_item(library)
        case "2":
            library.list_books()
        case "Q":
            log_msg = "Exiting program"
            logger.debug(log_msg)
            sys.exit()


def main():
    logger.debug("Application started")
    try:
        parser = argparse.ArgumentParser(description="Library Database")
        parser.add_argument("filename", help="Database file for the book records")
        args = parser.parse_args()

        library = Library(args.filename)
        logger.debug(f"Library loaded with {len(library.books)} existing books")

        while True:
            try:
                print_menu_commands()
                execute_menu_command(library)
            except KeyboardInterrupt:
                logger.warning("Application interrupted by user")
                sys.exit(130)
            except Exception as e:
                handle_error(e, "Unexpected error", logging.ERROR)
    except Exception as e:
        handle_error(e, "Critical error", logging.CRITICAL, 1)


if __name__ == "__main__":
    sys.exit(main())
