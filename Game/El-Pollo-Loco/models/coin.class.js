class Coin extends MovableObject {
    constructor() {
        super();
        this.loadImage('img/8_coin/coin_1.png'); 
        this.x = Math.random() * 1000; 
        this.y = Math.random() * 200 + 50; 
        this.width = 100; 
        this.height = 100; 
    }
}