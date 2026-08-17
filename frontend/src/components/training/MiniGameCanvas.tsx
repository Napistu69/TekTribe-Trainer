import { useEffect, useRef, useState } from 'react';
import Phaser from 'phaser';
import { TargetTapScene } from '../../games/TargetTapScene';
import { RhythmGrazeScene } from '../../games/RhythmGrazeScene';
import { SprintCourseScene } from '../../games/SprintCourseScene';
import { SkyGlideScene } from '../../games/SkyGlideScene';
import { ChargeLineScene } from '../../games/ChargeLineScene';
import { AlphaResolveScene } from '../../games/AlphaResolveScene';

interface MiniGameCanvasProps {
  gameId: string;
  onComplete: (score: number) => void;
}

const SCENE_MAP: Record<string, typeof Phaser.Scene> = {
  target_tap: TargetTapScene,
  rhythm_graze: RhythmGrazeScene,
  sprint_course: SprintCourseScene,
  sky_glide: SkyGlideScene,
  charge_line: ChargeLineScene,
  alpha_resolve: AlphaResolveScene,
};

export function MiniGameCanvas({ gameId, onComplete }: MiniGameCanvasProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const gameRef = useRef<Phaser.Game | null>(null);
  const [gameOver, setGameOver] = useState(false);

  useEffect(() => {
    if (!containerRef.current || !gameId) return;

    const SceneClass = SCENE_MAP[gameId];
    if (!SceneClass) return;

    const config: Phaser.Types.Core.GameConfig = {
      type: Phaser.AUTO,
      parent: containerRef.current,
      width: containerRef.current.clientWidth || 360,
      height: containerRef.current.clientHeight || 500,
      backgroundColor: '#1a1a2e',
      scene: [SceneClass],
      scale: {
        mode: Phaser.Scale.FIT,
        autoCenter: Phaser.Scale.CENTER_BOTH,
      },
      audio: {
        noAudio: true,
      },
    };

    const game = new Phaser.Game(config);
    gameRef.current = game;

    // Handle game completion via scene data
    game.events.on('gamecomplete', (score: number) => {
      setGameOver(true);
      onComplete(score);
    });

    return () => {
      game.destroy(true);
      gameRef.current = null;
    };
  }, [gameId, onComplete]);

  return (
    <div className="mini-game-container">
      <div ref={containerRef} className="game-canvas" />
      {gameOver && (
        <div className="game-overlay">
          <p>Game Complete!</p>
        </div>
      )}
    </div>
  );
}
