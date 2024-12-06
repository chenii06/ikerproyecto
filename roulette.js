// Level data
const levels = [
    { id: 1, name: "Convolution", creator: "KEaliTgeo", rating: 1, image: "imagenes/convolution.jpg" },
    { id: 2, name: "Null", creator: "RealMatter", rating: 4, image: "imagenes/null.jpg" },
    { id: 3, name: "Im Happy for You", creator: "No ob", rating: 3, image: "imagenes/imhappy4u.jpg" },
    { id: 4, name: "Project BUZZKILL", creator: "Superkobster", rating: 4, image: "imagenes/proyectbuzzkill.jpg" },
    { id: 5, name: "Crerro Kaizo II", creator: "Crerro", rating: 5, image: "imagenes/crerrokaizoii.jpg" },
    { id: 6, name: "Intervallum", creator: "KEaliTgeo", rating: 3, image: "imagenes/intervallum.jpg" },
    { id: 7, name: "Void World", creator: "zYuko", rating: 5, image: "imagenes/voidworld.jpg" },
    { id: 8, name: "Crerro Kaizo I", creator: "Crerro", rating: 2, image: "imagenes/crerrokaizoi.jpg" },
    { id: 9, name: "the guards mission", creator: "2ItalianCats", rating: 1, image: "imagenes/theguardsmission.jpg" },
    { id: 10, name: "Free Solo", creator: "MeowMasterer", rating: 5, image: "imagenes/freesolo.jpg" },
    { id: 11, name: "Whg3 Lv5", creator: "FakeHATETAG", rating: 2, image: "imagenes/wh3lv5.jpg" },
    { id: 12, name: "Nuclear Alarm", creator: "GabestGD", rating: 4, image: "imagenes/nuclearalarm.jpg" },
    { id: 13, name: "Jetpack Trials", creator: "Eefy77", rating: 1, image: "imagenes/jetpacktrials.jpg" },
    { id: 14, name: "CASIO HELLBURST", creator: "MVXgameS", rating: 1, image: "imagenes/casio.jpg" },
    { id: 15, name: "The Abyss", creator: "zYuko", rating: 5, image: "imagenes/theabyss.jpg" }
];

// DOM Elements
const wheel = document.querySelector('.wheel-inner');
const spinButton = document.getElementById('spinButton');
const levelCard = document.querySelector('.level-card');
const levelImage = document.querySelector('.level-image');
const levelName = document.querySelector('.level-name');
const levelCreator = document.querySelector('.level-creator');
const levelRating = document.querySelector('.level-rating');
const playButton = document.querySelector('.play-button');

// Create wheel segments
function createWheel() {
    const segmentAngle = 360 / levels.length;
    levels.forEach((level, index) => {
        const segment = document.createElement('div');
        segment.className = 'wheel-segment';
        segment.style.transform = `rotate(${segmentAngle * index}deg)`;
        
        const img = document.createElement('img');
        img.src = level.image;
        img.alt = level.name;
        
        segment.appendChild(img);
        wheel.appendChild(segment);
    });
}

// Spin the wheel
function spin() {
    spinButton.disabled = true;
    levelCard.classList.add('hidden');
    
    // Random rotation between 5 and 10 full spins plus random segment
    const spins = 5 + Math.random() * 5;
    const randomAngle = Math.random() * 360;
    const totalRotation = spins * 360 + randomAngle;
    
    wheel.style.transform = `rotate(${totalRotation}deg)`;
    
    // Calculate selected level
    setTimeout(() => {
        const finalAngle = totalRotation % 360;
        const segmentAngle = 360 / levels.length;
        const selectedIndex = Math.floor((360 - (finalAngle % 360)) / segmentAngle);
        const selectedLevel = levels[selectedIndex];
        
        displaySelectedLevel(selectedLevel);
    }, 4000);
}

// Display selected level
function displaySelectedLevel(level) {
    levelImage.src = level.image;
    levelName.textContent = `#${level.id} - ${level.name}`;
    levelCreator.textContent = `Creator: ${level.creator}`;
    levelRating.textContent = '⭐'.repeat(level.rating);
    playButton.href = `level${level.id}.html`;
    
    levelCard.classList.remove('hidden');
    spinButton.disabled = false;
}

// Event listeners
spinButton.addEventListener('click', spin);

// Initialize wheel
createWheel();