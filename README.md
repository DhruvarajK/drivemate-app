# DriveMate

DriveMate is a comprehensive ride-hailing and driver-matching platform built with Django. It facilitates seamless connections between customers and professional drivers, offering flexible ride modes and robust management tools for both parties.

## Key Features

- **Multi-Role User System**: Dedicated interfaces and functionalities for Customers, Drivers, and Administrators.
- **Flexible Ride Modes**: 
  - **Car with Driver**: Complete transportation service including a vehicle and a professional driver.
  - **Driver Only**: For customers who have a vehicle but require a professional driver.
- **Advanced Driver Matching**: Sophisticated algorithm to find the nearest available drivers based on haversine distance.
- **Filtering and Preferences**: Filter results based on vehicle type, transmission, fuel type, and driver ratings. Includes support for female driver preferences.
- **Trip Management**: Real-time ride requests, status tracking (pending, accepted, completed, cancelled), and trip history.
- **Rating and Feedback**: Integrated system for customers to rate their experience with both drivers and vehicles.
- **Payment Integration**: Streamlined payment processing module for ride transactions.
- **Administrative Dashboard**: Comprehensive management tools for overseeing users, vehicles, and rides.

## Technology Stack

- **Backend**: Python 3.x, Django 4.0+
- **API**: Django REST Framework
- **Database**: SQLite (Development), PostgreSQL (Production ready)
- **Frontend**: HTML5, CSS3, JavaScript
- **Deployment**: Uvicorn, WhiteNoise for static file management

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/DhruvarajK/drivemate-app.git
   cd drivemate-app
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows
   .\venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Perform database migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Create a superuser for administrative access:
   ```bash
   python manage.py createsuperuser
   ```

6. Start the development server:
   ```bash
   python manage.py runserver
   ```

The application will be accessible at `http://127.0.0.1:8000/`.

## Directory Structure

- `accounts/`: User authentication and profile management.
- `rides/`: Core ride Booking, matching, and tracking logic.
- `vehicles/`: Vehicle inventory and details management.
- `payments/`: Financial transaction and payment state handling.
- `myadmin/`: Custom administrative interfaces and analytics.
- `DriveMate/`: Project configuration and settings.

## Deployment

The project is configured for deployment on platforms like Render or Heroku. It includes `whitenoise` for serving static files and `uvicorn` for ASGI support. Ensure environment variables for `SECRET_KEY` and database configurations are properly set in production.
