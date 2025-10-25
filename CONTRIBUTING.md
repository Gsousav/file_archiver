## Contributing to File Archiver

Thank you for your interest in contributing to File Archiver! This document provides guidelines and instructions for contributing.

## Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/file-archiver.git
cd file-archiver
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install package in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev,full]"
```

### 4. Run Tests

```bash
pytest tests/ -v
```

## Project Structure

```
file_archiver/
├── core/              # Core data models and configuration
│   ├── config.py      # Configuration settings
│   └── models.py      # Data classes
├── services/          # Business logic services
│   ├── scanner.py     # Directory scanning
│   ├── classifier.py  # File classification
│   ├── content_analyzer.py  # Content analysis
│   ├── mover.py       # File moving operations
│   └── reporter.py    # Report generation
├── ui/                # User interfaces
│   └── cli.py         # Command-line interface
└── utils/             # Utility functions
    └── helpers.py     # Helper functions
```

## Code Style

We follow PEP 8 and use automated tools:

### Format Code

```bash
black file_archiver/
```

### Lint Code

```bash
flake8 file_archiver/
```

### Type Checking

```bash
mypy file_archiver/
```

## Adding New Features

### 1. Adding a New File Category

Edit `core/config.py`:

```python
CATEGORIES = {
    # ... existing categories
    "my_new_category": ["ext1", "ext2", "ext3"],
}
```

### 2. Adding Content Analysis

Edit `services/content_analyzer.py`:

```python
def analyze_my_file_type(self, file_path: Path) -> Dict[str, Any]:
    """Analyze a specific file type."""
    metadata = {}
    # Your analysis logic here
    return metadata
```

### 3. Adding a New Collision Policy

1. Add the policy to `core/models.py`:
```python
class CollisionPolicy(Enum):
    # ... existing policies
    MY_POLICY = "my_policy"
```

2. Implement the handler in `services/mover.py`:
```python
elif self.collision_policy == CollisionPolicy.MY_POLICY:
    # Your handling logic
    pass
```

## Testing Guidelines

### Writing Tests

1. Create test files in `tests/` directory
2. Name test files with `test_` prefix
3. Use pytest fixtures for setup/teardown
4. Aim for >80% code coverage

Example test:

```python
def test_my_feature():
    """Test description."""
    # Arrange
    input_data = "test"
    
    # Act
    result = my_function(input_data)
    
    # Assert
    assert result == expected_output
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=file_archiver --cov-report=html

# Run specific test file
pytest tests/test_basic.py -v
```

## Commit Guidelines

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(classifier): add support for .webp images

fix(mover): handle collision policy for directories

docs(readme): update installation instructions
```

## Pull Request Process

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/my-feature`
3. **Make** your changes and commit with clear messages
4. **Test** your changes: `pytest tests/`
5. **Format** your code: `black file_archiver/`
6. **Push** to your fork: `git push origin feature/my-feature`
7. **Submit** a pull request

### PR Checklist

- [ ] Tests pass locally
- [ ] Code is formatted with Black
- [ ] New features have tests
- [ ] Documentation is updated
- [ ] Commit messages follow guidelines
- [ ] No merge conflicts

## Feature Requests

Have an idea? Open an issue with:
- **Title**: Clear, concise description
- **Description**: Detailed explanation
- **Use Case**: Why this feature is useful
- **Example**: How it would work

## Bug Reports

Found a bug? Open an issue with:
- **Title**: Brief description
- **Steps to Reproduce**: Numbered list
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Environment**: Python version, OS, etc.
- **Logs**: Relevant error messages

## Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone.

### Our Standards

**Positive behavior:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community

**Unacceptable behavior:**
- Trolling, insulting/derogatory comments
- Public or private harassment
- Publishing others' private information
- Other unprofessional conduct

## Questions?

Feel free to:
- Open an issue for questions
- Start a discussion
- Reach out to maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
