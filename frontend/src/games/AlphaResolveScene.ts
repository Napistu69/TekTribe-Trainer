import { BaseMiniGameScene } from './BaseMiniGame';

/**
 * Alpha Resolve — Rex's game
 * Stamina management — tap to maintain meter in target zone. Trains: Power, Discipline
 */
export class AlphaResolveScene extends BaseMiniGameScene {
  private stamina: number = 50;
  private targetMin: number = 40;
  private targetMax: number = 60;
  private pressureRate: number = 0.02;
  private inZone: boolean = false;
  private zoneTime: number = 0;

  constructor() {
    super('AlphaResolve');
  }

  create() {
    super.create();
    
    const centerY = this.scale.height / 2;
    
    // Target zone
    const zoneHeight = (this.targetMax - this.targetMin) * 4;
    const zoneY = centerY - 100 + this.targetMin * 2;
    this.add.rectangle(this.scale.width / 2, zoneY + zoneHeight / 2, 60, zoneHeight, 0x00ff88, 0.2);
    
    this.add.text(this.scale.width / 2, 100, 'Tap to push stamina UP! Hold in the green zone!', {
      fontSize: '16px',
      color: '#ffffff',
    }).setOrigin(0.5);
    
    // Stamina bar background
    this.add.rectangle(this.scale.width / 2, centerY, 40, 200, 0x2a2a3e);
    
    // Input
    this.input.on('pointerdown', () => { this.inZone = true; });
    this.input.on('pointerup', () => { this.inZone = false; });
  }

  update(time: number, delta: number) {
    super.update(time, delta);
    if (this.isGameOver) return;

    // Stamina naturally decreases
    this.stamina -= this.pressureRate * delta;
    
    // Tap to increase
    if (this.inZone) {
      this.stamina += 0.05 * delta;
    }
    
    // Clamp
    this.stamina = Math.max(0, Math.min(100, this.stamina));
    
    // Track zone time
    if (this.stamina >= this.targetMin && this.stamina <= this.targetMax) {
      this.zoneTime += delta;
    }
    
    // Pressure increases over time
    this.pressureRate += 0.00001 * delta;
    
    this.updateDisplay();
  }

  private updateDisplay() {
    const centerY = this.scale.height / 2;
    
    // Remove old display
    this.children.getAll().forEach(child => {
      if (child.getData('isDisplay')) child.destroy();
    });
    
    // Stamina bar
    const barHeight = this.stamina * 2;
    const color = this.stamina >= this.targetMin && this.stamina <= this.targetMax ? 0x00ff88 : 0xff4444;
    const bar = this.add.rectangle(this.scale.width / 2, centerY + 100 - barHeight / 2, 36, barHeight, color);
    bar.setData('isDisplay', true);
  }

  protected calculateFinalScore(): number {
    return Math.min(100, Math.round(this.zoneTime / 100));
  }
}
