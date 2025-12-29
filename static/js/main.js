// Main JavaScript file for Spelling Bee application
console.log('Spelling Bee app loaded');

document.addEventListener('DOMContentLoaded', function() {
    const loadBtn = document.getElementById('load-btn');
    const driveUrlInput = document.getElementById('drive-url');
    const statusDiv = document.getElementById('status');
    const fileContentPre = document.getElementById('file-content');
    
    if (loadBtn) {
        loadBtn.addEventListener('click', async function() {
            const url = driveUrlInput.value.trim();
            
            if (!url) {
                statusDiv.textContent = 'Please enter a Google Drive URL';
                statusDiv.className = 'error';
                return;
            }
            
            statusDiv.textContent = 'Loading...';
            statusDiv.className = 'loading';
            
            try {
                const response = await fetch('/load-file', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ url: url })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    fileContentPre.textContent = data.content;
                    statusDiv.textContent = 'File loaded successfully!';
                    statusDiv.className = 'success';
                } else {
                    statusDiv.textContent = data.error || 'Error loading file';
                    statusDiv.className = 'error';
                    fileContentPre.textContent = '';
                }
            } catch (error) {
                statusDiv.textContent = 'Error: ' + error.message;
                statusDiv.className = 'error';
                fileContentPre.textContent = '';
            }
        });
        
        // Allow Enter key to trigger load
        driveUrlInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                loadBtn.click();
            }
        });
    }
});
