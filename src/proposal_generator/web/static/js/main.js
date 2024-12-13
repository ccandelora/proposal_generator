import progressTracker from './progress.js';

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('proposal-form');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Start progress tracking
        progressTracker.startTracking();
        
        try {
            // Get form data
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            
            // Send request
            const response = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                throw new Error('Failed to generate proposal');
            }
            
            const result = await response.json();
            
            // Handle success
            if (result.success) {
                // Display the generated proposal
                displayProposal(result.data);
            } else {
                throw new Error(result.error || 'Unknown error');
            }
            
        } catch (error) {
            console.error('Error:', error);
            progressTracker.showError(error.message);
        } finally {
            progressTracker.stopTracking();
        }
    });
});

function displayProposal(data) {
    const proposalDiv = document.getElementById('proposal-content');
    if (proposalDiv && data.content) {
        // Convert markdown to HTML
        const converter = new showdown.Converter();
        const html = converter.makeHtml(data.content);
        proposalDiv.innerHTML = html;
    }
} 