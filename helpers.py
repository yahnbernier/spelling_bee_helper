import requests

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