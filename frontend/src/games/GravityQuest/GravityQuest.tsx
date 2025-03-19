import "./GravityQuest.css";

import Phaser from "phaser";
import { useEffect } from "react";

// Game configuration types
interface TractorBeamConfig {
  radius: number;
  strength: number;
  falloff: number;
}

interface TractorBeamVisuals {
  circles: {
    count: number;
    speed: number;
    baseAlpha: number;
    lineWidth: number;
    color: number;
  };
  particles: {
    count: number;
    size: number;
    rotationSpeed: number;
    spiralSpeed: number;
    baseAlpha: number;
    color: number;
  };
  forceLines: {
    maxThickness: number;
    baseAlpha: number;
    color: number;
    dots: {
      count: number;
      speed: number;
      baseAlpha: number;
      color: number;
    };
  };
}

// Game constants
const GLOBAL_GRAVITY = 300;
const BASE_GAME_WIDTH = 800;
const BASE_GAME_HEIGHT = 600;
const JUMP_INITIAL_VELOCITY = -300; // Initial jump burst
const JUMP_FORCE_DECAY = 0.85; // How quickly the force decays (0-1, higher = slower decay)
const MIN_JUMP_FORCE = 5; // Minimum force before stopping the jump
const MAX_JUMP_FORCE = 400; // Starting jump force

const tractorBeamConfig: TractorBeamConfig = {
  radius: 200,
  strength: 100,
  falloff: 2.0,
};

const tractorBeamVisuals: TractorBeamVisuals = {
  circles: {
    count: 3,
    speed: 1500,
    baseAlpha: 0.3,
    lineWidth: 4,
    color: 0x00ff00,
  },
  particles: {
    count: 0,
    size: 3,
    rotationSpeed: 1000,
    spiralSpeed: 800,
    baseAlpha: 0.4,
    color: 0x00ff00,
  },
  forceLines: {
    maxThickness: 10,
    baseAlpha: 0.4,
    color: 0x00ff00,
    dots: {
      count: 3,
      speed: 500,
      baseAlpha: 0.6,
      color: 0x00ff00,
    },
  },
};

