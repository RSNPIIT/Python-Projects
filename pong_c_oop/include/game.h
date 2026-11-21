/**
 * game.h - Top-Level Game Application Coordinator.
 */

#ifndef GAME_H
#define GAME_H

#include "common.h"
#include "court.h"
#include "renderer.h"
#include "entity.h"
#include "paddle.h"
#include "ball.h"
#include "scene.h"

#define MAX_ENTITIES 8
#define KEY_BUFFER_SIZE 256

typedef struct GameApp {
    Renderer* renderer;
    Court court;

    /* Polymorphic Entity Array */
    Entity* entities[MAX_ENTITIES];
    int entity_count;

    Paddle* player1;
    Paddle* player2;
    Ball* ball;

    /* Scene State Machine */
    GameScene* current_scene;

    /* Match Configuration */
    GameMode game_mode;
    AIDifficulty ai_difficulty;
    int score_limit;
    int winner_id;

    /* Input State */
    bool keys[KEY_BUFFER_SIZE];
    int last_key;

    bool running;
    bool paused;
} GameApp;

/* Core Engine Functions */
GameApp* GameApp_Create(void);
void GameApp_Destroy(GameApp* self);
void GameApp_Run(GameApp* self);
void GameApp_SetScene(GameApp* self, GameScene* new_scene);
void GameApp_SetupMatch(GameApp* self);
void GameApp_OnScore(GameApp* self, int scoring_player);

bool GameApp_IsKeyPressed(const GameApp* self, int key);
const Ball* GameApp_GetBall(const GameApp* self);

#endif /* GAME_H */
