# OpenTicket-Django

![Django](https://img.shields.io/badge/Django-5.0%2B-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Black](https://img.shields.io/badge/code%20style-black-000000)

OpenTicket-Django is a ticket management system built using the Django framework. It provides a platform for creating, managing, and tracking tickets for various use cases.

## Features

- User authentication and authorization
- Create, update, and delete tickets
- Assign tickets to users
- Track ticket status and priority
- Search and filter tickets
- Responsive design for desktop and mobile

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/RedsonBr140/OpenTicket-Django.git
   cd OpenTicket-Django
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Apply migrations:

   ```bash
   python manage.py migrate
   ```

5. Run the development server:

   ```bash
   python manage.py runserver
   ```

6. Access the application at `http://127.0.0.1:8000`.

## Usage

1. Register or log in to your account.
2. Create new tickets and assign them to users.
3. Update ticket details or change their status as needed.
4. Use the search and filter options to manage tickets efficiently.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Commit your changes and push them to your fork.
4. Submit a pull request with a detailed description of your changes.

## Contact

For questions or support, please contact [redson@riseup.net].
