create_js_file()
    js_content = document.addEventListener('DOMContentLoaded', function()
    { 
    DOMelements
    const gridSizeSelect = document.getElementById('grid-size');
    const generateBtn = document.getElementById('generate-btn');
    const checkBtn = document.getElementById('check-btn');
    const revealBtn = document.getElementById('reveal-btn');
    const clearBtn = document.getElementById('clear-btn');
    const crosswordGrid = document.getElementById('crossword-grid');
    const acrossClues = document.getElementById('across-clues');
    const downClues = document.getElementById('down-clues');
    const messageDiv = document.getElementById('message');
    
    // Game state
    let currentPuzzle = null;
    let selectedCell = null;
    let currentOrientation = 'across';
    let currentWordStart = null;
    let currentWordCells = [];
    
    // Initialize
    generateBtn.addEventListener('click', generatePuzzle);
    checkBtn.addEventListener('click', checkAnswers);
    revealBtn.addEventListener('click', revealSolution);
    clearBtn.addEventListener('click', clearGrid);
    
    // Generate a puzzle on page load
    generatePuzzle();
    
    function generatePuzzle() {
        const size = parseInt(gridSizeSelect.value);
        messageDiv.textContent = 'Generating puzzle...';
        
        fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ size: size })
        })
        .then(response => response.json())
        .then(data => {
            currentPuzzle = data;
            renderPuzzle(data);
            messageDiv.textContent = 'New puzzle generated!';
        })
        .catch(error => {
            console.error('Error generating puzzle:', error);
            messageDiv.textContent = 'Error generating puzzle. Please try again.';
        });
    }
    
    function renderPuzzle(puzzleData) {
        // Clear previous puzzle
        crosswordGrid.innerHTML = '';
        acrossClues.innerHTML = '';
        downClues.innerHTML = '';
        
        // Set grid size
        const size = puzzleData.grid.length;
        crosswordGrid.style.gridTemplateColumns = `repeat(${size}, 1fr)`;
        crosswordGrid.style.gridTemplateRows = `repeat(${size}, 1fr)`;
        
        // Create the grid cells
        for (let row = 0; row < size; row++) {
            for (let col = 0; col < size; col++) {
                const cell = document.createElement('div');
                cell.className = 'cell';
                cell.dataset.row = row;
                cell.dataset.col = col;
                
                if (puzzleData.grid[row][col] === 0) {
                    cell.classList.add('black');
                } else {
                    // Add cell number if needed
                    const cellNumber = getCellNumber(puzzleData, row, col);
                    if (cellNumber) {
                        const numberSpan = document.createElement('span');
                        numberSpan.className = 'cell-number';
                        numberSpan.textContent = cellNumber;
                        cell.appendChild(numberSpan);
                    }
                    
                    // Add input handling
                    cell.addEventListener('click', () => selectCell(cell, row, col));
                }
                
                crosswordGrid.appendChild(cell);
            }
        }
        
        // Add clues
        renderClues(puzzleData);
        
        // Select the first cell
        selectFirstWord();
    }
    
    function getCellNumber(puzzleData, row, col) {
        for (const wordInfo of puzzleData.placed_words) {
            if (wordInfo.row === row && wordInfo.col === col) {
                return wordInfo.number;
            }
        }
        return null;
    }
    
    function renderClues(puzzleData) {
        // Sort words by number
        const words = puzzleData.placed_words.sort((a, b) => a.number - b.number);
        
        // Organize by orientation
        const acrossWords = words.filter(word => word.orientation === 'across');
        const downWords = words.filter(word => word.orientation === 'down');
        
        // Render across clues
        acrossWords.forEach(word => {
            const li = document.createElement('li');
            li.dataset.number = word.number;
            li.dataset.orientation = 'across';
            li.dataset.row = word.row;
            li.dataset.col = word.col;
            li.textContent = `${word.number}. ${puzzleData.clues.across[word.number]}`;
            li.addEventListener('click', () => selectWordFromClue(li));
            acrossClues.appendChild(li);
        });
        
        // Render down clues
        downWords.forEach(word => {
            const li = document.createElement('li');
            li.dataset.number = word.number;
            li.dataset.orientation = 'down';
            li.dataset.row = word.row;
            li.dataset.col = word.col;
            li.textContent = `${word.number}. ${puzzleData.clues.down[word.number]}`;
            li.addEventListener('click', () => selectWordFromClue(li));
            downClues.appendChild(li);
        });
    }
    
    function selectCell(cell, row, col) {
        // Skip black cells
        if (cell.classList.contains('black')) {
            return;
        }
        
        // Clear previous selection
        clearHighlights();
        
        // Set new selection
        cell.classList.add('selected');
        selectedCell = { cell, row, col };
        
        // Determine which word(s) this cell belongs to
        const acrossWord = findWord(row, col, 'across');
        const downWord = findWord(row, col, 'down');
        
        // If we were already in a word's sequence, maintain the same orientation if possible
        if (currentOrientation === 'across' && acrossWord) {
            highlightWord(acrossWord);
        } else if (currentOrientation === 'down' && downWord) {
            highlightWord(downWord);
        } else if (acrossWord) {
            highlightWord(acrossWord);
        } else if (downWord) {
            highlightWord(downWord);
        }
        
        // Highlight the corresponding clue
        highlightClue();
        
        // Add keyboard listener
        document.removeEventListener('keydown', handleKeyDown);
        document.addEventListener('keydown', handleKeyDown);
    }
    
    function findWord(row, col, orientation) {
        for (const word of currentPuzzle.placed_words) {
            if (word.orientation !== orientation) continue;
            
            const wordRow = word.row;
            const wordCol = word.col;
            const wordLength = word.word.length;
            
            // Check if the cell is part of this word
            if (orientation === 'across') {
                if (row === wordRow && col >= wordCol && col < wordCol + wordLength) {
                    return word;
                }
            } else { // down
                if (col === wordCol && row >= wordRow && row < wordRow + wordLength) {
                    return word;
                }
            }
        }
        
        return null;
    }
    
    function highlightWord(word) {
        const row = word.row;
        const col = word.col;
        const wordLength = word.word.length;
        currentWordCells = [];
        
        // Update orientation
        currentOrientation = word.orientation;
        currentWordStart = { row, col };
        
        if (word.orientation === 'across') {
            for (let c = col; c < col + wordLength; c++) {
                const cellElement = getCellElement(row, c);
                if (cellElement) {
                    cellElement.classList.add('highlight');
                    currentWordCells.push(cellElement);
                }
            }
        } else { // down
            for (let r = row; r < row + wordLength; r++) {
                const cellElement = getCellElement(r, col);
                if (cellElement) {
                    cellElement.classList.add('highlight');
                    currentWordCells.push(cellElement);
                }
            }
        }
    }
    
    function getCellElement(row, col) {
        return document.querySelector(`.cell[data-row="${row}"][data-col="${col}"]`);
    }
    
    function clearHighlights() {
        // Clear cell highlights
        document.querySelectorAll('.cell.selected, .cell.highlight').forEach(cell => {
            cell.classList.remove('selected', 'highlight');
        });
        
        // Clear clue highlights
        document.querySelectorAll('li.active').forEach(clue => {
            clue.classList.remove('active');
        });
    }
    
    function highlightClue() {
        if (!currentWordStart) return;
        
        const clueElements = document.querySelectorAll(`#${currentOrientation}-clues li`);
        clueElements.forEach(li => {
            if (parseInt(li.dataset.row) === currentWordStart.row && 
                parseInt(li.dataset.col) === currentWordStart.col &&
                li.dataset.orientation === currentOrientation) {
                li.classList.add('active');
                li.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        });
    }
    
    function selectWordFromClue(clueElement) {
        const row = parseInt(clueElement.dataset.row);
        const col = parseInt(clueElement.dataset.col);
        const orientation = clueElement.dataset.orientation;
        
        // Find the first cell of the word
        const cell = getCellElement(row, col);
        if (cell) {
            // Set orientation before selecting cell
            currentOrientation = orientation;
            selectCell(cell, row, col);
        }
    }
    
    function selectFirstWord() {
        if (currentPuzzle && currentPuzzle.placed_words.length > 0) {
            const firstWord = currentPuzzle.placed_words[0];
            const cell = getCellElement(firstWord.row, firstWord.col);
            if (cell) {
                currentOrientation = firstWord.orientation;
                selectCell(cell, firstWord.row, firstWord.col);
            }
        }
    }
    
    function handleKeyDown(event) {
        if (!selectedCell) return;
        
        const { row, col } = selectedCell;
        
        if (event.key >= 'a' && event.key <= 'z' || event.key >= 'A' && event.key <= 'Z') {
            // Enter letter
            const cell = getCellElement(row, col);
            cell.textContent = event.key.toUpperCase();
            
            // Move to next cell
            moveToNextCell();
        } else if (event.key === 'Backspace' || event.key === 'Delete') {
            // Delete letter
            const cell = getCellElement(row, col);
            if (cell.textContent.length > 0 && !cell.querySelector('.cell-number')) {
                cell.textContent = '';
            } else if (cell.querySelector('.cell-number')) {
                const numberSpan = cell.querySelector('.cell-number');
                cell.textContent = '';
                cell.appendChild(numberSpan);
            }
            
            // Move to previous cell
            moveToPreviousCell();
        } else if (event.key === 'ArrowLeft') {
            moveInDirection(0, -1);
            event.preventDefault();
        } else if (event.key === 'ArrowRight') {
            moveInDirection(0, 1);
            event.preventDefault();
        } else if (event.key === 'ArrowUp') {
            moveInDirection(-1, 0);
            event.preventDefault();
        } else if (event.key === 'ArrowDown') {
            moveInDirection(1, 0);
            event.preventDefault();
        } else if (event.key === 'Tab') {
            // Switch orientation
            currentOrientation = currentOrientation === 'across' ? 'down' : 'across';
            selectCell(selectedCell.cell, row, col);
            event.preventDefault();
        }
    }
    
    function moveToNextCell() {
        if (!selectedCell) return;
        
        const { row, col } = selectedCell;
        
        if (currentOrientation === 'across') {
            moveInDirection(0, 1);
        } else { // down
            moveInDirection(1, 0);
        }
    }
    
    function moveToPreviousCell() {
        if (!selectedCell) return;
        
        const { row, col } = selectedCell;
        
        if (currentOrientation === 'across') {
            moveInDirection(0, -1);
        } else { // down
            moveInDirection(-1, 0);
        }
    }
    
    function moveInDirection(rowDelta, colDelta) {
        if (!selectedCell) return;
        
        const { row, col } = selectedCell;
        const newRow = row + rowDelta;
        const newCol = col + colDelta;
        
        // Check bounds
        if (newRow < 0 || newRow >= currentPuzzle.grid.length || 
            newCol < 0 || newCol >= currentPuzzle.grid[0].length) {
            return;
        }
        
        // Get new cell
        const newCell = getCellElement(newRow, newCol);
        
        // Skip black cells
        if (newCell && !newCell.classList.contains('black')) {
            selectCell(newCell, newRow, newCol);
        }
    }
    
    function checkAnswers() {
        let allCorrect = true;
        
        for (const word of currentPuzzle.placed_words) {
            const row = word.row;
            const col = word.col;
            const orientation = word.orientation;
            const letters = word.word.toUpperCase();
            
            for (let i = 0; i < letters.length; i++) {
                const r = orientation === 'across' ? row : row + i;
                const c = orientation === 'across' ? col + i : col;
                const cell = getCellElement(r, c);
                
                // Get cell text, excluding the cell number
                let cellText = cell.textContent.replace(/\\d+\\s*/, '').trim().toUpperCase();
                if (cell.querySelector('.cell-number')) {
                    cellText = cellText.replace(cell.querySelector('.cell-number').textContent, '');
                }
                
                if (cellText !== letters[i]) {
                    cell.classList.add('incorrect');
                    allCorrect = false;
                } else {
                    cell.classList.add('correct');
                }
            }
        }
        
        if (allCorrect) {
            messageDiv.textContent = 'Congratulations! All answers are correct!';
        } else {
            messageDiv.textContent = 'Some answers are incorrect. Keep trying!';
        }
        
        // Remove marks after 2 seconds
        setTimeout(() => {
            document.querySelectorAll('.cell.correct, .cell.incorrect').forEach(cell => {
                cell.classList.remove('correct', 'incorrect');
            });
        }, 2000);
    }
    
    function revealSolution() {
        if (confirm('Are you sure you want to reveal the solution?')) {
            for (const word of currentPuzzle.placed_words) {
                const row = word.row;
                const col = word.col;
                const orientation = word.orientation;
                const letters = word.word.toUpperCase();
                
                for (let i = 0; i < letters.length; i++) {
                    const r = orientation === 'across' ? row : row + i;
                    const c = orientation === 'across' ? col + i : col;
                    const cell = getCellElement(r, c);
                    
                    // Clear cell content first
                    cell.textContent = '';
                    
                    // Add cell number back if it exists
                    const cellNumber = getCellNumber(currentPuzzle, r, c);
                    if (cellNumber) {
                        const numberSpan = document.createElement('span');
                        numberSpan.className = 'cell-number';
                        numberSpan.textContent = cellNumber;
                        cell.appendChild(numberSpan);
                        }
                    
                    // Add letter
                    cell.textContent += letters[i];
                }
            }
            
            messageDiv.textContent = 'Solution revealed.';
        }
    }
    
    function clearGrid() {
        if (confirm('Are you sure you want to clear all your answers?')) {
            for (let row = 0; row < currentPuzzle.grid.length; row++) {
                for (let col = 0; col < currentPuzzle.grid[0].length; col++) {
                    if (currentPuzzle.grid[row][col] !== 0) {
                        const cell = getCellElement(row, col);
                        
                        // Clear cell content
                        cell.textContent = '';
                        
                        // Add cell number back if it exists
                        const cellNumber = getCellNumber(currentPuzzle, row, col);
                        if (cellNumber) {
                            const numberSpan = document.createElement('span');
                            numberSpan.className = 'cell-number';
                            numberSpan.textContent = cellNumber;
                            cell.appendChild(numberSpan);
                        }
                    }
                }
            }
            
            messageDiv.textContent = 'Grid cleared.';
        }
    }
});