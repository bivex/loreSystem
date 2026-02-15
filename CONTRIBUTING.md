# Contributing to MythWeave Chronicles

Thank you for your interest in contributing to MythWeave Chronicles! We welcome contributions from the community to help improve and expand this lore management system.

## Ways to Contribute

- **Bug Reports**: Report bugs via [GitHub Issues](https://github.com/bivex/loreSystem/issues)
- **Feature Requests**: Suggest new features or improvements
- **Code Contributions**: Submit pull requests with bug fixes or new features
- **Documentation**: Improve documentation, tutorials, or examples
- **Testing**: Write or improve tests

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/loreSystem.git`
3. Create a virtual environment: `python -m venv venv`
4. Activate the environment: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
5. Install dependencies: `pip install -r requirements.txt`
6. Install dev dependencies: `pip install -r requirements-dev.txt`

## Development Workflow

1. Create a new branch for your changes: `git checkout -b feature/your-feature-name`
2. Make your changes
3. Run tests: `python -m pytest tests/ -v`
4. Run linting: `python -m flake8 src/`
5. Commit your changes: `git commit -m "Description of changes"`
6. Push to your fork: `git push origin feature/your-feature-name`
7. Create a Pull Request

## Code Standards

- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Write docstrings for all public functions and classes
- Ensure all tests pass
- Maintain test coverage above 90%

## Pull Request Guidelines

- Use a clear, descriptive title
- Provide a detailed description of the changes
- Reference any related issues
- Ensure CI checks pass
- Request review from maintainers

## Testing

- Write unit tests for new functionality
- Include integration tests for database operations
- Test edge cases and error conditions
- Run the full test suite before submitting

## Documentation

- Update documentation for any new features
- Ensure code examples work correctly
- Update the changelog for significant changes

## Questions?

If you have questions about contributing, feel free to:
- Open a [GitHub Discussion](https://github.com/bivex/loreSystem/discussions)
- Join our community chat (if available)
- Contact the maintainers

We appreciate your contributions to making MythWeave Chronicles better!