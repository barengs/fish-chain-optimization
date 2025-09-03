# Fish Chain Optimization API Documentation

## Overview

This document provides instructions on how to access and use the API documentation for the Fish Chain Optimization system, which is built using Django REST Framework with DRF Spectacular for API documentation.

## Prerequisites

- Python 3.8+
- Django 4.0+
- Django REST Framework
- DRF Spectacular

## Installation

The DRF Spectacular package should already be installed as part of the project dependencies:

```bash
pip install drf-spectacular
```

## Configuration

The API documentation is already configured in the settings.py file with the following settings:

```python
INSTALLED_APPS = [
    # ... other apps
    'drf_spectacular',
]

REST_FRAMEWORK = {
    # ... other settings
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Fish Chain Optimization API',
    'DESCRIPTION': 'API documentation for the Fish Chain Optimization system',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}
```

## Accessing Documentation

Once the server is running, you can access the API documentation at the following URLs:

1. **Swagger UI**: `http://localhost:8000/api/schema/swagger-ui/`
2. **Redoc**: `http://localhost:8000/api/schema/redoc/`
3. **Schema (YAML)**: `http://localhost:8000/api/schema/`

## Starting the Server

To start the development server and access the documentation:

```bash
cd /Users/ROFI/Develop/proyek/fishchain/fco
python manage.py runserver
```

Then open your browser and navigate to:

- Swagger UI: http://127.0.0.1:8000/api/schema/swagger-ui/
- Redoc: http://127.0.0.1:8000/api/schema/redoc/

## API Endpoints

### Authentication Endpoints

- `POST /users/register/` - Register a new user
- `POST /users/register/owner/` - Register a new owner (individual or company)
- `POST /users/register/captain/` - Register a new captain
- `POST /users/login/` - Login and obtain JWT tokens
- `POST /users/login/refresh/` - Refresh JWT tokens
- `POST /users/logout/` - Logout (blacklist refresh token)

### Role Management Endpoints

- `GET /roles/roles/` - List all roles
- `POST /roles/roles/` - Create a new role
- `GET /roles/roles/{id}/` - Get role details
- `PUT /roles/roles/{id}/` - Update a role
- `DELETE /roles/roles/{id}/` - Delete a role

### Permission Endpoints

- `GET /roles/permissions/` - List all permissions

### User Role Endpoints

- `GET /roles/user-roles/` - List all user-role assignments
- `POST /roles/user-roles/` - Assign a role to a user
- `DELETE /roles/user-roles/{id}/` - Remove a user-role assignment
- `GET /roles/users/{user_id}/roles/` - Get all roles for a specific user

### Role Group Endpoints

- `GET /roles/role-groups/` - List all role groups
- `POST /roles/role-groups/` - Create a new role group
- `GET /roles/role-groups/{id}/` - Get role group details
- `PUT /roles/role-groups/{id}/` - Update a role group
- `DELETE /roles/role-groups/{id}/` - Delete a role group

## Documentation Features

### Swagger UI

Swagger UI provides an interactive API documentation interface where you can:

- View all available endpoints
- See request/response schemas
- Try out API endpoints directly from the browser
- View example requests and responses

### Redoc

Redoc provides a clean, readable documentation interface that:

- Presents API documentation in a structured, easy-to-read format
- Shows detailed information about each endpoint
- Includes code examples for different programming languages

## Customization

To customize the documentation, you can modify the `SPECTACULAR_SETTINGS` in `settings.py`:

```python
SPECTACULAR_SETTINGS = {
    'TITLE': 'Your API Title',
    'DESCRIPTION': 'Your API description',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    # Additional settings can be added here
}
```

## Adding Documentation to Views

Documentation is added to views using the `@extend_schema` decorator from DRF Spectacular:

```python
from drf_spectacular.utils import extend_schema

@extend_schema(
    summary="Register a new user",
    description="Register a new user with username, email, password and optional role",
    request=CustomUserCreateSerializer,
    responses={201: CustomUserSerializer}
)
def post(self, request):
    # View implementation
```

## Adding Documentation to Serializers

Documentation is added to serializers through docstrings:

```python
class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer for user details.

    This serializer is used to serialize user information including their role.
    """
    # Serializer fields and methods
```

## Adding Documentation to Models

Documentation is added to models through docstrings:

```python
class CustomUser(AbstractUser):
    """
    Custom User model that extends Django's built-in User model.

    This model adds a role field that references the dynamic Role model
    from the role management system.
    """
    # Model fields and methods
```

## Troubleshooting

### Common Issues

1. **Circular Import Errors**: If you encounter circular import errors, ensure that ForeignKey relationships use string references instead of direct imports.

2. **Missing Documentation**: If endpoints are not appearing in the documentation, ensure that:

   - Views are properly decorated with `@extend_schema`
   - Serializers have appropriate docstrings
   - URLs are properly included in the main URL configuration

3. **Server Not Starting**: If the server fails to start:
   - Check for import errors in views, serializers, or models
   - Ensure all dependencies are installed
   - Verify database migrations are up to date

### Getting Help

For additional help with DRF Spectacular, refer to the official documentation:

- [DRF Spectacular Documentation](https://drf-spectacular.readthedocs.io/)

## Contributing to Documentation

To improve this documentation:

1. Update view docstrings with `@extend_schema` decorators
2. Add detailed docstrings to serializers and models
3. Update this DOCUMENTATION.md file with any new features or changes
4. Test documentation by running the server and verifying all endpoints appear correctly

## License

This documentation is part of the Fish Chain Optimization system and follows the same license as the main project.
