# Advanced Todo Application

A modern, feature-rich todo application built with Django that includes advanced functionality such as user authentication, task sharing, file attachments, and more.

## Features

- **User Authentication**: Secure login and registration system
- **Task Management**: Create, read, update, and delete todos
- **Categories**: Organize tasks into custom categories with colors
- **Priority Levels**: Set priority (low, medium, high) for tasks
- **Due Dates**: Set deadlines for tasks
- **File Attachments**: Upload files to tasks
- **Task Sharing**: Share tasks with other users with view or edit permissions
- **Search & Filter**: Find tasks by title, description, status, or category
- **Modern UI**: Responsive design with dark/light mode support
- **Drag & Drop**: Intuitive task management interface
- **Real-time Notifications**: Get notified about task updates
- **Data Export/Import**: Backup and restore your tasks

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd todo
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Run database migrations:
```bash
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Start the development server:
```bash
python manage.py runserver
```

## Usage

1. Access the application at `http://127.0.0.1:8000/`
2. Register a new account or log in with your superuser credentials
3. Create tasks, organize them with categories, set due dates and priorities
4. Share tasks with other users
5. Use the search and filter functionality to find specific tasks

## Project Structure

```
todo/                     # Project root
├── core/                 # Django project settings
│   ├── settings.py       # Configuration settings
│   ├── urls.py          # Main URL configuration
│   └── wsgi.py          # WSGI application
├── todo/                 # Todo application
│   ├── models.py        # Database models
│   ├── views.py         # View functions
│   ├── urls.py          # App URL configuration
│   ├── templates/       # HTML templates
│   │   └── todo/        # Todo-specific templates
│   ├── static/          # Static files (CSS, JS, images)
│   └── migrations/      # Database migrations
├── media/                # User-uploaded files
├── requirements.txt      # Python dependencies
└── README.md            # Project documentation
```

## API Endpoints

- `GET /` - Todo list view
- `GET/POST /create/` - Create a new todo
- `GET/POST /update/<id>/` - Update an existing todo
- `GET/POST /delete/<id>/` - Delete a todo
- `POST /toggle-complete/<id>/` - Toggle todo completion status
- `POST /share/<id>/` - Share a todo with another user
- `GET /search/` - Search todos
- `POST /category/create/` - Create a new category

## Technologies Used

- **Backend**: Django (Python)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Database**: SQLite (default), supports PostgreSQL, MySQL
- **Template Engine**: Django Templates
- **Icons**: Font Awesome, Bootstrap Icons

## Customization

### Adding New Features

1. Create new models in `todo/models.py`
2. Create views in `todo/views.py`
3. Add URL patterns in `todo/urls.py`
4. Create templates in `todo/templates/todo/`
5. Update the navigation in `todo/templates/base.html`

### Styling

The application uses Bootstrap 5 for responsive design. You can customize the appearance by:

1. Adding custom CSS to the `base.html` template
2. Creating a `static` folder and linking CSS files
3. Modifying the theme variables in the `base.html` style section

## Security Features

- CSRF protection for all forms
- SQL injection prevention through Django ORM
- XSS protection through template auto-escaping
- User authentication and authorization
- File upload validation

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.