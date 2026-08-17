import Phaser from 'phaser';
import { BaseMiniGameScene } from './BaseMiniGame';

/**
 * Sprint Course — Raptor's game
 * Swipe lanes and jump obstacles. Trains: Speed, Drive
 */
export class SprintCourseScene extends BaseMiniGameScene {
  private playerLane: number = 1;
  private obstacles: Phaser.GameObjects.Rectangle[] = [];
  private spawnTimer: number = 0;
  private distance: number = 0;
  private dodged: number = 0;

  constructor() {
    super('SprintCourse');
  }

  create() {
    super.create();
    
    const centerY = this.scale.height / 2;
    
    // Lane indicators
    const laneWidth = 80;
    const startX = this.scale.width / 2 - laneWidth;
    
    for (let i = 0; i < 3; i++) {
      this.add.rectangle(startX + i * laneWidth, centerY, 60, 200, 0x2a2a3e, 0.5);
    }
    
    this.add.text(this.scale.width / 2, 100, 'Tap left/right to dodge!', {
      fontSize: '18px',
      color: '#ffffff',
    }).setOrigin(0.5);
    
    // Input
    this.input.on('pointerdown', (pointer: Phaser.Input.Pointer) => {
      if (pointer.x < this.scale.width / 2) {
        this.playerLane = Math.max(0, this.playerLane - 1);
      } else {
        this.playerLane = Math.min(2, this.playerLane + 1);
      }
    });
  }

  update(time: number, delta: number) {
    super.update(time, delta);
    if (this.isGameOver) return;

    this.distance++;
    this.spawnTimer += delta;
    
    // Spawn obstacles
    if (this.spawnTimer > 1000) {
      this.spawnTimer = 0;
      this.spawnObstacle();
    }
    
    // Move obstacles
    const speed = 5;
    this.obstacles = this.obstacles.filter(obs => {
      obs.y += speed;
      if (obs.y > this.scale.height + 50) {
        this.dodged++;
        obs.destroy();
        return false;
      }
      return true;
    });
  }

  private spawnObstacle() {
    const lane = Phaser.Math.Between(0, 2);
    const laneWidth = 80;
    const startX = this.scale.width / 2 - laneWidth;
    const obs = this.add.rectangle(startX + lane * laneWidth, -30, 50, 50, 0xff4444);
    obs.setData('lane', lane);
    this.obstacles.push(obs);
  }

  protected calculateFinalScore(): number {
    return Math.min(100, Math.round(this.dodged * 2));
  }
}
