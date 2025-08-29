# Hotel Management CRM

A comprehensive hotel management system built with Django REST Framework, featuring user management, room management, reservations, and billing systems.

## Features

- **User Management**
  - Multiple user types (Admin, Front Desk, Housekeeping, Manager)
  - JWT Authentication
  - Custom user model with extended profile information

- **Room Management**
  - Room inventory and status tracking
  - Room type categorization
  - Maintenance status

- **Reservations**
  - Room booking and availability checking
  - Check-in/Check-out management
  - Guest information tracking

- **Billing**
  - Invoice generation
  - Payment tracking
  - Financial reporting

## Tech Stack

- **Backend**: Django 5.2.5
- **API**: Django REST Framework
- **Authentication**: JWT (SimpleJWT)
- **Database**: SQLite (default)
- **Development Tools**: 
  - UV (Python package installer)
  - Just (Command runner)
  - Black (Code formatter)
  - Ruff (Linter)

## Prerequisites

- Python 3.11+
- UV package installer
- Just command runner

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/sakshamtolani-qc/hotel-management.git
   cd hotel-management
   ```

2. **Set up the environment**
   ```bash
   just create-env
   ```
   This will create a `.env` file from `.env.template`

3. **Configure environment variables**
   Edit the `.env` file with your settings:
   - `MODE`: Set to 'dev' for development or 'prod' for production
   - `DEBUG`: Set to 'True' for development or 'False' for production
   - `SECRET_KEY`: Your Django secret key

4. **Complete setup**
   ```bash
   just setup
   ```
   This will:
   - Install dependencies
   - Run migrations
   - Create a superuser

5. **Start the development server**
   ```bash
   just run
   ```
   The API will be available at `http://localhost:8000`

## Development Commands

- `just install` - Install dependencies
- `just migrate` - Run database migrations
- `just makemigrations` - Generate new migrations
- `just run` - Start development server
- `just shell` - Open Django shell
- `just test` - Run tests
- `just lint` - Check code with Ruff
- `just format` - Format code with Black
- `just clean` - Remove cache files
- `just requirements` - Update requirements.txt

## Project Structure

```
hotel-management/
├── backend/          # Django project settings
├── billing/          # Billing management app
├── reservations/     # Reservation management app
├── rooms/            # Room management app
├── users/            # User management app
├── static/           # Static files
└── manage.py         # Django management script
```

## Environment Variables

| Variable    | Description                     | Options        |
|-------------|---------------------------------|----------------|
| MODE        | Application environment         | dev/prod       |
| DEBUG       | Debug mode                      | True/False     |
| SECRET_KEY  | Django secret key              | string         |

> **Important**: Never commit your `.env` file to the repository. The `.env` file contains sensitive information and is automatically ignored by Git.

## API Documentation

The API endpoints are organized by app:

- `/api/users/` - User management endpoints
- `/api/rooms/` - Room management endpoints
- `/api/reservations/` - Reservation endpoints
- `/api/billing/` - Billing endpoints

Detailed API documentation is available at `/api/docs/` when running the server.

## Development Guidelines

### Branch Management
- ⚠️ **IMPORTANT**: Direct commits to the `main` branch are strictly prohibited
- All development work must be done in feature branches
- Branch naming convention: `HMCRM-{notion-ticket-number}`
  ```bash
  # Example for Notion ticket HMCRM-123
  git checkout -b HMCRM-123
  ```

### Pull Request (PR) Process
1. **Branch Creation**
   - Create a new branch from `main` using the Notion ticket number
   - Keep branches focused on a single feature or fix

2. **Commit Guidelines**
   - Write clear, descriptive commit messages
   - Include the Notion ticket number in commit messages
   ```bash
   git commit -m "[HMCRM-123] Add user authentication feature"
   ```

3. **Before Submitting PR**
   - Ensure all tests pass: `just test`
   - Format code: `just format`
   - Run linter: `just lint`
   - Update documentation if needed
   - Verify the .env file is not included in commits

4. **PR Review Process**
   - All PRs must be reviewed and approved
   - Address review comments promptly
   - PRs will be merged by @sakshamtolani-qc only
   - Squash commits before merging

### Code Quality Standards
- Maintain consistent code style using Black formatter
- Follow PEP 8 guidelines for Python code
- Keep functions and methods focused and single-purpose
- Write meaningful docstrings for classes and functions
- Add appropriate comments for complex logic

### Important Notes
- Always keep your local `main` branch updated
  ```bash
  git checkout main
  git pull origin main
  ```
- Never force push to any branch without team discussion
- Keep PRs focused and manageable in size
- Update requirements.txt if adding new dependencies
- Document API changes in the appropriate documentation
- Run tests before pushing changes

### Security Notes
- Never commit sensitive information
- Keep environment variables in .env (not in source control)
- Follow security best practices for Django
- Report security vulnerabilities directly to team lead

## Contributing

1. Follow all development guidelines above
2. Create your feature branch with Notion ticket number
3. Make your changes
4. Run tests with `just test`
5. Format code with `just format`
6. Submit a pull request for review

## License

This project is licensed under the MIT License - see the LICENSE file for details.
