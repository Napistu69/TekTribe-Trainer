import { useEffect, useRef } from 'react';
import Phaser from 'phaser';
import { BaseMiniGameScene } from '../games/BaseMiniGame';
import { TargetTapScene } from '../games/TargetTapScene';
import { RhythmGrazeScene } from '../games/RhythmGrazeScene';
import { ChargeLineScene } from '../games/ChargeLineScene';
import { SprintCourseScene } from '../games/SprintCourseScene';
import { SkyGlideScene } from '../games/SkyGlideScene';
import { AlphaResolveScene } from '../games/AlphaResolveScene';
import { useAuthStore } from '../stores/authStore';

interface GameEntry {
  scene: new () => BaseMiniGameScene;
  key: string;
}

const GAME_SCENE_MAP: Record<string, GameEntry> = {
  target_tap: { scene: TargetTapScene, key: 'TargetTap' },
  rhythm_graze: { scene: RhythmGrazeScene, key: 'RhythmGraze' },
  charge_line: { scene: ChargeLineScene, key: 'ChargeLine' },
  sprint_course: { scene: SprintCourseScene, key: 'SprintCourse' },
  sky_glide: { scene: SkyGlideScene, key: 'SkyGlide' },
  alpha_resolve: { scene: AlphaResolveScene, key: 'AlphaResolve' },
};

export interface MiniGameCanvasProps {
  gameId: string;
  gameName: string;
  difficulty: string;
  duration: number;
  companionUuid: string;
  onGameComplete: (score: number) => void;
  onCancel: () => void;
}

export function MiniGameCanvas({ gameId, gameName, difficulty, duration, companionUuid, onGameComplete }: MiniGameCanvasProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const gameRef = useRef<Phaser.Game | null>(null);
  const sessionToken = useAuthStore((s) => s.sessionToken);

  useEffect(() => {
    if (!containerRef.current) return;

    const gameEntry = GAME_SCENE_MAP[gameId];
    if (!gameEntry) {
      console.error(`Unknown game: ${gameId}`);
      return;
    }

    const { scene: SceneClass, key: sceneKey } = gameEntry;

    const handleComplete = (score: number) => {
      if (sessionToken) {
        fetch(`${import.meta.env.VITE_API_URL}/api/training/submit`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${sessionToken}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            companion_uuid: companionUuid,
            game_id: gameId,
            score,
            duration_seconds: duration,
          }),
        }).then(async (resp) => {
          if (resp.ok) {
            onGameComplete(score);
          } else {
            resp.json().then(err => console.error('Training submit failed:', err?.detail || err)).catch(() => {});
          }
        }).catch(console.error);
      } else {
        onGameComplete(score);
      }
    };

    const game = new Phaser.Game({
      type: Phaser.AUTO,
      parent: containerRef.current,
      width: 480,
      height: 320,
      scene: [SceneClass],
      backgroundColor: '#1a1a2e',
    });

    gameRef.current = game;

    // Start the scene with init data
    game.scene.start(sceneKey, {
      config: { id: gameId, name: gameName, species: '', stats: ['focus', 'trick_skill'] as [string, string], difficulty, duration },
      onComplete: handleComplete,
    });

    return () => {
      if (gameRef.current) {
        gameRef.current.destroy(true);
        gameRef.current = null;
      }
    };
  }, [gameId, gameName, difficulty, duration, companionUuid, sessionToken, onGameComplete]);

  return (
    <div className="minigame-canvas-container">
      <div ref={containerRef} className="minigame-canvas" />
    </div>
  );
}
