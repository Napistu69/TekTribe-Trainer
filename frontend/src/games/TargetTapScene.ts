import Phaser from 'phaser';
import { BaseMiniGameScene } from './BaseMiniGame';

/**
 * Target Tap — Dilo's game
 * Tap targets as they appear. Trains: Focus, Trick Skill
 */
export class TargetTapScene extends BaseMiniGameScene {
  private targets: Phaser.GameObjects.Arc[] = [];
  private hits: number = 0;
  private misses: number = 0;
  private spawnTimer: number = 0;

  constructor() {
    super('TargetTap');
  }

  create() {
    super.create();
    this.add.text(this.scale.width / 2, 80, 'Tap the targets!', {
      fontSize: '24px',
      color: '#00d4ff',
    }).setOrigin(0.5);
  }

  update(time: number, delta: number) {
    super.update(time, delta);
    if (this.isGameOver) return;

    // Spawn targets
    this.spawnTimer += delta;
    if (this.spawnTimer > 800) {
      this.spawnTimer = 0;
      this.spawnTarget();
    }

    // Remove expired targets
    this.targets = this.targets.filter((target) => {
      const age = time - (target.getData('born') as number);
      if (age > 2000) {
        target.destroy();
        this.misses++;
        return false;
      }
      return true;
    });
  }

  private spawnTarget() {
    const x = Phaser.Math.Between(40, this.scale.width - 40);
    const y = Phaser.Math.Between(120, this.scale.height - 40);
    const target = this.add.circle(x, y, 25, 0x6d4aff);
    target.setInteractive();
    target.setData('born', this.time);
    
    target.on('pointerdown', () => {
      this.hits++;
      this.addScore(10);
      target.destroy();
      // Remove from array
      this.targets = this.targets.filter(t => t !== target);
    });
    
    this.targets.push(target);
  }

  protected calculateFinalScore(): number {
    const total = this.hits + this.misses;
    if (total === 0) return 0;
    return Math.round((this.hits / total) * 100);
  }
}
