# Fish Chain Optimization API

## Overview

Fish Chain Optimization is a Django-based API system for managing users, roles, and permissions in a fish chain business environment.

## Features

- User authentication with JWT tokens
- Dynamic role management system
- Owner profiles (individual and company)
- Captain profiles
- Role-based access control
- API documentation with DRF Spectacular

## Prerequisites

- Python 3.8+
- MySQL database
- pip package manager

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd fishchain/fco
   ```

2. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure the database in `fco/settings.py`:

   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'your_database_name',
           'USER': 'your_database_user',
           'PASSWORD': 'your_database_password',
           'HOST': 'localhost',
           'PORT': '3306',
       }
   }
   ```

5. Run migrations:

   ```bash
   python manage.py migrate
   ```

6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

## Running the Application

1. Start the development server:

   ```bash
   python manage.py runserver
   ```

2. Access the application:
   - Admin interface: http://127.0.0.1:8000/admin/
   - API endpoints: http://127.0.0.1:8000/
   - API documentation: http://127.0.0.1:8000/api/schema/swagger-ui/

## API Documentation

The API is documented using DRF Spectacular and can be accessed at:

- **Swagger UI**: http://127.0.0.1:8000/api/schema/swagger-ui/
- **Redoc**: http://127.0.0.1:8000/api/schema/redoc/
- **Schema (YAML)**: http://127.0.0.1:8000/api/schema/

For detailed documentation, see [DOCUMENTATION.md](DOCUMENTATION.md).

## Project Structure

```
fco/
├── fco/                 # Project settings
├── users/               # User management app
├── role_managements/    # Role management app
├── manage.py            # Django management script
├── requirements.txt     # Project dependencies
├── DOCUMENTATION.md     # API documentation guide
└── README.md            # This file
```

## Main Components

### Users App

Handles user authentication, registration, and profiles:

- Custom user model with dynamic roles
- Owner profiles (individual and company)
- Captain profiles
- JWT-based authentication

### Role Management App

Manages roles, permissions, and user-role assignments:

- Dynamic role creation and management
- Permission assignment to roles
- User-role relationships
- Role groups for easier management

## API Endpoints

### Authentication

- `POST /users/register/` - Register new user
- `POST /users/register/owner/` - Register owner user
- `POST /users/register/captain/` - Register captain user
- `POST /users/login/` - Obtain JWT tokens
- `POST /users/login/refresh/` - Refresh JWT tokens
- `POST /users/logout/` - Logout

### Roles

- `GET /roles/roles/` - List all roles
- `POST /roles/roles/` - Create new role
- `GET /roles/roles/{id}/` - Get role details
- `PUT /roles/roles/{id}/` - Update role
- `DELETE /roles/roles/{id}/` - Delete role

### Permissions

- `GET /roles/permissions/` - List all permissions

### User Roles

- `GET /roles/user-roles/` - List all user-role assignments
- `POST /roles/user-roles/` - Assign role to user
- `DELETE /roles/user-roles/{id}/` - Remove user-role assignment
- `GET /roles/users/{user_id}/roles/` - Get user's roles

### Role Groups

- `GET /roles/role-groups/` - List all role groups
- `POST /roles/role-groups/` - Create new role group
- `GET /roles/role-groups/{id}/` - Get role group details
- `PUT /roles/role-groups/{id}/` - Update role group
- `DELETE /roles/role-groups/{id}/` - Delete role group

## Development

### Creating Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Running Tests

```bash
python manage.py test
```

### Code Quality

- Follow PEP 8 style guide
- Use type hints where possible
- Write docstrings for all public methods and classes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
