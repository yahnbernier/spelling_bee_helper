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

- **Letter-based word search**: Find words using up to 7 letters
- **Advanced filters**: 
  - "Starts With" filter (up to 2 letters)
  - "Must Contain" filter (1 letter)
  - Word length filters (4-12+ letters)
- **Word list options**: Regular words vs. All words
- **Real-time search**: Results update as you type
- **Word management**:
  - Check words to add them to your list
  - Manual entry for additional words
  - Copy selected words to clipboard
  - **Append to Google Drive**: Save selected words directly to your Google Drive document with automatic alphabetical sorting
- **Pangram detection**: Automatically highlights words that use all 7 letters
- **Persistent search**: Search state is saved and restored between sessions
- **Live reload**: Refresh word lists from Google Drive without restarting

## Append to Google Drive Feature

The "Append" button allows you to save selected words directly to your Google Drive document. The feature:
- Appends new words to your Google Drive document (identified by `GOOGLE_FILE_ID_REGULAR_WORDS`)
- Automatically sorts the entire document alphabetically
- Removes duplicates
- Reloads the word list after appending

### Setup Google Drive Integration

To use the Append feature, you need to set up Google API credentials. See [GOOGLE_API_SETUP.md](GOOGLE_API_SETUP.md) for detailed instructions.

Quick steps:
1. Create a Google Cloud Project
2. Enable Google Docs API
3. Download OAuth credentials as `credentials.json`
4. Place `credentials.json` in the project root
5. First time you click "Append", you'll authenticate via browser
6. A `token.pickle` file will be created for future authentication

## Next Steps

- Implement additional word expansion rules
- Add word history tracking
- Create export options for different formats
