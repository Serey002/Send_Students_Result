// Show clear data confirmation modal
function showClearDataModal() {
    document.getElementById('clearDataModal').classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

// Hide clear data confirmation modal
function hideClearDataModal() {
    document.getElementById('clearDataModal').classList.add('hidden');
    document.body.style.overflow = '';
}

// Clear all data by making a POST request to the clear-data endpoint
async function clearAllData() {
    try {
        const response = await fetch('/clear-data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (response.ok) {
            const data = await response.json();
            if (data.message) {
                // Create a flash message
                const flashMessage = document.createElement('div');
                flashMessage.className = 'alert alert-success rounded-md p-4 mb-4 border-l-4 border-green-500 bg-green-50';
                flashMessage.innerHTML = `
                    <div class="flex">
                        <div class="flex-shrink-0">
                            <i class="fas fa-check-circle text-green-500"></i>
                        </div>
                        <div class="ml-3">
                            <p class="text-sm text-green-700">${data.message}</p>
                        </div>
                    </div>
                `;
                
                // Insert the flash message at the top of the content
                const content = document.querySelector('main');
                if (content.firstChild) {
                    content.insertBefore(flashMessage, content.firstChild);
                } else {
                    content.appendChild(flashMessage);
                }

                // Remove the flash message after 5 seconds
                setTimeout(() => {
                    flashMessage.style.transition = 'opacity 0.5s';
                    flashMessage.style.opacity = '0';
                    setTimeout(() => flashMessage.remove(), 500);
                }, 5000);
            }
            
            // Refresh the dashboard to show updated data
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            const error = await response.json();
            throw new Error(error.error || 'Failed to clear data');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while clearing data. Please try again.');
    } finally {
        hideClearDataModal();
    }
}

// Close modal when clicking outside of it
window.onclick = function(event) {
    const modal = document.getElementById('clearDataModal');
    if (event.target === modal) {
        hideClearDataModal();
    }
}

// Close modal with Escape key
document.addEventListener('keydown', function(event) {
    const modal = document.getElementById('clearDataModal');
    if (event.key === 'Escape' && !modal.classList.contains('hidden')) {
        hideClearDataModal();
    }
});
