class World {
    character = new Character();
    level = level1;
    canvas;
    ctx;
    keyboard;
    camera_x = 0;
    statusBar;
    throwableObjects = [];
    backgroundMusic;
    musicInterval;
    coinStatusBar;
    coins = [];
    gameEnded = false; // Флаг, сигнализирующий о завершении игры
    intervals = []; // Массив для хранения всех интервалов

    constructor(canvas, keyboard) {
        this.canThrow = true; // Флаг для управления частотой бросков
        this.ctx = canvas.getContext('2d');
        this.canvas = canvas;
        this.keyboard = keyboard;
        // Задаём гравитацию для мира
        this.gravity = 2.5;

        // Настройка фоновой музыки (не запускаем автоматически)
        this.backgroundMusic = new Audio('./audio/mexikan.mp3');
        this.backgroundMusic.loop = true;
        this.backgroundMusic.volume = 0.1;

        // Инициализируем панели с передачей canvas
        this.statusBar = new StatusBar(canvas);
        this.coinStatusBar = new CoinStatusBar(canvas);

        // Запускаем основной цикл отрисовки
        this.draw();
        // Устанавливаем ссылки в персонажа и врагов
        this.setWorld();
        // Запускаем проверку коллизий и бросков
        this.run();
    }

    setWorld() {
        this.character.world = this;
        this.level.enemies.forEach((enemy) => {
            enemy.world = this;
        });
    }

    run() {
        const interval = setInterval(() => {
            if (!this.gameEnded) {
                this.checkCollisions();
                this.checkThrowObjects();
            }
        }, 200);
        this.intervals.push(interval);
    }

    /**
     * Проверяет, нажата ли клавиша для броска бутылок, и создает новый объект бутылки.
     * Бросок происходит только один раз за 500 мс (canThrow).
     */
    checkThrowObjects() {
        if (this.keyboard.D && this.canThrow) {
            let bottle = new ThrowableObjects(
                this.character.x + 50,
                this.character.y + 50
            );
            bottle.hasHit = false;
            this.throwableObjects.push(bottle);
            this.canThrow = false;
            setTimeout(() => {
                this.canThrow = true;
            }, 500);
        }
    }

    /**
     * Проверяет столкновения:
     * 1. Персонажа с врагами.
     * 2. Персонажа с монетами.
     * 3. Бутылок с врагами.
     */
    checkCollisions() {
        // 1. Столкновения персонажа с врагами
        this.level.enemies.forEach((enemy) => {
            if (this.character.isColliding(enemy) && !enemy.isDead) {
                this.character.hit();
                this.statusBar.setPercentage(this.character.energy);
                // Если энергия <= 0, персонаж проиграл
                if (this.character.energy <= 0 && !this.gameEnded) {
                    this.gameEnded = true;
                    this.showGameOverScreen();
                    // Вызываем endGame() для сохранения результата и обновления лидеров
                    endGame();
                }
            }
        });

        // 2. Столкновения персонажа с монетами
        for (let i = this.level.coins.length - 1; i >= 0; i--) {
            if (this.character.isColliding(this.level.coins[i])) {
                this.level.coins.splice(i, 1);
                this.character.collectCoin();
            }
        }
        
        // 3. Столкновения бутылок с врагами
        this.throwableObjects.forEach((bottle) => {
            this.level.enemies.forEach((enemy) => {
                if (!bottle.hasHit && bottle.isColliding(enemy) && !enemy.isDead) {
                    // Если это босс
                    if (enemy instanceof Endboss) {
                        enemy.takeDamage(15);
                        if (enemy.health === 0 && !this.gameEnded) {
                            this.gameEnded = true;
                            this.showVictoryScreen();
                            endGame(); // Сохраняем результат, например, score = this.character.collectedCoins
                        }
                    } else {
                        enemy.takeDamage(15);
                    }
                    bottle.hasHit = true;
                }
            });
        });

        // Удаляем бутылки, которые уже нанесли урон
        this.throwableObjects = this.throwableObjects.filter(bottle => !bottle.hasHit);
    }

