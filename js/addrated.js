document.addEventListener('DOMContentLoaded', function() {
    const addLevelForm = document.getElementById('addLevelForm');
    const submitBtn = document.querySelector('.submit-btn');
    const title = document.querySelector('.add-level-title');
    title.setAttribute('data-text', title.textContent);

    // Interactive background
    document.body.addEventListener('mousemove', (e) => {
        const mouseX = e.clientX / window.innerWidth;
        const mouseY = e.clientY / window.innerHeight;
        document.documentElement.style.setProperty('--mouse-x', mouseX);
        document.documentElement.style.setProperty('--mouse-y', mouseY);
    });

    addLevelForm.addEventListener('submit', function(e) {
        e.preventDefault();

        if (!validateForm()) {
            showNotification('Please fill all fields correctly', 'error');
            return;
        }

        // Show loading spinner
        const spinner = document.createElement('div');
        spinner.className = 'loading-spinner';
        addLevelForm.appendChild(spinner);

        // Disable the submit button and show loading state
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding...';

        const newLevel = {
            id: Date.now().toString(),
            name: document.getElementById('levelName').value,
            creator: document.getElementById('creator').value,
            rating: parseInt(document.getElementById('rating').value),
            image: document.getElementById('imageUrl').value
        };

        document.getElementById('image').addEventListener('change', function(e) {
            var fileName = e.target.value.split('\\').pop();
            if (fileName) {
                e.target.nextElementSibling.querySelector('.file-name').textContent = fileName;
            }
        });

        // Simulate an API call with setTimeout
        setTimeout(() => {
            let levels = JSON.parse(localStorage.getItem('levels')) || [];
            levels.push(newLevel);
            localStorage.setItem('levels', JSON.stringify(levels));

            // Remove loading spinner
            spinner.remove();

            // Show success message
            showNotification('Level added successfully!', 'success');

            // Reset form and button state
            addLevelForm.reset();
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Add Level';

            // Redirect after a short delay
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 2000);
        }, 1500);
    });

    // Form validation
    function validateForm() {
        const inputs = addLevelForm.querySelectorAll('input');
        let isValid = true;
        inputs.forEach(input => {
            if (!input.checkValidity()) {
                isValid = false;
                input.classList.add('invalid');
            } else {
                input.classList.remove('invalid');
            }
        });
        return isValid;
    }

    // Interactive form elements
    const formGroups = document.querySelectorAll('.form-group');
    formGroups.forEach(group => {
        const input = group.querySelector('input');
        const label = group.querySelector('label');

        input.addEventListener('focus', () => {
            label.style.transform = 'translateY(-20px) translateZ(30px)';
        });

        input.addEventListener('blur', () => {
            if (!input.value) {
                label.style.transform = 'translateY(0) translateZ(20px)';
            }
        });
    });

    // Notification function
    function showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.classList.add('show');
            setTimeout(() => {
                notification.classList.remove('show');
                setTimeout(() => {
                    notification.remove();
                }, 300);
            }, 3000);
        }, 100);
    }
});

// Enhanced particle animation
const canvas = document.getElementById('particleCanvas');
const ctx = canvas.getContext('2d');

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

window.addEventListener('resize', () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
});

const particles = [];
const particleCount = 150;

class Particle {
    constructor() {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.size = Math.random() * 5 + 1;
        this.speedX = Math.random() * 3 - 1.5;
        this.speedY = Math.random() * 3 - 1.5;
        this.color = `hsl(${Math.random() * 60 + 180}, 100%, 50%)`;
    }

    update() {
        this.x += this.speedX;
        this.y += this.speedY;

        if (this.size > 0.2) this.size -= 0.1;

        if (this.x > canvas.width) this.x = 0;
        if (this.x < 0) this.x = canvas.width;
        if (this.y > canvas.height) this.y = 0;
        if (this.y < 0) this.y = canvas.height;
    }

    draw() {
        ctx.fillStyle = this.color;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
    }
}

for (let i = 0; i < particleCount; i++) {
    particles.push(new Particle());
}

function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    particles.forEach(particle => {
        particle.update();
        particle.draw();
    });

    particles.forEach((a, i) => {
        particles.slice(i + 1).forEach(b => {
            const dx = a.x - b.x;
            const dy = a.y - b.y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            if (distance < 100) {
                const opacity = (1 - distance / 100) * 0.5;
                ctx.strokeStyle = `hsla(${Math.random() * 60 + 180}, 100%, 50%, ${opacity})`;
                ctx.lineWidth = 0.5;
                ctx.beginPath();
                ctx.moveTo(a.x, a.y);
                ctx.lineTo(b.x, b.y);
                ctx.stroke();
            }
        });
    });

    requestAnimationFrame(animate);
}

animate();

// Create star field
const starsContainer = document.querySelector('.stars');
for (let i = 0; i < 200; i++) {
    const star = document.createElement('div');
    star.classList.add('star');
    star.style.width = `${Math.random() * 2}px`;
    star.style.height = star.style.width;
    star.style.left = `${Math.random() * 100}%`;
    star.style.top = `${Math.random() * 100}%`;
    star.style.setProperty('--duration', `${Math.random() * 3 + 2}s`);
    starsContainer.appendChild(star);
}

// Interactive cosmic background
const cosmicBackground = document.querySelector('.cosmic-background');
document.addEventListener('mousemove', (e) => {
    const mouseX = e.clientX / window.innerWidth;
    const mouseY = e.clientY / window.innerHeight;
    
    cosmicBackground.style.background = `
        radial-gradient(circle at ${mouseX * 100}% ${mouseY * 100}%, rgba(0, 170, 255, 0.3) 0%, transparent 50%),
        radial-gradient(circle at ${(1 - mouseX) * 100}% ${(1 - mouseY) * 100}%, rgba(255, 51, 102, 0.3) 0%, transparent 50%),
        radial-gradient(circle at 50% 50%, rgba(119, 0, 255, 0.1) 0%, transparent 50%)
    `;
});

