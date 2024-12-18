document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const starfield = document.getElementById('starfield');
    
    starfield.appendChild(canvas);
    
    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    
    let time = 0;
    const colors = [
        { r: 10, g: 10, b: 40 },  // Deep blue
        { r: 40, g: 10, b: 60 },  // Purple
        { r: 20, g: 10, b: 50 }   // Indigo
    ];
    
    function lerp(start, end, t) {
        return start * (1 - t) + end * t;
    }
    
    function animate() {
        time += 0.001;
        
        // Create gradient background
        const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
        
        colors.forEach((color, i) => {
            const offset = (time + i / colors.length) % 1;
            const r = Math.floor(lerp(color.r, colors[(i + 1) % colors.length].r, offset));
            const g = Math.floor(lerp(color.g, colors[(i + 1) % colors.length].g, offset));
            const b = Math.floor(lerp(color.b, colors[(i + 1) % colors.length].b, offset));
            gradient.addColorStop(offset, `rgb(${r}, ${g}, ${b})`);
        });
        
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Add subtle wave effect
        const waveCount = 3;
        for (let i = 0; i < waveCount; i++) {
            ctx.beginPath();
            ctx.strokeStyle = `rgba(255, 255, 255, ${0.03 - (i * 0.01)})`;
            ctx.lineWidth = 2;
            
            for (let x = 0; x < canvas.width; x++) {
                const frequency = 0.001 + (i * 0.0005);
                const amplitude = 50 - (i * 10);
                const y = Math.sin((x * frequency) + (time * 2)) * amplitude;
                
                if (x === 0) {
                    ctx.moveTo(x, canvas.height / 2 + y);
                } else {
                    ctx.lineTo(x, canvas.height / 2 + y);
                }
            }
            ctx.stroke();
        }
        
        requestAnimationFrame(animate);
    }
    
    animate();

    // Achievement hover effects
    const achievements = document.querySelectorAll('.achievement');
    
    achievements.forEach(achievement => {
        achievement.addEventListener('mousemove', (e) => {
            const rect = achievement.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            achievement.style.setProperty('--mouse-x', `${x}px`);
            achievement.style.setProperty('--mouse-y', `${y}px`);
        });
    });
});