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
- Or, for a local (non-Docker) setup: **Python 3.10+** and a local **PostgreSQL** instance.

## Configuration

This project reads its configuration from environment variables. Copy the example file and fill in your own values:

```bash
cp .env.example .env
```

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key. Generate one, never reuse the example value. |
| `DEBUG` | `True` or `False`. |
| `POSTGRES_USER` | PostgreSQL username. |
| `POSTGRES_PASSWORD` | PostgreSQL password. |
| `POSTGRES_DB` | PostgreSQL database name. |
| `POSTGRES_HOST` | Database host (`inventory_db` when using Docker Compose, `localhost` otherwise). |
| `POSTGRES_PORT` | Database port (`5432` by default). |

## Installation with Docker (recommended)

1. **Clone the repository**:
   ```bash
   git clone git@github.com:OkHandTone/reverse_engineering.git
   cd reverse_engineering
   ```

2. **Create your `.env` file** (see [Configuration](#configuration)):
   ```bash
   cp .env.example .env
   ```

3. **Build the Docker containers**:
   ```bash
   docker compose build
   ```

4. **Start the containers**:
   ```bash
   docker compose up
   ```

5. **Run database migrations** (in another terminal, once the containers are up):
   ```bash
   docker compose exec api python manage.py migrate
   ```

6. **Create an admin user**:
   ```bash
   docker compose exec api python manage.py createsuperuser
   ```

The API is then available at `http://localhost:8000/api/v1/`, and the Django admin at `http://localhost:8000/admin/`.

## Installation without Docker

1. **Clone the repository** and move into it.

2. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # on Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create your `.env` file** and set `POSTGRES_HOST=localhost` (assuming PostgreSQL runs locally).

5. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

6. **Create an admin user**:
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the development server**:
   ```bash
   python manage.py runserver 0.0.0.0:8000
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
