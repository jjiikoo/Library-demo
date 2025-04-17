import os
import pytest

from library import Book, Library


class TestBook:
    def test_book_creation(self):
        """Test that a Book object is created correctly"""
        book = Book("Test Book One", "J", "1234567890123", "2000")
        assert book.title == "Test Book One"
        assert book.writer == "J"
        assert book.isbn == "1234567890123"
        assert book.publishing_year == "2000"
        assert book.sort_index == 2000

    def test_book_string_representation(self):
        """Test that a Book object's string presentation is correcty"""
        book = Book("Test Book", "Test Author", "1234567890123", "2000")
        assert str(book) == "TEST BOOK (2000) by Test Author [ISBN-13: 1234567890123]"

    def test_book_file_line_format(self):
        """Test that a Book object line is formatted correctly"""
        book = Book("Test Book", "J", "1234567890123", "2000")
        assert book.file_line_format() == "Test Book/J/1234567890123/2000"

    def test_book_sorting(self):
        """Test that books are sorted correctly by the publishing year"""
        book1 = Book("Test Book One", "J", "1234567890123", "2025")
        book2 = Book("Test Book Two", "J", "1234567890124", "1990")
        book3 = Book("Test Book Three", "J", "1234567890125", "2010")

        sorted_books = sorted([book1, book2, book3])
        assert sorted_books[0] == book2  # 1990
        assert sorted_books[1] == book3  # 2010
        assert sorted_books[2] == book1  # 2025


class TestLibrary:
    @pytest.fixture
    def test_db_path(self, tmp_path):
        """Returns a DB file test path"""
        return tmp_path / "test_books.txt"

    @pytest.fixture
    def db_file_two_books(self, test_db_path):
        """Creates a DB file with two books"""
        with open(test_db_path, "w") as f:
            f.write("Test Book One/J/1234567890123/2025\n")
            f.write("Test Book Two/J/1234567890124/2025\n")
        return test_db_path

    @pytest.fixture
    def db_file_empty(self, tmp_path):
        """Returns a path for a DB file that doesn't exist yet"""
        return tmp_path / "empty_library.txt"

    @pytest.fixture
    def db_file_malformed(self, test_db_path):
        """Creates a DB file with a mix of valid and invalid lines"""
        with open(test_db_path, "w") as f:
            f.write("Test Book One/J/1234567890123/2020\n")  # Valid
            f.write("Test Book Two/J/1234567890124/2030\n")  # Valid
            f.write("Test Book Invalid One/J\n")  # Invalid - not enough fields
            f.write("Test Book Invalid Two/J/123456789012A/2000\n")  # Invalid ISBN-13
            f.write(
                "Test Book Invalid Three/J/1234567890125/Test/Test\n"
            )  # Invalid year, extra field
            f.write("\n")  # Invalid, empty line
        return test_db_path

    def test_new_library_creation(self, db_file_empty):
        """Test creating an empty library database"""
        library = Library(str(db_file_empty))

        assert os.path.exists(db_file_empty)
        assert len(library.books) == 0

    def test_loading_existing_books(self, db_file_two_books):
        """Test loading books from an existing database"""
        library = Library(db_file_two_books)

        assert len(library.books) == 2
        assert library.books[0].title == "Test Book One"
        assert library.books[1].title == "Test Book Two"

    def test_malformed_lines(self, db_file_malformed):
        """Test that books are correctly read from a file where some of the lines are malformed"""
        library = Library(str(db_file_malformed))

        # Verify all valid books were loaded
        assert len(library.books) == 2

        book_titles = [book.title for book in library.books]
        assert "Test Book One" in book_titles
        assert "Test Book Two" in book_titles
        assert "Test Book Invalid One" not in book_titles
        assert "Test Book Invalid Two" not in book_titles

    def test_save_book_to_database(self, db_file_empty):
        """Test saving a new book to the database"""
        library = Library(db_file_empty)

        # Add a new book
        new_book = Book("Test Book", "J", "1234567890123", "2020")
        library.save_to_database(new_book)

        # Verify book was added
        assert len(library.books) == 1
        assert library.books[0].title == "Test Book"

        # Verify book was written to file
        with open(db_file_empty, "r") as f:
            content = f.read()
        assert "Test Book/J/1234567890123/2020" in content
