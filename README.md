# Spelling Bee

A Flask-based spelling practice web application.

## Project Structure

```
spelling_bee/
├── app.py              # Main Flask application
├── templates/          # HTML templates
│   ├── index.html
│   └── about.html
├── static/            # Static assets
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

## Setup Instructions

1. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment**:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. **Start the Flask development server**:
   ```bash
   python app.py
   ```

2. **Open your browser** and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

## Development

- The application runs in debug mode by default during development
- Changes to Python files will automatically reload the server
- Static files (CSS/JS) changes may require a browser refresh

## Features

- Basic Flask web application structure
- Template rendering with Jinja2
- Static file serving (CSS, JavaScript)
- Simple navigation between pages

## Next Steps

- Add spelling bee game logic
- Implement word database
- Add user authentication (optional)
- Create API endpoints for game functionality
