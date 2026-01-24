import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import json
import base64

# Google API scopes
SCOPES = ['https://www.googleapis.com/auth/documents']

def get_google_docs_service():
    """Get authenticated Google Docs API service using service account."""
    
    # Try environment variable first (for Kubernetes/cloud deployments)
    if os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY'):
        try:
            # Decode base64-encoded key from environment variable
            key_data = base64.b64decode(os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY'))
            service_account_info = json.loads(key_data)
            creds = service_account.Credentials.from_service_account_info(
                service_account_info, scopes=SCOPES)
        except Exception as e:
            raise ValueError(f"Failed to parse GOOGLE_SERVICE_ACCOUNT_KEY environment variable: {str(e)}")
    else:
        # Fall back to file (for local development)
        service_account_file = 'service-account-key.json'
        
        if not os.path.exists(service_account_file):
            raise FileNotFoundError(
                f"Service account key file '{service_account_file}' not found. "
                "Please follow the instructions in GOOGLE_API_SETUP.md to create and download your service account key."
            )
        
        # Create credentials from service account file
        creds = service_account.Credentials.from_service_account_file(
            service_account_file, scopes=SCOPES)
    
    service = build('docs', 'v1', credentials=creds)
    return service

def load_google_drive_file(file_id, is_doc=True):
    """Load text content from a Google Drive file ID."""
    if is_doc:
        download_url = f'https://docs.google.com/document/d/{file_id}/export?format=txt'
    else:
        download_url = f'https://drive.google.com/uc?export=download&id={file_id}'
    
    try:
        response = requests.get(download_url)
        response.raise_for_status()
        # Strip BOM character that Google Docs adds
        return response.text.lstrip('\ufeff')
    except requests.exceptions.RequestException as e:
        return f"Error loading file: {str(e)}"

def append_words_to_google_doc(file_id, new_words):
    """
    Append words to a Google Doc and sort all words alphabetically.
    
    Args:
        file_id: The Google Drive document ID
        new_words: List of words to add
        
    Returns:
        dict with status and message
    """
    try:
        service = get_google_docs_service()
        
        # First, read the current document content
        document = service.documents().get(documentId=file_id).execute()
        content = document.get('body').get('content')
        
        # Extract text from the document
        current_text = ''
        for element in content:
            if 'paragraph' in element:
                for text_run in element['paragraph'].get('elements', []):
                    if 'textRun' in text_run:
                        current_text += text_run['textRun'].get('content', '')
        
        # Parse existing words
        existing_words = set()
        for line in current_text.splitlines():
            line = line.strip()
            if line:
                existing_words.add(line.lower())
        
        # Add new words
        for word in new_words:
            word = word.strip().lower()
            if word:
                existing_words.add(word)
        
        # Sort all words alphabetically
        sorted_words = sorted(existing_words)
        new_content = '\n'.join(sorted_words)
        
        # Get document length to delete all content
        doc_length = len(current_text)
        
        # Build requests to update the document
        requests_list = [
            # Delete all existing content
            {
                'deleteContentRange': {
                    'range': {
                        'startIndex': 1,
                        'endIndex': doc_length
                    }
                }
            },
            # Insert sorted content
            {
                'insertText': {
                    'location': {
                        'index': 1
                    },
                    'text': new_content
                }
            }
        ]
        
        # Execute the batch update
        result = service.documents().batchUpdate(
            documentId=file_id,
            body={'requests': requests_list}
        ).execute()
        
        return {
            'status': 'success',
            'message': f'Added {len(new_words)} new words. Total: {len(sorted_words)} words.',
            'total_words': len(sorted_words),
            'new_words_count': len(new_words)
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }

def process_word_lines(lines):
    """Process word lines, splitting on '/' and spaces to create separate entries."""
    import re
    words = set()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Split by both '/' and spaces
        parts = re.split(r'[/\s]+', line)
        words.update(part for part in parts if part)
    
    return words

def expand_word( w, all_words):
    # nothing to do if there are no parentheses
    if '(' not in w or ')' not in w:
        return [w]
    
    if w.count('(') != w.count(')'):
        print( w, "is ill_formed" )
        exit(0)
    
    options = []
    # snag all the options within parentheses
    for i, char in enumerate(w):
        if char == '(':
            start = i
        elif char == ')':
            end = i
            guts = w[start+1:end]
            options.append( guts )

    # base word is the word with all the parentheses and their contents removed
    base_word = w
    for opt in options:
        base_word = base_word.replace( f'({opt})', '' ) 

    out = []
    if base_word in all_words:
        out.append( base_word )

    # now we make permutations of the word by appending each optional suffix
    for suffix in options:
        new_word = base_word + suffix
        if new_word in all_words:
            out.append( new_word )  
    return out

def expand_words( words, all_words ):
    out = []
    for word in words:
        expanded = expand_word( word, all_words )
        out.extend( expanded )
    return out

def is_possible(word, letters):
  word_letters = set(word)
  # how many unique letters are in the word
  word_letter_count = len(word_letters)
  # words with more than 7 unique letters are impossible
  if word_letter_count > 7:
    return False
  # how many unique letters are specified by user
  avail_wildcards = 7 - len(letters)
  good_letter_count = len(letters.union(word_letters))
  needed_wildcards = word_letter_count - good_letter_count
  if needed_wildcards > avail_wildcards:
      return False

  return True

def get_possibles( words, all_words, letters, starts_with, must_contain, word_list, word_lengths=None ):
    # Validate inputs
    if not (letters and letters.isalpha() and len(letters) <= 7):
        return []
    if starts_with and (not starts_with.isalpha() or len(starts_with) > 2):
        return []
    if must_contain and (not must_contain.isalpha() or len(must_contain) > 1):
        return []
    
    # Select word list based on user choice
    if word_list == 'all':
        # Union of expanded regular words and all words
        selected_words = set(words).union(all_words)
    else:
        selected_words = words
    
    # Find words that contain all of the provided letters
    if len(letters) == 7:
        candidates = sorted([word for word in selected_words if all(letter in letters for letter in word.lower())])
    else:
        letters_set = set(letters)
        candidates = sorted(list(filter(lambda word: is_possible(word, letters_set), selected_words)))
        
    matched_words = candidates[:]
    # Apply starts_with filter
    if starts_with:
        matched_words = [word for word in matched_words if word.lower().startswith(starts_with)]
    
    # Apply must_contain filter
    if must_contain:
        matched_words = [word for word in matched_words if must_contain in word.lower()]
    
    # Apply word length filter
    if word_lengths:
        def matches_length(word):
            word_len = len(word)
            for length in word_lengths:
                if length == '12+':
                    if word_len >= 12:
                        return True
                elif str(word_len) == str(length):
                    return True
            return False
        
        candidates = [word for word in candidates if matches_length(word)]
        matched_words = [word for word in matched_words if matches_length(word)]
    
    matched_words = sorted(matched_words)
    
    # Group matched_words by length (descending)
    from collections import defaultdict
    grouped_words = defaultdict(list)
    letters_set = set(letters)
    for word in matched_words:
        # Mark if word is in regular word list
        in_regular_list = word.lower() in words
        # Check if word is a pangram (uses all 7 letters)
        is_pangram = len(letters) == 7 and len(set(word.lower()) - letters_set) == 0 and len(set(word.lower())) == 7
        grouped_words[len(word)].append({
            'word': word, 
            'in_regular': in_regular_list,
            'is_pangram': is_pangram
        })
    
    # Sort by length descending
    grouped_words_sorted = dict(sorted(grouped_words.items(), key=lambda x: x[0], reverse=True))
    #print( matched_words)

    return ( candidates, grouped_words_sorted )