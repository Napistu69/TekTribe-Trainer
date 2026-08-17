import { BaseMiniGameScene } from './BaseMiniGame';

/**
 * Charge Line — Trike's game
 * Hold to charge power, release at optimal moment. Trains: Grit, Defense
 */
export class ChargeLineScene extends BaseMiniGameScene {
  private power: number = 0;
  private charging: boolean = false;
  private targetZone: number = 70; // Target power level
  private charges: number = 0;
  private bestAccuracy: number = 0;

  constructor() {
    super('ChargeLine');
  }

  create() {
    super.create();
    
    const centerY = this.scale.height / 2;
    
    // Power bar background
    this.add.rectangle(this.scale.width / 2, centerY, 200, 30, 0x2a2a3e);
    
    // Target zone indicator
    const targetX = this.scale.width / 2 - 100 + (this.targetZone / 100) * 200;
    this.add.rectangle(targetX, centerY, 20, 40, 0x00ff88, 0.5);
    
    this.add.text(this.scale.width / 2, 100, 'Hold SPACE or tap to charge! Release at the target!', {
      fontSize: '16px',
      color: '#ffffff',
    }).setOrigin(0.5);
    
    // Input
    this.input.keyboard?.on('keydown-SPACE', () => { this.charging = true; });
    this.input.keyboard?.on('keyup-SPACE', () => { this.release(); });
    this.input.on('pointerdown', () => { this.charging = true; });
    this.input.on('pointerup', () => { this.release(); });
  }

  update(time: number, delta: number) {
    super.update(time, delta);
    if (this.isGameOver) return;

    if (this.charging) {
      this.power = Math.min(100, this.power + delta * 0.05);
      this.updatePowerBar();
    }
  }

  private updatePowerBar() {
    const centerY = this.scale.height / 2;
    const barWidth = (this.power / 100) * 200;
    
    // Remove old bar
    this.children.getAll().forEach(child => {
      if (child.getData('isPowerBar')) child.destroy();
    });
    
    // Draw new bar
    const bar = this.add.rectangle(this.scale.width / 2 - 100 + barWidth / 2, centerY, barWidth, 28, 0x6d4aff);
    bar.setData('isPowerBar', true);
  }

  private release() {
    if (!this.charging) return;
    this.charging = false;
    this.charges++;
    
    const accuracy = 100 - Math.abs(this.power - this.targetZone);
    this.bestAccuracy = Math.max(this.bestAccuracy, accuracy);
    this.addScore(Math.round(accuracy * 0.15));
    
    this.power = 0;
    this.updatePowerBar();
  }

  protected calculateFinalScore(): number {
    if (this.charges === 0) return 0;
    return Math.round(this.bestAccuracy);
  }
}
