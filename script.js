// Level data
let levels = [
    {
        id: 'convolution',
        name: 'Convolution',
        creator: 'KEaliTgeo',
        rating: 1,
        image: 'imagenes/convolution.jpg'
    },
    {
        id: 'null',
        name: 'Null',
        creator: 'RealMatter',
        rating: 4,
        image: 'imagenes/null.jpg'
    },
    {
        id: 'imhappy4u',
        name: 'Im Happy 4 You',
        creator: 'No ob',
        rating: 3,
        image: 'imagenes/imhappy4u.jpg'
    },
    {
        id: 'projectbuzzkill',
        name: 'Project BUZZKILL',
        creator: 'Superkobster',
        rating: 4,
        image: 'imagenes/proyectbuzzkill.jpg'
    },
    {
        id: 'crerrokaizoii',
        name: 'Crerro Kaizo II',
        creator: 'Crerro',
        rating: 5,
        image: 'imagenes/crerrokaizoii.jpg'
    },
    {
        id: 'intervallum',
        name: 'Intervallum',
        creator: 'KEaliTgeo',
        rating: 3,
        image: 'imagenes/intervallum.jpg'
    },
    {
        id: 'voidworld',
        name: 'Void World',
        creator: 'zYuko',
        rating: 5,
        image: 'imagenes/voidworld.jpg'
    },
    {
        id: 'crerrokaizoi',
        name: 'Crerro Kaizo I',
        creator: 'Crerro',
        rating: 2,
        image: 'imagenes/crerrokaizoi.jpg'
    },
    {
        id: 'theguardsmission',
        name: 'the guards mission',
        creator: '2ItalianCats',
        rating: 1,
        image: 'imagenes/theguardsmission.jpg'
    },
    {
        id: 'freesolo',
        name: 'Free Solo',
        creator: 'MeowMasterer',
        rating: 5,
        image: 'imagenes/freesolo.jpg'
    },
    {
        id: 'whg3lv5',
        name: 'Whg3 Lv5',
        creator: 'FakeHATETAG',
        rating: 2,
        image: 'imagenes/wh3lv5.jpg'
    },
    {
        id: 'nuclearalarm',
        name: 'Nuclear Alarm',
        creator: 'GabestGD',
        rating: 4,
        image: 'imagenes/nuclearalarm.jpg'
    },
    {
        id: 'jetpacktrials',
        name: 'Jetpack Trials',
        creator: 'Eefy77',
        rating: 1,
        image: 'imagenes/jetpacktrials.jpg'
    },
    {
        id: 'casiohellburst',
        name: 'CASIO HELLBURST',
        creator: 'MVXgameS',
        rating: 1,
        image: 'imagenes/casio.jpg'
    },
    {
        id: 'theabyss',
        name: 'The Abyss',
        creator: 'zYuko',
        rating: 5,
        image: 'imagenes/theabyss.jpg'
    }
];

let isAdminMode = false;
let sortableInstance = null;

const adminButton = document.getElementById('adminButton');
const levelsContainer = document.getElementById('levelsContainer');

// Load saved level order and data from localStorage
function loadSavedLevelData() {
    const savedLevels = localStorage.getItem('levels');
    if (savedLevels) {
        levels = JSON.parse(savedLevels);
    }
}

// Save current level data to localStorage
function saveLevelData() {
    localStorage.setItem('levels', JSON.stringify(levels));
}

function createStarRating(rating) {
    return '⭐'.repeat(rating);
}

function createLevelHTML(level, index) {
    return `
        <div class="level ${isAdminMode ? 'draggable' : ''}" data-id="${level.id}">
            <div class="level-inner">
                <img src="${level.image}" alt="${level.name} Level">
                <div class="level-details">
                    <h4>#${index + 1} - ${level.name}</h4>
                    <p>Creator: ${level.creator}</p>
                    <p class="rating">${createStarRating(level.rating)}</p>
                </div>
                ${isAdminMode ? `
                    <div class="admin-controls">
                        <button class="delete-level" data-id="${level.id}">
                            <i class="fas fa-trash-alt"></i>
                        </button>
                    </div>
                ` : ''}
            </div>
        </div>
    `;
}

