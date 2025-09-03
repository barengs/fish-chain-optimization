# Fish Chain API Documentation

## Authentication

This API uses JWT (JSON Web Tokens) for authentication.

### Login

```
POST /users/login/
```

Request body:

```json
{
  "username": "your_username",
  "password": "your_password"
}
```

Response:

```json
{
  "refresh": "refresh_token",
  "access": "access_token"
}
```

### Refresh Token

```
POST /users/login/refresh/
```

Request body:

```json
{
  "refresh": "refresh_token"
}
```

Response:

```json
{
  "access": "new_access_token"
}
```

## User Registration

### Register General User

```
POST /users/register/
```

Request body:

```json
{
  "username": "user123",
  "email": "user@example.com",
  "role": "admin",
  "password": "password123",
  "password2": "password123"
}
```

Response:

```json
{
  "user": {
    "id": 1,
    "username": "user123",
    "email": "user@example.com",
    "role": "admin"
  },
  "refresh": "refresh_token",
  "access": "access_token"
}
```

### Register Ship Owner

```
POST /users/register/owner/
```

For individual owner:

```json
{
  "username": "owner123",
  "email": "owner@example.com",
  "password": "password123",
  "password2": "password123",
  "owner_type": "individual",
  "profile": {
    "first_name": "John",
    "last_name": "Doe",
    "id_number": "1234567890",
    "phone_number": "08123456789"
  }
}
```

For company owner:

```json
{
  "username": "company123",
  "email": "company@example.com",
  "password": "password123",
  "password2": "password123",
  "owner_type": "company",
  "profile": {
    "company_name": "Test Company",
    "company_registration_number": "COMP12345",
    "tax_number": "TAX12345",
    "contact_person": "Jane Smith",
    "phone_number": "08123456789"
  }
}
```

### Register Captain

```
POST /users/register/captain/
```

Request body:

```json
{
  "username": "captain123",
  "email": "captain@example.com",
  "password": "password123",
  "password2": "password123",
  "profile": {
    "first_name": "Captain",
    "last_name": "Jack",
    "license_number": "LIC12345",
    "years_of_experience": 10,
    "phone_number": "08123456789"
  }
}
```

## Role Management

### List All Roles

```
GET /roles/roles/
```

Response:

```json
[
  {
    "id": 1,
    "name": "Admin",
    "description": "Administrator role",
    "permissions": [],
    "permissions_count": 0,
    "is_active": true,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  }
]
```

### Create Role

```
POST /roles/roles/
```

Request body:

```json
{
  "name": "Manager",
  "description": "Manager role",
  "permission_ids": [1, 2, 3],
  "is_active": true
}
```

### Get Role Details

```
GET /roles/roles/{role_id}/
```

### Update Role

```
PUT /roles/roles/{role_id}/
```

Request body:

```json
{
  "name": "Updated Manager",
  "description": "Updated manager role",
  "permission_ids": [1, 2],
  "is_active": true
}
```

### Delete Role

```
DELETE /roles/roles/{role_id}/
```

### List All Permissions

```
GET /roles/permissions/
```

### List All User Roles

```
GET /roles/user-roles/
```

### Assign Role to User

```
POST /roles/user-roles/
```

Request body:

```json
{
  "user": 1,
  "role": 2
}
```

### Remove Role from User

```
DELETE /roles/user-roles/{user_role_id}/
```

### Get User's Roles

```
GET /roles/users/{user_id}/roles/
```

### List All Role Groups

```
GET /roles/role-groups/
```

### Create Role Group

```
POST /roles/role-groups/
```

Request body:

```json
{
  "name": "Management Group",
  "description": "Group for management roles",
  "role_ids": [1, 2, 3],
  "is_active": true
}
```

### Get Role Group Details

```
GET /roles/role-groups/{role_group_id}/
```

### Update Role Group

```
PUT /roles/role-groups/{role_group_id}/
```

### Delete Role Group

```
DELETE /roles/role-groups/{role_group_id}/
```

## User Roles

The system supports three types of users:

1. **Admin** (`admin`) - System administrators
2. **Ship Owner** (`pemilik_kapal`) - Ship owners (individual or company)
3. **Ship Captain** (`nahkoda_kapal`) - Ship captains

## Profile Management

Each user type has a specific profile:

- **Individual Owners** have an IndividualOwnerProfile
- **Company Owners** have a CompanyOwnerProfile
- **Captains** have a CaptainProfile

Profiles are automatically created during registration based on the user's role.
