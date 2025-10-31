class ThrowableObjects extends MovableObject {
    constructor(x, y) {
        super().loadImage('img/6_salsa_bottle/bottle_rotation/1_bottle_rotation.png');
        this.x = x;
        this.y = y;
        this.height = 60;
        this.width = 70;
        this.hasHit = false;
        this.intervals = []; // Массив для хранения интервалов
        this.startThrow();
    }
    
    startThrow() {
        // Задаём отрицательное значение, чтобы бутылка сразу полетела вниз
        this.speedY = -20;
        this.applyGravity();
        const movementInterval = setInterval(() => {
            if (!this.hasHit) {
                this.x += 5;
            }
        }, 20);
        this.intervals.push(movementInterval);
    }

    /**
     * Очищает все интервалы бутылки
     */
    cleanup() {
        this.intervals.forEach(interval => clearInterval(interval));
        this.intervals = [];
    }
    
    // (Метод checkCollisionWith можно оставить для альтернативной проверки столкновений)
    checkCollisionWith(enemy) {
        if (this.hasHit) return false;
        return this.x < enemy.x + enemy.width &&
               this.x + this.width > enemy.x &&
               this.y < enemy.y + enemy.height &&
               this.y + this.height > enemy.y;
    }
}