    /**
     * Обновляет позицию камеры так, чтобы персонаж всегда оставался в центре экрана,
     * и чтобы камера не выходила за границы уровня.
     */
    updateCameraPosition() {
        // Центрируем камеру на персонаже
        let targetOffset = -this.character.x + (this.canvas.width / 2) - (this.character.width / 2);
        
        // Ограничение слева - камера не должна уходить за начало уровня
        if (targetOffset > 0) {
            targetOffset = 0;
        }
        
        // Ограничение справа - камера не должна уходить за конец уровня
        let maxOffset = -this.level.level_end_x + this.canvas.width;
        if (targetOffset < maxOffset) {
            targetOffset = maxOffset;
        }
        
        this.camera_x = targetOffset;
    }

    draw() {
        this.updateCameraPosition();
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Смещаем камеру
        this.ctx.translate(this.camera_x, 0);

        // 1. Рисуем фоновые объекты
        this.addObjectsToMap(this.level.backgroundObjects);

        // 2. Возвращаем камеру для статических элементов
        this.ctx.translate(-this.camera_x, 0);
        this.addToMap(this.statusBar);
        this.addToMap(this.coinStatusBar);
        
        // Отрисовываем полосу здоровья босса в статической области
        this.level.enemies.forEach((enemy) => {
            if (enemy instanceof Endboss && !enemy.isDead) {
                this.drawBossHealthBar(enemy);
            }
        });

        // 3. Снова смещаем камеру для динамических объектов
        this.ctx.translate(this.camera_x, 0);
        this.addObjectsToMap(this.level.coins);
        this.addToMap(this.character);

        // 4. Рисуем врагов
        this.level.enemies.forEach((enemy) => {
            this.addToMap(enemy);
        });

        // 5. Рисуем облака и бросаемые объекты
        this.addObjectsToMap(this.level.clouds);
        this.addObjectsToMap(this.throwableObjects);

        // Возвращаем камеру
        this.ctx.translate(-this.camera_x, 0);

        requestAnimationFrame(() => this.draw());
    }

    addObjectsToMap(objects) {
        objects.forEach((obj) => this.addToMap(obj));
    }

    addToMap(mo) {
        if (mo.otherDirection) {
            this.ctx.save();
            this.ctx.translate(mo.x + mo.width, mo.y);
            this.ctx.scale(-1, 1);
            mo.draw(this.ctx);
            mo.drawFrame(this.ctx);
            this.ctx.restore();
        } else {
            mo.draw(this.ctx);
            mo.drawFrame(this.ctx);
        }
    }

    showVictoryScreen() {
        document.getElementById('victoryScreen').style.display = 'flex';
        this.gameEnded = true;
    }

    showGameOverScreen() {
        document.getElementById('gameOverScreen').style.display = 'flex';
        this.gameEnded = true;
        this.cleanup();
    }

    showVictoryScreen() {
        document.getElementById('victoryScreen').style.display = 'flex';
        this.gameEnded = true;
        this.cleanup();
    }

    /**
     * Отрисовывает полосу здоровья босса в статической области экрана
     */
    drawBossHealthBar(boss) {
        // Проверяем, виден ли босс на экране
        if (boss.x + boss.width > -this.camera_x && boss.x < -this.camera_x + this.canvas.width) {
            // Вычисляем позицию полосы здоровья относительно экрана
            let screenX = boss.x + this.camera_x;
            let screenY = boss.y - 50; // Поднимаем полосу выше босса
            
            // Ограничиваем позицию, чтобы полоса не выходила за границы экрана
            screenX = Math.max(10, Math.min(screenX, this.canvas.width - 210));
            screenY = Math.max(10, screenY);
            
            // Отрисовываем полосу здоровья
            const statusImage = new Image();
            statusImage.src = boss.IMAGES_STATUS[boss.statusBarIndex];
            this.ctx.drawImage(statusImage, screenX, screenY, 200, 60);
        }
    }

    /**
     * Очищает все интервалы и останавливает анимацию
     */
    cleanup() {
        this.intervals.forEach(interval => clearInterval(interval));
        this.intervals = [];
        
        // Останавливаем фоновую музыку
        if (this.backgroundMusic) {
            this.backgroundMusic.pause();
            this.backgroundMusic.currentTime = 0;
        }
        
        // Очищаем массив бутылок
        this.throwableObjects = [];
    }
}
