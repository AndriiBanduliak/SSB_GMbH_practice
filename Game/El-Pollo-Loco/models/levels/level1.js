// Создаем тестового босса с координатой x = 2000 вместо 2500
const testEndboss = new Endboss();
testEndboss.x = 2000; // Для теста, чтобы босс был виден

// Создаем уровень с необходимыми объектами
const level1 = new Level(
    [
        new Chicken(),
        new Chicken(),
        new Chicken(),
        testEndboss
    ],
    [
        new Cloud()
    ],
    [
        new BackgroundObject('img/5_background/layers/air.png', -719),
        new BackgroundObject('img/5_background/layers/2_second_layer/1.png', -720),
        new BackgroundObject('img/5_background/layers/1_first_layer/2.png', -719),

        new BackgroundObject('img/5_background/layers/air.png', -719 * 2),
        new BackgroundObject('img/5_background/layers/3_third_layer/2.png', -719 * 2),
        new BackgroundObject('img/5_background/layers/2_second_layer/2.png', -719 * 2),
        new BackgroundObject('img/5_background/layers/1_first_layer/1.png', -719 * 2),

        new BackgroundObject('img/5_background/layers/air.png', 0),
        new BackgroundObject('img/5_background/layers/3_third_layer/1.png', 0),
        new BackgroundObject('img/5_background/layers/2_second_layer/1.png', 0),
        new BackgroundObject('img/5_background/layers/2_second_layer/2.png', 0),
        new BackgroundObject('img/5_background/layers/1_first_layer/1.png', 0),

        new BackgroundObject('img/5_background/layers/air.png', 718),
        new BackgroundObject('img/5_background/layers/3_third_layer/2.png', 718),
        new BackgroundObject('img/5_background/layers/2_second_layer/2.png', 718),
        new BackgroundObject('img/5_background/layers/1_first_layer/2.png', 718),

        new BackgroundObject('img/5_background/layers/air.png', 718 * 2),
        new BackgroundObject('img/5_background/layers/3_third_layer/1.png', 718 * 2),
        new BackgroundObject('img/5_background/layers/2_second_layer/1.png', 718 * 2),
        new BackgroundObject('img/5_background/layers/1_first_layer/1.png', 718 * 2),

        new BackgroundObject('img/5_background/layers/air.png', 718 * 3),
        new BackgroundObject('img/5_background/layers/3_third_layer/2.png', 718 * 3),
        new BackgroundObject('img/5_background/layers/2_second_layer/2.png', 718 * 3),
        new BackgroundObject('img/5_background/layers/1_first_layer/2.png', 718 * 3),
    ],
    [
        new Coin(),
        new Coin()
    ]
);

// Устанавливаем конец уровня так, чтобы персонаж и босс были видны
level1.level_end_x = 2500;
