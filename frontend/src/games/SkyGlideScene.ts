import Phaser from 'phaser';
import { BaseMiniGameScene } from './BaseMiniGame';

/**
 * Sky Glide — Ptera's game
 * Tilt/drag to balance through rings. Trains: Agility, Curiosity
 */
export class SkyGlideScene extends BaseMiniGameScene {
  private player!: Phaser.GameObjects.Ellipse;
  private rings: Phaser.GameObjects.Arc[] = [];
  private spawnTimer: number = 0;
  private passed: number = 0;
  private targetX: number = 0;

  constructor() {
    super('SkyGlide');
  }

  create() {
    super.create();
    
    this.targetX = this.scale.width / 2;
    
    // Player (simple circle)
    this.player = this.add.ellipse(this.scale.width / 2, this.scale.height - 100, 30, 20, 0x00d4ff);
    
    this.add.text(this.scale.width / 2, 100, 'Drag left/right to glide through rings!', {
      fontSize: '18px',
      color: '#ffffff',
    }).setOrigin(0.5);
    
    // Input
    this.input.on('pointermove', (pointer: Phaser.Input.Pointer) => {
      this.targetX = pointer.x;
    });
  }

  update(time: number, delta: number) {
    super.update(time, delta);
    if (this.isGameOver) return;

    // Move player toward target
    this.player.x += (this.targetX - this.player.x) * 0.1;
    
    // Spawn rings
    this.spawnTimer += delta;
    if (this.spawnTimer > 1500) {
      this.spawnTimer = 0;
      this.spawnRing();
    }
    
    // Move rings up
    this.rings = this.rings.filter(ring => {
      ring.y -= 3;
      
      // Check if player passed through
      const dist = Math.abs(ring.x - this.player.x);
      if (ring.y < this.player.y && !ring.getData('scored')) {
        ring.setData('scored', true);
        if (dist < 40) {
          this.passed++;
          this.addScore(15);
          ring.setStrokeStyle(2, 0x00ff88);
        }
      }
      
      if (ring.y < -50) {
        ring.destroy();
        return false;
      }
      return true;
    });
  }

  private spawnRing() {
    const x = Phaser.Math.Between(60, this.scale.width - 60);
    const ring = this.add.circle(x, this.scale.height + 50, 30);
    ring.setStrokeStyle(3, 0x6d4aff);
    ring.setData('scored', false);
    this.rings.push(ring);
  }

  protected calculateFinalScore(): number {
    return Math.min(100, this.passed * 10);
  }
}
