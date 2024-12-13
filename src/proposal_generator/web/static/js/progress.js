class ProgressTracker {
    constructor() {
        this.progressBar = document.getElementById('progress-bar');
        this.statusText = document.getElementById('status-text');
        this.stageText = document.getElementById('current-stage');
        this.errorDiv = document.getElementById('error-message');
        this.completedList = document.getElementById('completed-steps');
        this.pollInterval = null;
    }

    startTracking() {
        this.pollInterval = setInterval(() => this.updateProgress(), 1000);
    }

    stopTracking() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }
    }

    async updateProgress() {
        try {
            const response = await fetch('/api/progress');
            if (!response.ok) {
                throw new Error('Failed to fetch progress');
            }
            
            const data = await response.json();
            this.updateUI(data);
            
            // Stop polling if complete or error
            if (data.error || data.progress === 100) {
                this.stopTracking();
            }
        } catch (error) {
            console.error('Error updating progress:', error);
            this.showError(error.message);
        }
    }

    updateUI(data) {
        // Update progress bar
        if (this.progressBar && typeof data.progress === 'number') {
            this.progressBar.style.width = `${data.progress}%`;
            this.progressBar.setAttribute('aria-valuenow', data.progress);
        }

        // Update status text
        if (this.statusText && data.status) {
            this.statusText.textContent = data.status;
        }

        // Update stage
        if (this.stageText && data.current_stage) {
            this.stageText.textContent = data.current_stage;
        }

        // Update completed steps
        if (this.completedList && Array.isArray(data.completed_steps)) {
            this.completedList.innerHTML = data.completed_steps
                .map(step => `<li class="completed">${step}</li>`)
                .join('');
        }

        // Handle errors
        if (data.error) {
            this.showError(data.error);
        } else {
            this.hideError();
        }
    }

    showError(message) {
        if (this.errorDiv) {
            this.errorDiv.textContent = message;
            this.errorDiv.style.display = 'block';
        }
    }

    hideError() {
        if (this.errorDiv) {
            this.errorDiv.style.display = 'none';
        }
    }
}

// Initialize and export progress tracker
const progressTracker = new ProgressTracker();
export default progressTracker; 