const Game = () => {
  useEffect(() => {
    // Game state
    const gameState = {
      player: null as Phaser.Physics.Arcade.Sprite | null,
      stars: null as Phaser.Physics.Arcade.Group | null,
      bombs: null as Phaser.Physics.Arcade.Group | null,
      platforms: null as Phaser.Physics.Arcade.StaticGroup | null,
      cursors: null as Phaser.Types.Input.Keyboard.CursorKeys | null,
      score: 0,
      gameOver: false,
      scoreText: null as Phaser.GameObjects.Text | null,
      gameOverText: null as Phaser.GameObjects.Text | null,
      restartText: null as Phaser.GameObjects.Text | null,
      spaceKey: null as Phaser.Input.Keyboard.Key | null,
      tractorBeamKey: null as Phaser.Input.Keyboard.Key | null,
      tractorBeamCircle: null as Phaser.GameObjects.Graphics | null,
      debugText: null as Phaser.GameObjects.Text | null,
      currentJumpForce: 0,
      isJumping: false,
    };

    const setupStars = (sprite: Phaser.Physics.Arcade.Sprite): void => {
      sprite.setGravityY(-GLOBAL_GRAVITY / 2);
      sprite.setBounceY(1);
      sprite.setBounceX(1);
      sprite.setVelocityX(Phaser.Math.FloatBetween(-100, 100));
      sprite.setCollideWorldBounds(true);
    };

    const resetStars = (starsGroup: Phaser.Physics.Arcade.Group): void => {
      starsGroup.children.iterate((child): boolean | null => {
        const sprite = child as Phaser.Physics.Arcade.Sprite;
        sprite.enableBody(true, sprite.x, 0, true, true);
        setupStars(sprite);
        return null;
      });
    };

    const calculateTractorBeamForce = (
      source: Phaser.Physics.Arcade.Sprite,
      target: Phaser.Physics.Arcade.Sprite
    ): { x: number; y: number } => {
      const dx = source.x - target.x;
      const dy = source.y - target.y;
      const distance = Math.sqrt(dx * dx + dy * dy);

      if (distance > tractorBeamConfig.radius) {
        return { x: 0, y: 0 };
      }

      const force =
        tractorBeamConfig.strength *
        Math.pow(
          1 - distance / tractorBeamConfig.radius,
          tractorBeamConfig.falloff
        );

      return {
        x: (dx / distance) * force,
        y: (dy / distance) * force,
      };
    };

    const config: Phaser.Types.Core.GameConfig = {
      type: Phaser.AUTO,
      scale: {
        mode: Phaser.Scale.FIT,
        parent: "game-container",
        autoCenter: Phaser.Scale.CENTER_BOTH,
        width: BASE_GAME_WIDTH,
        height: BASE_GAME_HEIGHT,
        min: {
          width: BASE_GAME_WIDTH / 2,
          height: BASE_GAME_HEIGHT / 2,
        },
        max: {
          width: BASE_GAME_WIDTH * 2,
          height: BASE_GAME_HEIGHT * 2,
        },
      },
      physics: {
        default: "arcade",
        arcade: {
          gravity: { y: GLOBAL_GRAVITY, x: 0 },
          debug: false,
        },
      },
      scene: {
        preload,
        create,
        update,
      },
    };

    const game = new Phaser.Game(config);

    function showGameOver(this: Phaser.Scene) {
      gameState.gameOverText = this.add.text(400, 250, "GAME OVER", {
        fontSize: "64px",
        color: "#ff0000",
      });
      gameState.gameOverText.setOrigin(0.5);

      gameState.restartText = this.add.text(
        400,
        350,
        "Press SPACE or Click to Restart",
        {
          fontSize: "32px",
          color: "#fff",
        }
      );
      gameState.restartText.setOrigin(0.5);

      // Add click handler for the entire game
      this.input.on("pointerdown", restartGame, this);
    }

    function restartGame(this: Phaser.Scene) {
      // Reset game state
      gameState.gameOver = false;
      gameState.score = 0;
      gameState.scoreText!.setText("Score: 0");

      // Remove game over text
      if (gameState.gameOverText) gameState.gameOverText.destroy();
      if (gameState.restartText) gameState.restartText.destroy();

      // Remove click handler
      this.input.off("pointerdown", restartGame, this);

      // Reset player
      gameState.player!.setTint(0xffffff);
      gameState.player!.anims.play("turn");
      gameState.player!.setPosition(100, 450);
      gameState.player!.setVelocity(0, 0);

      // Reset all stars
      resetStars(gameState.stars!);

      // Clear bombs
      gameState.bombs!.clear(true, true);

      // Resume physics
      this.physics.resume();
    }

    function preload(this: Phaser.Scene) {
      this.load.image("sky", "/assets/sky1.jpg");
      this.load.image("ground", "/assets/platform.png");
      this.load.image("star", "/assets/star.png");
      this.load.image("bomb", "/assets/bomb.png");
      this.load.spritesheet("dude", "/assets/dude.png", {
        frameWidth: 32,
        frameHeight: 48,
      });
    }

    function create(this: Phaser.Scene) {
      // Add space key for restart
      if (this.input.keyboard) {
        gameState.spaceKey = this.input.keyboard.addKey(
          Phaser.Input.Keyboard.KeyCodes.SPACE
        );

        // Add tractor beam key (separate from restart key)
        gameState.tractorBeamKey = this.input.keyboard.addKey(
          Phaser.Input.Keyboard.KeyCodes.SHIFT
        );
      }

      this.add.image(400, 300, "sky");

      gameState.platforms = this.physics.add.staticGroup();

      gameState.platforms.create(400, 568, "ground").setScale(2).refreshBody();

      gameState.platforms.create(600, 400, "ground");
      gameState.platforms.create(50, 250, "ground");
      gameState.platforms.create(750, 220, "ground");

      gameState.player = this.physics.add.sprite(100, 450, "dude");

      gameState.player.setBounce(0.2);
      gameState.player.setCollideWorldBounds(true);

      this.anims.create({
        key: "left",
        frames: this.anims.generateFrameNumbers("dude", { start: 0, end: 3 }),
        frameRate: 10,
        repeat: -1,
      });

      this.anims.create({
        key: "turn",
        frames: [{ key: "dude", frame: 4 }],
        frameRate: 20,
      });

      this.anims.create({
        key: "right",
        frames: this.anims.generateFrameNumbers("dude", { start: 5, end: 8 }),
        frameRate: 10,
        repeat: -1,
      });

      // Add colliders
      if (gameState.player && gameState.platforms) {
        this.physics.add.collider(gameState.player, gameState.platforms);
      }

      gameState.cursors = this.input.keyboard!.createCursorKeys();

      gameState.stars = this.physics.add.group({
        key: "star",
        repeat: 11,
        setXY: { x: 12, y: 0, stepX: 70 },
      });

      // Set bounce for all stars in the group
      gameState.stars.children.iterate((child): boolean | null => {
        setupStars(child as Phaser.Physics.Arcade.Sprite);
        return null;
      });

      this.physics.add.collider(gameState.stars, gameState.platforms);

      gameState.bombs = this.physics.add.group();

      gameState.scoreText = this.add.text(16, 16, "Score: 0", {
        fontSize: "32px",
        color: "#000",
      });

      // Create debug graphics for tractor beam
      gameState.tractorBeamCircle = this.add.graphics();
      gameState.tractorBeamCircle.setDepth(1); // Ensure it renders above the background

      // Add debug text
      gameState.debugText = this.add.text(16, 50, "", {
        fontSize: "16px",
        color: "#fff",
        backgroundColor: "#000",
        padding: { x: 4, y: 4 },
      });
      gameState.debugText.setDepth(1);
      gameState.debugText.setVisible(false);

      const collectStarCallback = (
        _object1:
          | Phaser.Types.Physics.Arcade.GameObjectWithBody
          | Phaser.Physics.Arcade.Body
          | Phaser.Physics.Arcade.StaticBody
          | Phaser.Tilemaps.Tile,
        object2:
          | Phaser.Types.Physics.Arcade.GameObjectWithBody
          | Phaser.Physics.Arcade.Body
          | Phaser.Physics.Arcade.StaticBody
          | Phaser.Tilemaps.Tile
      ) => {
        (object2 as Phaser.Physics.Arcade.Sprite).disableBody(true, true);

        gameState.score += 10;
        gameState.scoreText!.setText("Score: " + gameState.score);

        if (gameState.stars!.countActive(true) === 0) {
          resetStars(gameState.stars!);

          const x =
            gameState.player!.x < 400
              ? Phaser.Math.Between(400, 800)
              : Phaser.Math.Between(0, 400);

          const bomb = gameState.bombs!.create(
            x,
            16,
            "bomb"
          ) as Phaser.Physics.Arcade.Sprite;
          bomb.setBounce(1);
          bomb.setCollideWorldBounds(true);
          bomb.setVelocity(Phaser.Math.Between(-200, 200), 20);
          bomb.setGravityY(0);
          if (gameState.platforms) {
            this.physics.add.collider(bomb, gameState.platforms);
          }
        }
      };

      const hitBombCallback = (
        object1:
          | Phaser.Types.Physics.Arcade.GameObjectWithBody
          | Phaser.Physics.Arcade.Body
          | Phaser.Physics.Arcade.StaticBody
          | Phaser.Tilemaps.Tile,
        _object2:
          | Phaser.Types.Physics.Arcade.GameObjectWithBody
          | Phaser.Physics.Arcade.Body
          | Phaser.Physics.Arcade.StaticBody
          | Phaser.Tilemaps.Tile
      ) => {
        const hitPlayer = object1 as Phaser.Physics.Arcade.Sprite;
        this.physics.pause();
        hitPlayer.setTint(0xff0000);
        hitPlayer.anims.play("turn");
        gameState.gameOver = true;
        showGameOver.call(this);
      };

      this.physics.add.overlap(
        gameState.player,
        gameState.stars,
        collectStarCallback,
        undefined,
        this
      );
      this.physics.add.collider(
        gameState.player,
        gameState.bombs,
        hitBombCallback,
        undefined,
        this
      );
    }

    // Helper function to update tractor beam visuals
    function updateTractorBeamVisuals(
      scene: Phaser.Scene,
      isActive: boolean,
      affectedObjects: {
        stars: Array<{ sprite: Phaser.Physics.Arcade.Sprite; force: number }>;
        bombs: Array<{ sprite: Phaser.Physics.Arcade.Sprite; force: number }>;
      }
    ): void {
      gameState.tractorBeamCircle!.clear();

      if (isActive) {
        const time = scene.time.now;

        // Create pulsing/pulling effect with multiple circles
        for (let i = 0; i < tractorBeamVisuals.circles.count; i++) {
          const phase =
            (time / tractorBeamVisuals.circles.speed +
              i / tractorBeamVisuals.circles.count) %
            1;
          const radius = tractorBeamConfig.radius * (1 - phase);
          const alpha = tractorBeamVisuals.circles.baseAlpha * (1 - phase);

          gameState.tractorBeamCircle!.lineStyle(
            tractorBeamVisuals.circles.lineWidth,
            tractorBeamVisuals.circles.color,
            alpha
          );
          gameState.tractorBeamCircle!.strokeCircle(
            gameState.player!.x,
            gameState.player!.y,
            radius
          );
        }

        // Add particle-like dots in the field
        for (let i = 0; i < tractorBeamVisuals.particles.count; i++) {
          const angle =
            (time / tractorBeamVisuals.particles.rotationSpeed +
              i / tractorBeamVisuals.particles.count) *
            Math.PI *
            2;
          const spiralPhase =
            (time / tractorBeamVisuals.particles.spiralSpeed +
              i / tractorBeamVisuals.particles.count) %
            1;
          const particleRadius = tractorBeamConfig.radius * (1 - spiralPhase);
          const x = gameState.player!.x + Math.cos(angle) * particleRadius;
          const y = gameState.player!.y + Math.sin(angle) * particleRadius;

          gameState.tractorBeamCircle!.lineStyle(
            1,
            tractorBeamVisuals.particles.color,
            0
          );
          gameState.tractorBeamCircle!.fillStyle(
            tractorBeamVisuals.particles.color,
            tractorBeamVisuals.particles.baseAlpha * (1 - spiralPhase)
          );
          gameState.tractorBeamCircle!.fillCircle(
            x,
            y,
            tractorBeamVisuals.particles.size
          );
        }

        // Draw force lines with "flow" effect
        const drawForceLine = (obj: {
          sprite: Phaser.Physics.Arcade.Sprite;
          force: number;
        }) => {
          const thickness =
            (obj.force / tractorBeamConfig.strength) *
            tractorBeamVisuals.forceLines.maxThickness;

          // Draw main force line
          gameState.tractorBeamCircle!.lineStyle(
            thickness,
            tractorBeamVisuals.forceLines.color,
            tractorBeamVisuals.forceLines.baseAlpha
          );
          gameState.tractorBeamCircle!.beginPath();
          gameState.tractorBeamCircle!.moveTo(
            gameState.player!.x,
            gameState.player!.y
          );
          gameState.tractorBeamCircle!.lineTo(obj.sprite.x, obj.sprite.y);
          gameState.tractorBeamCircle!.strokePath();

          // Add flowing dots along the force line
          const dx = obj.sprite.x - gameState.player!.x;
          const dy = obj.sprite.y - gameState.player!.y;

          for (let i = 0; i < tractorBeamVisuals.forceLines.dots.count; i++) {
            const dotPhase =
              (time / tractorBeamVisuals.forceLines.dots.speed +
                i / tractorBeamVisuals.forceLines.dots.count) %
              1;
            const x = gameState.player!.x + dx * (1 - dotPhase);
            const y = gameState.player!.y + dy * (1 - dotPhase);

            gameState.tractorBeamCircle!.lineStyle(
              1,
              tractorBeamVisuals.forceLines.dots.color,
              0
            );
            gameState.tractorBeamCircle!.fillStyle(
              tractorBeamVisuals.forceLines.dots.color,
              tractorBeamVisuals.forceLines.dots.baseAlpha * (1 - dotPhase)
            );
            gameState.tractorBeamCircle!.fillCircle(x, y, thickness);
          }
        };

        // Draw lines for all affected objects
        [...affectedObjects.stars, ...affectedObjects.bombs].forEach(
          drawForceLine
        );

        // Update debug text
        gameState.debugText!.setVisible(true);
        gameState.debugText!.setText(
          `Tractor Beam Active\nAffecting ${affectedObjects.stars.length} stars\nAffecting ${affectedObjects.bombs.length} bombs`
        );
      } else {
        gameState.tractorBeamCircle!.clear();
        gameState.debugText!.setVisible(false);
      }
    }

    // Modified applyTractorBeamToGroup to return force information
    function applyTractorBeamToGroup(
      source: Phaser.Physics.Arcade.Sprite,
      group: Phaser.Physics.Arcade.Group
    ): Array<{ sprite: Phaser.Physics.Arcade.Sprite; force: number }> {
      const affectedObjects: Array<{
        sprite: Phaser.Physics.Arcade.Sprite;
        force: number;
      }> = [];

      group.children.iterate((child): boolean | null => {
        const sprite = child as Phaser.Physics.Arcade.Sprite;
        if (sprite.active && sprite.body) {
          const force = calculateTractorBeamForce(source, sprite);
          const forceMagnitude = Math.sqrt(
            force.x * force.x + force.y * force.y
          );

          if (forceMagnitude > 0) {
            affectedObjects.push({ sprite, force: forceMagnitude });
            sprite.setTint(0x00ff00); // Visual feedback on affected objects
            sprite.setVelocityX(sprite.body.velocity.x + force.x);
            sprite.setVelocityY(sprite.body.velocity.y + force.y);
          } else {
            sprite.clearTint(); // Remove tint when not affected
          }
        }
        return null;
      });

      return affectedObjects;
    }

    function update(this: Phaser.Scene) {
      if (gameState.gameOver) {
        if (gameState.spaceKey!.isDown) {
          restartGame.call(this);
        }
        return;
      }

      // Apply and visualize tractor beam when holding shift
      if (gameState.tractorBeamKey!.isDown) {
        const affectedObjects = {
          stars: applyTractorBeamToGroup(gameState.player!, gameState.stars!),
          bombs: applyTractorBeamToGroup(gameState.player!, gameState.bombs!),
        };
        updateTractorBeamVisuals(this, true, affectedObjects);
      } else {
        // Clear visuals when not active
        updateTractorBeamVisuals(this, false, { stars: [], bombs: [] });
        // Clear tints
        gameState.stars!.children.iterate((child) => {
          (child as Phaser.Physics.Arcade.Sprite).clearTint();
          return null;
        });
        gameState.bombs!.children.iterate((child) => {
          (child as Phaser.Physics.Arcade.Sprite).clearTint();
          return null;
        });
      }

      if (gameState.cursors!.left.isDown) {
        gameState.player!.setVelocityX(-160);
        gameState.player!.anims.play("left", true);
      } else if (gameState.cursors!.right.isDown) {
        gameState.player!.setVelocityX(160);
        gameState.player!.anims.play("right", true);
      } else {
        gameState.player!.setVelocityX(0);
        gameState.player!.anims.play("turn");
      }

      // Handle jumping mechanics with force decay
      if (
        gameState.cursors!.up.isDown &&
        gameState.player!.body?.touching.down
      ) {
        // Start new jump
        gameState.isJumping = true;
        gameState.currentJumpForce = MAX_JUMP_FORCE;
        gameState.player!.setVelocityY(JUMP_INITIAL_VELOCITY);
      } else if (gameState.cursors!.up.isDown && gameState.isJumping) {
        // Continue jump with decaying force
        if (gameState.currentJumpForce > MIN_JUMP_FORCE) {
          // Apply current force
          gameState.player!.setVelocityY(
            gameState.player!.body!.velocity.y -
              (gameState.currentJumpForce * this.game.loop.delta) / 1000
          );
          // Decay the force
          gameState.currentJumpForce *= JUMP_FORCE_DECAY;
        } else {
          // Force has decayed too much, end jump
          gameState.isJumping = false;
        }
      } else if (gameState.isJumping) {
        // Button released, end jump
        gameState.isJumping = false;
      }
    }

    return () => {
      game.destroy(true);
    };
  }, []);

  return <div id="game-container"></div>;
};

export default Game;