function createNewLevelForm() {
    return `
        <div class="new-level-form">
            <h3>Add New Level</h3>
            <form id="newLevelForm">
                <div class="form-group">
                    <label for="newLevelName">Level Name</label>
                    <input type="text" id="newLevelName" required>
                </div>
                <div class="form-group">
                    <label for="newLevelCreator">Creator Name</label>
                    <input type="text" id="newLevelCreator" required>
                </div>
                <div class="form-group">
                    <label for="newLevelRating">Rating (1-5)</label>
                    <input type="number" id="newLevelRating" min="1" max="5" required>
                </div>
                <div class="form-group">
                    <label for="newLevelImage">Image URL</label>
                    <input type="text" id="newLevelImage" required>
                </div>
                <button type="submit">Add Level</button>
            </form>
        </div>
    `;
}

function renderLevels() {
    let content = isAdminMode ? createNewLevelForm() : '';
    content += levels.map((level, index) => createLevelHTML(level, index)).join('');
    levelsContainer.innerHTML = content;
    
    if (!isAdminMode) {
        document.querySelectorAll('.level').forEach((level, index) => {
            level.addEventListener('click', () => {
                const levelId = level.dataset.id;
                const levelIndex = levels.findIndex(l => l.id === levelId);
                window.location.href = `level${levelIndex + 1}.html`;
            });
        });
    } else {
        document.getElementById('newLevelForm').addEventListener('submit', addNewLevel);
        document.querySelectorAll('.delete-level').forEach(button => {
            button.addEventListener('click', deleteLevel);
        });
    }
}

function initializeSortable() {
    if (sortableInstance) {
        sortableInstance.destroy();
    }
    
    if (isAdminMode) {
        sortableInstance = new Sortable(levelsContainer, {
            animation: 150,
            ghostClass: 'dragging',
            onEnd: function(evt) {
                const item = levels.splice(evt.oldIndex - 1, 1)[0]; // -1 to account for the new level form
                levels.splice(evt.newIndex - 1, 0, item);
                renderLevels();
                saveLevelData();
            }
        });
    }
}

function toggleAdminMode() {
    isAdminMode = !isAdminMode;
    adminButton.classList.toggle('active');
    adminButton.innerHTML = isAdminMode ? 
        '<i class="fas fa-shield"></i> Exit Admin' : 
        '<i class="fas fa-shield"></i> Admin Mode';
    
    renderLevels();
    initializeSortable();
}

function addNewLevel(event) {
    event.preventDefault();
    const newLevel = {
        id: Date.now().toString(), // Using timestamp as a simple unique ID
        name: document.getElementById('newLevelName').value,
        creator: document.getElementById('newLevelCreator').value,
        rating: parseInt(document.getElementById('newLevelRating').value),
        image: document.getElementById('newLevelImage').value
    };
    levels.unshift(newLevel);
    renderLevels();
    saveLevelData();
    initializeSortable();
}

function deleteLevel(event) {
    const levelId = event.currentTarget.dataset.id;
    levels = levels.filter(level => level.id !== levelId);
    renderLevels();
    saveLevelData();
    initializeSortable();
}

adminButton.addEventListener('click', toggleAdminMode);

// Initialize
loadSavedLevelData();
renderLevels();

// Particle animation
const canvas = document.getElementById('particleCanvas');
const ctx = canvas.getContext('2d');

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

window.addEventListener('resize', () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
});

const particles = [];
const particleCount = 100;

class Particle {
    constructor() {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.size = Math.random() * 3 + 1;
        this.speedX = Math.random() * 2 - 1;
        this.speedY = Math.random() * 2 - 1;
        this.color = `hsla(${195 + Math.random() * 30}, 100%, 70%, ${0.3 + Math.random() * 0.4})`;
    }

    update() {
        this.x += this.speedX;this.y += this.speedY;

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
                const opacity = (1 - distance / 100) * 0.3;
                ctx.strokeStyle = `rgba(0, 170, 255, ${opacity})`;
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

