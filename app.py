from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests
import time
from  helpers import *

app = Flask(__name__)

# Google drive file with regular words
GOOGLE_FILE_ID_REGULAR_WORDS = '1fd_ml5_Lk8jv09LIbYddH_tgdg-6TozZyuXxhoJ4XHI'
ALL_WORDS_FILENAME = 'static/words_spellingbee.txt'

# word file just a .txt file
def load_word_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()
    
# NOTE: this loads words into global words variable
def load_regular_words(file_id):
    """Load and process regular words from Google Drive."""
    global words
    
    # Load regular words
    start_time = time.time()
    contents = load_google_drive_file(file_id, is_doc=True)
    words_set = process_word_lines(contents.splitlines())
    load_time = time.time() - start_time
    
    # Expand regular words
    oldc = len(words_set)
    start_time = time.time()
    words = expand_words(list(words_set), all_words)
    
    # Check if any words contain anything other than letters and print the offending words
    for word in words:
        if not word.isalpha():
            print(f" * Warning: word '{word}' contains non-letter characters.")
    
    expand_time = time.time() - start_time
    
    print(f" * Loaded words: {len(words_set)} in {load_time:.3f}s")
    print(f" * Expanded words: {len(words)} from {oldc} original entries in {expand_time:.3f}s")
    
    return {
        'regular_words': len(words),
        'regular_original': oldc,
        'regular_load_time': load_time,
        'expand_time': expand_time
    }

# Load all words list first (regular file, not a document)
def load_all_words( all_words_filename ):
    start_time = time.time()
    contents = load_word_file( all_words_filename ) 
    all_words = set(contents.splitlines())
    load_time = time.time() - start_time
    print(f" * Loaded all words: {len(all_words)} in {load_time:.3f}s")
    return all_words

# load all words first
all_words = load_all_words( ALL_WORDS_FILENAME )

# Load regular words using shared function
load_regular_words(GOOGLE_FILE_ID_REGULAR_WORDS)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        letters = request.form.get('letters', '').strip()
        starts_with = request.form.get('starts_with', '').strip().lower()
        must_contain = request.form.get('must_contain', '').strip().lower()
        word_list = request.form.get('word_list', 'regular')  # 'regular' or 'all'
        word_lengths = request.form.getlist('length')  # Get all checked length values

        letters = set(letters.lower())
        letters.update(set(starts_with))   
        letters.update(set(must_contain))
        letters=''.join(letters)
        
        (possibles, candidates) = get_possibles( words, all_words, letters, starts_with, must_contain, word_list, word_lengths )
            
        return render_template('index.html', 
                             letters=letters, 
                             starts_with=starts_with, 
                             must_contain=must_contain,
                             word_list=word_list,
                             word_lengths=word_lengths,
                             possibles=possibles, 
                             candidates=candidates)
    # GET request - show empty form
    return render_template('index.html', letters='', starts_with='', must_contain='', word_list='regular', word_lengths=[], possibles=[], candidates={})

@app.route('/api/search', methods=['GET'])
def api_search():
    letters_input = request.args.get('letters', '').strip().lower()
    starts_with = request.args.get('starts_with', '').strip().lower()
    must_contain = request.args.get('must_contain', '').strip().lower()
    word_list = request.args.get('word_list', 'regular')  # 'regular' or 'all'
    word_lengths = request.args.getlist('length')  # Get all checked length values
    
    # Combine all letters from all inputs
    letters = set(letters_input)
    letters.update(set(starts_with))
    letters.update(set(must_contain))
    letters=''.join(letters)

    # Validate inputs - now checking combined letters
    if not letters:
        return jsonify({'possibles': [], 'candidates': []})
    
    if not (letters.isalpha() and len(letters) <= 7):
        return jsonify({'error': 'Combined letters must be 1-7 alphabetic characters'}), 400
    if starts_with and (not starts_with.isalpha() or len(starts_with) > 2):
        return jsonify({'error': 'Starts with must be 0-2 alphabetic characters'}), 400
    if must_contain and (not must_contain.isalpha() or len(must_contain) > 1):
        return jsonify({'error': 'Must contain must be 0-1 alphabetic character'}), 400

    (possibles, candidates) = get_possibles( words, all_words, letters, starts_with, must_contain, word_list, word_lengths )
        
    return jsonify({
        'possibles': possibles,
        'candidates': candidates
    })

@app.route('/reload', methods=['POST'])
def reload():
    """Manually reload word lists from Google Drive."""
    try:
        stats = load_regular_words(GOOGLE_FILE_ID_REGULAR_WORDS)
        print(f" * Reloaded - Regular: {stats['regular_words']} (from {stats['regular_original']}) in {stats['regular_load_time']:.3f}s, Expand: {stats['expand_time']:.3f}s")
        return jsonify({
            'status': 'success',
            'message': 'Word lists reloaded successfully',
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
