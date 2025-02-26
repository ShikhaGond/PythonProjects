import os
import random
import json
import numpy as np
from flask import Flask, render_template, request, jsonify
import nltk
from nltk.corpus import words

# Download NLTK data (first-time setup)
nltk.download('words')

# Initialize Flask app
app = Flask(__name__)

class CrosswordGenerator:
    def __init__(self, size=15, min_word_length=3):
        self.size = size
        self.min_word_length = min_word_length
        self.grid = np.zeros((size, size), dtype=int)
        self.word_list = [w for w in words.words() if len(w) >= min_word_length and len(w) <= size and w.isalpha()]
        self.placed_words = []
        self.clues = {}
        
    def generate_crossword(self, max_attempts=100, target_words=25):
        """Generate a crossword puzzle with words and clues"""
        self.grid = np.zeros((self.size, self.size), dtype=int)
        self.placed_words = []
        self.clues = {'across': {}, 'down': {}}
        
        attempts = 0
        while attempts < max_attempts and len(self.placed_words) < target_words:
            word = random.choice(self.word_list)
            if word in [w['word'] for w in self.placed_words]:
                continue
                
            # Try to place word horizontally or vertically
            orientation = random.choice(['across', 'down'])
            success = self._place_word(word, orientation)
            
            if success:
                # Generate a simple clue
                clue = self._generate_clue(word)
                word_info = {'word': word, 'row': success[0], 'col': success[1], 'orientation': orientation, 'number': len(self.placed_words) + 1}
                self.placed_words.append(word_info)
                self.clues[orientation][len(self.placed_words)] = clue
            
            attempts += 1
            
        # Number the grid
        self._number_grid()
        
        return {
            'grid': self.grid.tolist(),
            'placed_words': self.placed_words,
            'clues': self.clues
        }
    
    def _place_word(self, word, orientation):
        """Attempt to place a word on the grid in the given orientation"""
        word = word.upper()
        word_length = len(word)
        
        if orientation == 'across':
            max_row = self.size
            max_col = self.size - word_length + 1
        else:  # down
            max_row = self.size - word_length + 1
            max_col = self.size
            
        # Try random positions
        positions = [(r, c) for r in range(max_row) for c in range(max_col)]
        random.shuffle(positions)
        
        for row, col in positions:
            if self._can_place_word(word, row, col, orientation):
                # Place the word
                for i, letter in enumerate(word):
                    if orientation == 'across':
                        self.grid[row][col + i] = ord(letter)
                    else:  # down
                        self.grid[row + i][col] = ord(letter)
                return (row, col)
                
        return False
    
    def _can_place_word(self, word, row, col, orientation):
        """Check if a word can be placed at the given position and orientation"""
        word = word.upper()
        word_length = len(word)
        intersections = 0
        
        for i, letter in enumerate(word):
            r, c = (row, col + i) if orientation == 'across' else (row + i, col)
            
            # Check if position is filled with a different letter
            if self.grid[r][c] != 0 and self.grid[r][c] != ord(letter):
                return False
                
            # Count intersections with existing letters
            if self.grid[r][c] == ord(letter):
                intersections += 1
                
            # Check adjacent cells to ensure words don't run together
            if orientation == 'across':
                # Check left of first letter
                if i == 0 and c > 0 and self.grid[r][c-1] != 0:
                    return False
                # Check right of last letter
                if i == word_length - 1 and c < self.size - 1 and self.grid[r][c+1] != 0:
                    return False
            else:  # down
                # Check above first letter
                if i == 0 and r > 0 and self.grid[r-1][c] != 0:
                    return False
                # Check below last letter
                if i == word_length - 1 and r < self.size - 1 and self.grid[r+1][c] != 0:
                    return False
        
        # If this is the first word, place it or require at least one intersection
        if len(self.placed_words) == 0 or intersections > 0:
            return True
            
        return False
    
    def _number_grid(self):
        """Number the grid for clue references"""
        number = 1
        numbered_grid = np.zeros((self.size, self.size), dtype=int)
        
        for r in range(self.size):
            for c in range(self.size):
                # If cell has a letter and is the start of across or down word
                if self.grid[r][c] != 0:
                    is_across_start = (c == 0 or self.grid[r][c-1] == 0) and (c < self.size - 1 and self.grid[r][c+1] != 0)
                    is_down_start = (r == 0 or self.grid[r-1][c] == 0) and (r < self.size - 1 and self.grid[r+1][c] != 0)
                    
                    if is_across_start or is_down_start:
                        numbered_grid[r][c] = number
                        
                        # Update word numbers in placed_words list
                        for word_info in self.placed_words:
                            if word_info['row'] == r and word_info['col'] == c:
                                word_info['number'] = number
                        
                        number += 1
        
        self.numbered_grid = numbered_grid.tolist()
        return self.numbered_grid
    
    def _generate_clue(self, word):
        """Generate a simple clue for the given word"""
        word = word.lower()
        
        # Dictionary of simple clues - in a real application, you'd use a more sophisticated approach
        simple_clues = {
            'cat': 'A domestic feline',
            'dog': 'Man\'s best friend',
            'house': 'A place to live',
            'car': 'A four-wheeled vehicle',
            'book': 'Written or printed work',
            'tree': 'Woody perennial plant',
            'water': 'H2O',
            'computer': 'Electronic device for processing data',
            'phone': 'Communication device',
            'coffee': 'Popular caffeinated beverage'
        }
        
        # Return a predefined clue or generate a basic one
        if word in simple_clues:
            return simple_clues[word]
        else:
            return f"Definition of {word}"

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    size = request.json.get('size', 15)
    generator = CrosswordGenerator(size=size)
    crossword_data = generator.generate_crossword()
    return jsonify(crossword_data)

@app.route('/check', methods=['POST'])
def check_answer():
    user_input = request.json.get('input', '').upper()
    word = request.json.get('word', '').upper()
    
    if user_input == word:
        return jsonify({'correct': True})
    return jsonify({'correct': False})

# Create directories for templates and static files
def setup_directories():
    if not os.path.exists('templates'):
        os.makedirs('templates')
    if not os.path.exists('static'):
        os.makedirs('static')
    if not os.path.exists('static/css'):
        os.makedirs('static/css')
    if not os.path.exists('static/js'):
        os.makedirs('static/js')


# Create HTML template
def create_html_template():
    html_content = """
    
""" 
    with open('templates/index.html', 'w') as f:
        f.write(html_content)

# Create CSS file
def create_css_file():
    css_content = """

    """
    
    with open('static/css/style.css', 'w') as f:
        f.write(css_content)

