let canvas;
let world;
let keyboard = new Keyboard();

function init() {
    try {
        // Получаем элемент canvas и создаём мир
        canvas = document.getElementById('canvas');
        if (!canvas) {
            throw new Error('Canvas element not found');
        }
        
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
    } catch (error) {
        console.error('Error initializing game:', error);
        alert('Ошибка инициализации игры. Проверьте консоль для подробностей.');
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
    try {
        if (!world || !world.character) return;
        
        let playerName = prompt("Введите ваше имя для таблицы лидеров:");
        if (!playerName || playerName.trim() === '') {
            playerName = 'Anonymous';
        }
        
        let score = world.character.collectedCoins || 0;
        
        // Сохраняем результат (предполагается наличие scoreManager.js с функцией saveScore)
        if (typeof saveScore === 'function') {
            saveScore(playerName.trim(), score);
        }
        
        // Обновляем таблицу лидеров (функция showLeaderboard должна быть определена)
        if (typeof showLeaderboard === 'function') {
            showLeaderboard();
        }
        
        // Очищаем интервалы персонажа
        if (world.character && typeof world.character.cleanup === 'function') {
            world.character.cleanup();
        }
    } catch (error) {
        console.error('Error in endGame:', error);
    }
}

/**
 * Отображает таблицу лидеров (Top 20) в элементе #leaderboardList.
 */
function showLeaderboard() {
    try {
        // Предполагается наличие функции getLeaderboard() в scoreManager.js
        if (typeof getLeaderboard !== 'function') {
            console.warn('getLeaderboard function not found');
            return;
        }
        
        let leaderboard = getLeaderboard();
        let listElement = document.getElementById('leaderboardList');
        if (!listElement) {
            console.warn('leaderboardList element not found');
            return;
        }

        listElement.innerHTML = "";
        leaderboard.forEach((entry, index) => {
            const li = document.createElement('li');
            li.textContent = `${index + 1}. ${entry.name} — ${entry.score} очков`;
            listElement.appendChild(li);
        });
    } catch (error) {
        console.error('Error in showLeaderboard:', error);
    }
}

// Обработчики клавиатуры с поддержкой современных браузеров
window.addEventListener("keydown", (e) => {
    // Предотвращаем повторное срабатывание при зажатой клавише
    if (e.repeat) return;
    
    switch(e.keyCode || e.which) {
        case 39: // Arrow Right
            keyboard.RIGHT = true;
            break;
        case 37: // Arrow Left
            keyboard.LEFT = true;
            break;
        case 38: // Arrow Up
        case 87: // W key
            keyboard.UP = true;
            break;
        case 40: // Arrow Down
        case 83: // S key
            keyboard.DOWN = true;
            break;
        case 32: // Space
            keyboard.SPACE = true;
            e.preventDefault(); // Предотвращаем прокрутку страницы
            break;
        case 68: // D key (для броска)
            keyboard.D = true;
            break;
        case 65: // A key (для движения влево)
            keyboard.LEFT = true;
            break;
    }
});

window.addEventListener("keyup", (e) => {
    switch(e.keyCode || e.which) {
        case 39: // Arrow Right
            keyboard.RIGHT = false;
            break;
        case 37: // Arrow Left
            keyboard.LEFT = false;
            break;
        case 38: // Arrow Up
        case 87: // W key
            keyboard.UP = false;
            break;
        case 40: // Arrow Down
        case 83: // S key
            keyboard.DOWN = false;
            break;
        case 32: // Space
            keyboard.SPACE = false;
            break;
        case 68: // D key (для броска)
            keyboard.D = false;
            break;
        case 65: // A key (для движения влево)
            keyboard.LEFT = false;
            break;
    }
});
