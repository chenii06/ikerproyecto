const form = document.getElementById('submit-form');

// Validación del formulario al enviarlo
form.addEventListener('submit', (event) => {
    const playerName = document.getElementById('player-name').value.trim();
    const level = document.getElementById('level').value;
    const completionTime = document.getElementById('completion-time').value.trim();
    const videoLink = document.getElementById('video-link').value.trim();
    const rawFootageLink = document.getElementById('raw-footage-link').value.trim();
    const notes = document.getElementById('notes').value.trim();

    const timePattern = /^\d{2}:\\d{2}:\\d{2}\.\\d{3}$/;

    // Validación de campos
    if (!playerName || !level || !timePattern.test(completionTime) || !isValidUrl(videoLink) || !isValidUrl(rawFootageLink)) {
        event.preventDefault();
        alert('Please fill out all required fields correctly!');
        return;
    }

    alert('Record submitted successfully!');
});

function isValidUrl(url) {
    const urlPattern = /^(https?:\/\/)?([\w\-]+\.)+[\w\-]+(\/[\w\-._~:/?#[\]@!$&'()*+,;=%]*)?$/;
    return urlPattern.test(url);
}
