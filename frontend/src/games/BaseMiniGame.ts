import Phaser from 'phaser';

/**
 * Base configuration for all mini-games.
 * Subclasses override create() and update().
 */
export interface MiniGameConfig {
  /** Game ID (e.g., 'target_tap') */
  id: string;
  /** Display name */
  name: string;
  /** Species this game trains */
  species: string;
  /** Stats trained */
  stats: [string, string];
  /** Difficulty rating */
  difficulty: 'very_easy' | 'easy' | 'medium' | 'hard';
  /** Round duration in seconds */
  duration: number;
}

export abstract class BaseMiniGameScene extends Phaser.Scene {
  protected score: number = 0;
  protected timeRemaining: number = 60;
  protected isGameOver: boolean = false;
  protected onComplete?: (score: number) => void;
  
  constructor(key: string) {
    super({ key });
  }

  init(data: { config: MiniGameConfig; onComplete?: (score: number) => void }) {
    this.score = 0;
    this.timeRemaining = data.config?.duration || 60;
    this.isGameOver = false;
    this.onComplete = data.onComplete;
  }

  create() {
    // Background
    this.cameras.main.setBackgroundColor('#1a1a2e');
    
    // Timer text
    this.add.text(16, 16, `Time: ${this.timeRemaining}`, {
      fontSize: '20px',
      color: '#00d4ff',
    });
    
    // Score text
    this.add.text(16, 48, `Score: ${this.score}`, {
      fontSize: '20px',
      color: '#ffffff',
    });
  }

  update(_time: number, delta: number) {
    if (this.isGameOver) return;
    
    // Update timer
    this.timeRemaining -= delta / 1000;
    if (this.timeRemaining <= 0) {
      this.timeRemaining = 0;
      this.endGame();
    }
    
    // Update timer display
    const timerText = this.children.getByName('timer') as Phaser.GameObjects.Text;
    if (timerText) {
      timerText.setText(`Time: ${Math.ceil(this.timeRemaining)}`);
    }
  }

  protected addScore(points: number) {
    this.score += points;
    const scoreText = this.children.getByName('score') as Phaser.GameObjects.Text;
    if (scoreText) {
      scoreText.setText(`Score: ${this.score}`);
    }
  }

  protected endGame() {
    this.isGameOver = true;
    // Calculate final score (0-100)
    const finalScore = Math.min(100, Math.max(0, this.calculateFinalScore()));
    
    if (this.onComplete) {
      this.onComplete(finalScore);
    }
  }

  /** Override to calculate final score from game-specific metrics */
  protected abstract calculateFinalScore(): number;
}


