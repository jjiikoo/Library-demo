# Library Database Manager

### Prerequisites

- Python 3.10 or higher
- Pytest (for running tests)
- Other tools

### Installation

Clone this repository:

```bash
git clone https://github.com/jjiikoo/Library-demo.git
```

To run tests, install pytest:

```bash
pip install pytest
```

## Usage

Run the application by providing a database file:

```bash
python library.py <filename>
```

If the file doesn't exist, it will be created automatically.

### Database Format

The database is a simple [text] file with each book on a separate line in the following format:

```
Title/Writer/ISBN-13/Publishing-year
```

## Running Tests

```bash
# Run all tests
pytest
```

## File Structure

- `library.py` - Main application
- `test_library.py` - Tests
