class DrawableObject {
    img;
    imageCache = {};
    currentImage = 0;
    x = 120;
    y = 280;
    height = 150;
    width = 100;

    /**
     * Загружает изображение по указанному пути.
     * Добавлены обработчики onload и onerror для отслеживания состояния загрузки.
     */
    loadImage(path) {
        this.img = new Image();
        // Обработчик успешной загрузки изображения
        this.img.onload = () => {
            console.log("Изображение загружено: " + path);
        };
        // Обработчик ошибки загрузки
        this.img.onerror = () => {
            console.error("Ошибка загрузки изображения: " + path);
        };
        this.img.src = path;
    }

    /**
     * Отрисовывает изображение на канвасе, если оно успешно загружено.
     * Если изображение не загружено или находится в "broken" состоянии, отрисовка не выполняется.
     */
    draw(ctx) {
        // Проверяем, загружено ли изображение и не находится ли оно в состоянии ошибки
        if (!this.img || !this.img.complete || this.img.naturalWidth === 0) {
            // Изображение не готово или сломано — пропускаем отрисовку
            return;
        }
        ctx.drawImage(this.img, this.x, this.y, this.width, this.height);
    }

    /**
     * Отрисовывает рамку (hitbox) для отладки, если объект является Character или Chicken.
     */
    drawFrame(ctx) {
        if (this instanceof Character || this instanceof Chicken) {
            ctx.beginPath();
            ctx.lineWidth = '5';
            ctx.strokeStyle = 'blue';
            ctx.rect(this.x, this.y, this.width, this.height);
            ctx.stroke();
        }
    }

    /**
     * Загружает набор изображений по массиву путей.
     * Для каждого изображения сохраняется объект Image в кэше.
     */
    loadImages(arr) {
        arr.forEach((path) => {
            let img = new Image();
            // Обработчик успешной загрузки
            img.onload = () => {
                console.log("Изображение загружено: " + path);
            };
            // Обработчик ошибки загрузки
            img.onerror = () => {
                console.error("Ошибка загрузки изображения: " + path);
            };
            img.src = path;
            this.imageCache[path] = img;
        });
    }
}
