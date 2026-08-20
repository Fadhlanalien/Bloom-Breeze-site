# Bloom Breeze

Bloom Breeze is a Flask-based online clothing store that allows users to browse clothing products, select product variants, add items to a shopping cart, and place orders.

## Features

* User registration and login
* Browse clothing products
* Product detail pages
* Multiple product images
* Product variants based on size and colour
* Shopping cart
* Buy Now functionality
* Checkout
* Shipping information
* Order placement
* Order status management
* Admin functionality for managing products and orders
* Responsive user interface for different screen sizes

## Technologies Used

### Backend

* Python
* Flask

### Frontend

* HTML
* CSS
* Bootstrap
* JavaScript

### Database

* PostgreSQL

### Deployment

* Render

## Project Structure

```text
Bloom_Breeze/
│
├── static/
│   ├── CSS/
│   ├── images/
│   └── ...
│
├── templates/
│   ├── ...
│
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

> The project structure may change as the application is developed.

## Database

Bloom Breeze uses PostgreSQL as its database.

The application uses an environment variable for the database connection:

```text
DATABASE_URL
```

The database URL should not be stored directly in the source code or committed to the repository.

## Running the Project Locally

### 1. Clone the repository

```bash
git clone <repository-url>
cd Bloom_Breeze
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
```

### 3. Activate the virtual environment

On Linux/WSL:

```bash
source venv/bin/activate
```

On Windows:

```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Set the required environment variables, including:

```text
DATABASE_URL
```

### 6. Run the application

For local Flask development:

```bash
python app.py
```

The application can then be accessed through the local address displayed by Flask.

## Running with Gunicorn

The application can also be run using Gunicorn:

### 1. Run the init_db

```bash
python init_db.py
```

### 2. Run the application
```bash
gunicorn app:app
```

The exact command depends on the Python file containing the Flask application and the name of the Flask application object.

## Deployment

Bloom Breeze is planned to be deployed using Render.

The deployment will use:

* GitHub for source code management
* Render for hosting the Flask application
* PostgreSQL for the production database
* Gunicorn as the application server

## Environment Variables

The following environment variables should be configured in the deployment environment:

```text
DATABASE_URL
```

Sensitive values such as database credentials should be stored as environment variables and should not be committed to GitHub.

## Status

🚧 **Development / Deployment in Progress**

The application is currently being prepared for deployment on Render.

## License

This project currently does not include a specific open-source license.
