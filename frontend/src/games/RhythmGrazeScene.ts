import Phaser from 'phaser';
import { BaseMiniGameScene } from './BaseMiniGame';

/**
 * Rhythm Graze — Parasaur's game
 * Tap in rhythm with moving indicator. Trains: Trust, Affection
 */
export class RhythmGrazeScene extends BaseMiniGameScene {
  private indicator!: Phaser.GameObjects.Rectangle;
  private hitZone!: Phaser.GameObjects.Rectangle;
  private direction: number = 1;
  private speed: number = 2;
  private hits: number = 0;
  private attempts: number = 0;

  constructor() {
    super('RhythmGraze');
  }

  create() {
    super.create();
    
    const centerY = this.scale.height / 2;
    
    // Hit zone (center)
    this.hitZone = this.add.rectangle(this.scale.width / 2, centerY, 60, 80, 0x00ff88, 0.3);
    
    // Moving indicator
    this.indicator = this.add.rectangle(50, centerY, 30, 60, 0x00d4ff);
    
    this.add.text(this.scale.width / 2, centerY - 60, 'HIT', {
      fontSize: '20px',
      color: '#00ff88',
    }).setOrigin(0.5);
    
    this.add.text(this.scale.width / 2, 80, 'Tap when indicator is in the zone!', {
      fontSize: '18px',
      color: '#ffffff',
    }).setOrigin(0.5);
    
    // Tap input
    this.input.on('pointerdown', () => this.checkHit());
  }

  update(time: number, delta: number) {
    super.update(time, delta);
    if (this.isGameOver) return;

    // Move indicator
    this.indicator.x += this.speed * this.direction;
    
    if (this.indicator.x > this.scale.width - 40) {
      this.direction = -1;
    } else if (this.indicator.x < 40) {
      this.direction = 1;
    }
  }

  private checkHit() {
    this.attempts++;
    const distance = Math.abs(this.indicator.x - this.hitZone.x);
    
    if (distance < 30) {
      this.hits++;
      this.addScore(15);
      this.cameras.main.flash(100, 0, 255, 100);
    }
  }

  protected calculateFinalScore(): number {
    if (this.attempts === 0) return 0;
    return Math.round((this.hits / this.attempts) * 100);
  }
}
