import { useEffect, useRef } from 'react';
import Phaser from 'phaser';

interface PhaserGameProps {
  width?: number;
  height?: number;
}

class HatcheryScene extends Phaser.Scene {
  constructor() {
    super({ key: 'HatcheryScene' });
  }

  preload() {
    this.load.spritesheet('raptor_attack', '/assets/Creatures/Raptor_Adult_Attack_Sprite_Sheet.png', {
      frameWidth: 256,
      frameHeight: 819,
    });
    
    this.load.image('egg_common', '/assets/Hatch System/Egg_Common.png');
    this.load.image('egg_uncommon', '/assets/Hatch System/Egg_Uncommon.png');
    this.load.image('egg_rare', '/assets/Hatch System/Egg_Rare.png');
    this.load.image('egg_epic', '/assets/Hatch System/Egg_Epic.png');
    this.load.image('egg_ascendant', '/assets/Hatch System/Egg_Ascendant.png');
    this.load.image('egg_legendary', '/assets/Hatch System/Egg_Legendary.png');
    this.load.image('egg_mythic', '/assets/Hatch System/Egg_Mythic.png');
  }

  create() {
    const centerX = this.cameras.main.width / 2;
    const centerY = this.cameras.main.height / 2;

    // Background gradient
    this.add.rectangle(centerX, centerY, this.cameras.main.width, this.cameras.main.height, 0x0a0a1a);
    this.add.grid(centerX, centerY, this.cameras.main.width, this.cameras.main.height, 32, 32, 0x0a0a1a, 1, 0x1a1a3e, 0.3);

    // Title
    this.add.text(centerX, 40, 'HATCHERY', {
      fontSize: '32px',
      fontFamily: 'Segoe UI, sans-serif',
      color: '#00d4ff',
      fontStyle: 'bold',
    }).setOrigin(0.5);

    // Create raptor attack animation
    this.anims.create({
      key: 'raptor_attack',
      frames: this.anims.generateFrameNumbers('raptor_attack', { start: 0, end: 7 }),
      frameRate: 10,
      repeat: -1,
    });

    // Raptor sprite
    const raptor = this.add.sprite(centerX - 150, centerY + 50, 'raptor_attack');
    raptor.setScale(0.4);
    raptor.play('raptor_attack');

    // Egg display
    const egg = this.add.image(centerX + 120, centerY, 'egg_rare');
    egg.setScale(0.8);
    
    // Egg float animation
    this.tweens.add({
      targets: egg,
      y: centerY - 10,
      duration: 1500,
      ease: 'Sine.easeInOut',
      yoyo: true,
      repeat: -1,
    });

    // Glow effect around egg
    const glow = this.add.circle(centerX + 120, centerY, 60, 0x0080ff, 0.2);
    this.tweens.add({
      targets: glow,
      scaleX: 1.2,
      scaleY: 1.2,
      alpha: 0.1,
      duration: 1000,
      yoyo: true,
      repeat: -1,
    });

    // Click egg to "incubate"
    egg.setInteractive({ useHandCursor: true });
    egg.on('pointerdown', () => {
      this.tweens.add({
        targets: egg,
        scaleX: 1.2,
        scaleY: 1.2,
        duration: 100,
        yoyo: true,
      });
    });

    // Labels
    this.add.text(centerX - 150, centerY + 120, 'Raptor', {
      fontSize: '16px',
      fontFamily: 'Segoe UI, sans-serif',
      color: '#ffffff',
    }).setOrigin(0.5);

    this.add.text(centerX + 120, centerY + 80, 'Rare Egg', {
      fontSize: '16px',
      fontFamily: 'Segoe UI, sans-serif',
      color: '#0080ff',
    }).setOrigin(0.5);
  }
}

export function PhaserGame({ width = 800, height = 500 }: PhaserGameProps) {
  const gameRef = useRef<Phaser.Game | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current || gameRef.current) return;

    const config: Phaser.Types.Core.GameConfig = {
      type: Phaser.AUTO,
      width,
      height,
      parent: containerRef.current,
      backgroundColor: '#0a0a1a',
      scene: [HatcheryScene],
      scale: {
        mode: Phaser.Scale.FIT,
        autoCenter: Phaser.Scale.CENTER_BOTH,
      },
      render: {
        pixelArt: true,
        antialias: false,
      },
    };

    gameRef.current = new Phaser.Game(config);

    return () => {
      gameRef.current?.destroy(true);
      gameRef.current = null;
    };
  }, [width, height]);

  return <div ref={containerRef} className="phaser-container" />;
}
