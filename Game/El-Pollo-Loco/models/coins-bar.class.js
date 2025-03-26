class CoinStatusBar extends DrawableObject {
    // Массив путей к изображениям статус-бара для монет (должен содержать изображения для 0%, 20%, 40%, 60% или 80%/100%)
    IMAGES = [
        'img/7_statusbars/1_statusbar/1_statusbar_coin/blue/0.png',
        'img/7_statusbars/1_statusbar/1_statusbar_coin/blue/20.png',
        'img/7_statusbars/1_statusbar/1_statusbar_coin/blue/40.png',
        'img/7_statusbars/1_statusbar/1_statusbar_coin/blue/60.png'
    ];
    
    percentage = 0;

    constructor() {
        super();
        // Загружаем все изображения в кэш (метод loadImages определён в DrawableObject)
        this.loadImages(this.IMAGES);
        // Устанавливаем позицию и размеры статус-бара
        this.x = 40; 
        this.y = 60; 
        this.width = 200;
        this.height = 50;
        // Устанавливаем изначальное значение процента (0)
        this.setPercentage(0);
    }

    /**
     * Устанавливает процент заполнения статус-бара и обновляет отображаемое изображение.
     * Индекс изображения рассчитывается как Math.floor(percentage / 20), но ограничивается размером массива.
     * 
     * @param {number} percentage - Процент заполнения статус-бара (от 0 до 100)
     */
    setPercentage(percentage) {
        this.percentage = percentage;
        // Вычисляем индекс: для 0% → 0, для 20% → 1, для 40% → 2, для 60% → 3, для 80% и 100% также будет максимум 3,
        // так как в массиве всего 4 изображения (индексы 0...3)
        let imageIndex = Math.min(Math.floor(this.percentage / 20), this.IMAGES.length - 1);
        // Обновляем изображение, используя кэш загруженных изображений
        this.img = this.imageCache[this.IMAGES[imageIndex]];
    }

    /**
     * Метод resolveImageIndex() не используется, так как выбор изображения осуществляется через setPercentage().
     * Можно его удалить или оставить для справки.
     */
    resolveImageIndex() {
        if (this.percentage == 100) { 
            return 3;
        } else if (this.percentage > 80) {
            return 3;
        } else if (this.percentage > 60) {
            return 2;
        } else if (this.percentage > 40) {
            return 1;
        } else if (this.percentage > 20) { 
            return 1;
        } else {
            return 0;
        }
    }
}
