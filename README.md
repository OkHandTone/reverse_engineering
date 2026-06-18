# Inventory Management System API

## Overview
This project is an inventory management system API developed using Django Rest Framework (DRF). It's designed to handle various aspects of inventory management, including items, stock, transactions, categories, suppliers, businesses, and user authentication.

## Features
- **Items Management**: Add, retrieve, update, and delete inventory items.
- **Stock Management**: Manage stock levels for each item.
- **Transaction Recording**: Record and retrieve purchase/sale transactions.
- **Category and Supplier Management**: Organize items into categories and manage supplier details.
- **Business Management**: Associate users with businesses.
- **Authentication**: User registration, login, and profile endpoints.

## Prerequisites

- **Docker** and **Docker Compose**: [official Docker website](https://www.docker.com/get-started).
- That's it — no Python, no PostgreSQL install, no manual `.env` setup needed.

## Installation

```bash
git clone git@github.com:OkHandTone/reverse_engineering.git
cd reverse_engineering
docker compose up
```

That single command builds the image (first run only), starts the API and the database, generates a `.env` file with working defaults if none exists, runs the database migrations, and creates the default admin user. Once the logs show `Starting development server at http://0.0.0.0:8000/`, the app is ready:

- API: `http://localhost:8000/api/v1/`
- Django admin: `http://localhost:8000/admin/`

### Default admin login

| Field | Default value |
|---|---|
| Username | `admin` |
| Password | `change-me` |
| Email | `admin@example.com` |

**Change this password before exposing the app outside your machine.** It's controlled by `DJANGO_SUPERUSER_PASSWORD` — set it in `.env` before the first `docker compose up` (the superuser is only created once; changing the variable afterwards won't update an existing user).

We strongly recommend logging into [http://localhost:8000/admin/](http://localhost:8000/admin/) right after the first start and using the **"CHANGE PASSWORD"** link (top right, next to your username) to set a new password immediately — don't leave the default `change-me` password active.

## Configuration

A `.env` file is created automatically on first run with the defaults baked into [docker-compose.yml](docker-compose.yml). To customize anything (admin password, database credentials, etc.), create your own `.env` *before* the first launch — it takes precedence over the built-in defaults.

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | Django secret key. Change it for anything beyond local use. | `django-insecure-default-key-change-me` |
| `DEBUG` | `True` or `False`. | `True` |
| `DB_ENGINE` | `sqlite` or `postgres`. **Defaults to `sqlite`** — the bundled Postgres container runs but is unused unless you set this to `postgres`. | `sqlite` |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | PostgreSQL credentials (only used when `DB_ENGINE=postgres`). | `admin` / `admin` / `admin` |
| `POSTGRES_HOST` / `POSTGRES_PORT` | Database host/port. | `inventory_db` / `5432` |
| `DJANGO_SUPERUSER_USERNAME` / `PASSWORD` / `EMAIL` | Default admin account, created automatically on first boot. | see [above](#default-admin-login) |

## Useful commands

```bash
docker compose up -d          # run in the background
docker compose logs -f api    # follow API logs
docker compose down           # stop everything (data is kept in Docker volumes)
docker compose down -v        # stop and wipe the database/venv volumes
docker compose exec api python manage.py <command>   # run any Django management command
```

## API Endpoints

All endpoints are prefixed with `/api/v1/`.

### Categories (`/api/v1/categories/`)
- `GET /` – list categories
- `POST /` – create a category
- `GET /one/{id}` – retrieve a category
- `PUT /update/{id}` – update a category
- `DELETE /delete/{id}` – delete a category

### Items (`/api/v1/items/`)
- `GET /` – list items
- `POST /` – create an item
- `GET /one/{id}` – retrieve an item
- `PUT /update/{id}` – update an item
- `DELETE /delete/{id}` – delete an item

### Stock (`/api/v1/stocks/`)
- `GET /` – list stock entries
- `POST /create` – create a stock entry
- `GET /one/{id}` – retrieve a stock entry
- `PUT /update/{id}` – update a stock entry
- `DELETE /delete/{id}` – delete a stock entry

### Suppliers (`/api/v1/suppliers/`)
- `GET /` – list suppliers
- `POST /create` – create a supplier
- `GET /one/{id}` – retrieve a supplier
- `PUT /update/{id}` – update a supplier
- `DELETE /delete/{id}` – delete a supplier

### Transactions (`/api/v1/transactions/`)
- `GET /` – list transactions
- `POST /create` – create a transaction
- `GET /one/{id}` – retrieve a transaction
- `PUT /update/{id}` – update a transaction
- `DELETE /delete/{id}` – delete a transaction

### Business (`/api/v1/business/`)
- `GET /` – retrieve business info

### Users (`/api/v1/users/`)
- `POST /login/` – log in
- `POST /register/` – register a new user
- `GET /profile/` – retrieve the authenticated user's profile

## Project Structure

Each domain lives in its own Django app (`category_management`, `item_management`, `stock_management`, `supplier_management`, `transaction_management`, `business_management`, `auth_management`), following the standard Django layout:

- `models.py`: data models for the app.
- `serializers.py`: DRF serializers for model instances.
- `views.py`: views handling requests.
- `urls.py`: URL declarations for the app's endpoints.

## Contributing

Contributions are welcome. Feel free to open an issue or a pull request.