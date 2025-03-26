// scoreManager.js

/**
 * Сохраняет новый результат в таблице лидеров.
 * @param {string} name - Имя игрока.
 * @param {number} score - Количество очков игрока.
 */
function saveScore(name, score) {
    // Получаем существующий массив результатов из localStorage или создаём новый
    let leaderboard = JSON.parse(localStorage.getItem('leaderboard')) || [];
    
    // Добавляем новый результат
    leaderboard.push({ name, score });
    
    // Сортируем результаты по убыванию очков
    leaderboard.sort((a, b) => b.score - a.score);
    
    // Оставляем только топ 20
    leaderboard = leaderboard.slice(0, 20);
    
    // Сохраняем обновлённый массив в localStorage
    localStorage.setItem('leaderboard', JSON.stringify(leaderboard));
  }
  
  /**
   * Возвращает массив лидеров (Top 20) из localStorage.
   * @returns {Array} Массив объектов с полями name и score.
   */
  function getLeaderboard() {
    return JSON.parse(localStorage.getItem('leaderboard')) || [];
  }
  