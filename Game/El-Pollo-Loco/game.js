let canvas;
let world;
let keyboard = new Keyboard();

function init() {
    // Получаем элемент canvas и создаём мир
    canvas = document.getElementById('canvas');
    world = new World(canvas, keyboard);
    let ctx = canvas.getContext('2d');

    // Пример отрисовки изображения (необязательно)
    let characterImage = new Image();
    characterImage.src = 'img/2_character_pepe/2_walk/W-24.png';
    characterImage.onload = function() {
        ctx.drawImage(characterImage, 20, 20, 50, 100);
    };

    console.log('My Character is', world.character);

    // Регулятор громкости
    const volumeSlider = document.getElementById('volumeSlider');
    if (volumeSlider) {
        volumeSlider.addEventListener('input', (e) => {
            let vol = parseFloat(e.target.value);
            setVolume(vol);
            localStorage.setItem('gameVolume', vol);
        });

        let savedVol = localStorage.getItem('gameVolume');
        if (savedVol !== null) {
            volumeSlider.value = savedVol;
            setVolume(parseFloat(savedVol));
        }
    }
}

/**
 * Функция для установки громкости у фоновой музыки и других аудиообъектов.
 */
function setVolume(vol) {
    if (world && world.backgroundMusic) {
        world.backgroundMusic.volume = vol;
    }
    if (world && world.character && world.character.walking_sound) {
        world.character.walking_sound.volume = vol;
    }
    // Добавьте другие звуки, если нужно
}


function endGame() {
    if (!world || !world.character) return;
    let playerName = prompt("Введите ваше имя для таблицы лидеров:");
    let score = world.character.collectedCoins || 0;
    // Сохраняем результат (предполагается наличие scoreManager.js с функцией saveScore)
    saveScore(playerName, score);
    // Обновляем таблицу лидеров (функция showLeaderboard должна быть определена)
    showLeaderboard();
}

/**
 * Отображает таблицу лидеров (Top 20) в элементе #leaderboardList.
 */
function showLeaderboard() {
    // Предполагается наличие функции getLeaderboard() в scoreManager.js
    let leaderboard = getLeaderboard();
    let listElement = document.getElementById('leaderboardList');
    if (!listElement) return;

    listElement.innerHTML = "";
    leaderboard.forEach((entry, index) => {
        const li = document.createElement('li');
        li.textContent = `${index + 1}. ${entry.name} — ${entry.score} очков`;
        listElement.appendChild(li);
    });
}

// Обработчики клавиатуры
window.addEventListener("keydown", (e) => {
    if (e.keyCode == 39) {
        keyboard.RIGHT = true;
    }
    if (e.keyCode == 37) {
        keyboard.LEFT = true;
    }
    if (e.keyCode == 38) {
        keyboard.UP = true;
    }
    if (e.keyCode == 40) {
        keyboard.DOWN = true;
    }
    if (e.keyCode == 32) {
        keyboard.SPACE = true;
    }
    if (e.keyCode == 68) {
        keyboard.D = true;
    }
});

window.addEventListener("keyup", (e) => {
    if (e.keyCode == 39) {
        keyboard.RIGHT = false;
    }
    if (e.keyCode == 37) {
        keyboard.LEFT = false;
    }
    if (e.keyCode == 38) {
        keyboard.UP = false;
    }
    if (e.keyCode == 40) {
        keyboard.DOWN = false;
    }
    if (e.keyCode == 32) {
        keyboard.SPACE = false;
    }
    if (e.keyCode == 68) {
        keyboard.D = false;
    }
});
