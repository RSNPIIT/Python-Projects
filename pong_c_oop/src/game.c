/**
 * game.c - Top-Level Game Application Coordinator.
 * Manages the high-precision 60 FPS clock, entity lifecycle,
 * scene state machine, and polymorphic subsystem dispatch.
 */

#define _POSIX_C_SOURCE 199309L
#include "game.h"
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#define TARGET_FPS 60.0f
#define FRAME_TIME_USEC ((useconds_t)(1000000.0f / TARGET_FPS))

static uint64_t get_time_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
}

GameApp* GameApp_Create(void) {
    GameApp* self = (GameApp*)calloc(1, sizeof(GameApp));
    if (!self) return NULL;

    /* Initialize Renderer and Terminal */
    self->renderer = Renderer_Create();
    if (!self->renderer) {
        free(self);
        return NULL;
    }

    /* Initialize Court Geometry */
    Court_Init(&self->court, self->renderer->screen_w, self->renderer->screen_h);

    /* Match Defaults */
    self->game_mode = GAME_MODE_SINGLEPLAYER;
    self->ai_difficulty = AI_MEDIUM;
    self->score_limit = 7;
    self->winner_id = 0;
    self->running = true;
    self->paused = false;
    self->last_key = ERR;

    return self;
}

void GameApp_Destroy(GameApp* self) {
    if (!self) return;

    /* Destroy Current Active Scene */
    if (self->current_scene) {
        GameScene_Exit(self->current_scene, self);
        GameScene_Destroy(self->current_scene);
        self->current_scene = NULL;
    }

    /* Destroy Polymorphic Entities */
    for (int i = 0; i < self->entity_count; i++) {
        if (self->entities[i]) {
            Entity_Destroy(self->entities[i]);
            self->entities[i] = NULL;
        }
    }
    self->entity_count = 0;
    self->player1 = NULL;
    self->player2 = NULL;
    self->ball = NULL;

    /* Destroy Renderer */
    if (self->renderer) {
        Renderer_Destroy(self->renderer);
        self->renderer = NULL;
    }

    free(self);
}

void GameApp_SetScene(GameApp* self, GameScene* new_scene) {
    if (!self) return;

    if (self->current_scene) {
        GameScene_Exit(self->current_scene, self);
        GameScene_Destroy(self->current_scene);
    }

    self->current_scene = new_scene;

    if (self->current_scene) {
        GameScene_Enter(self->current_scene, self);
    }
}

void GameApp_SetupMatch(GameApp* self) {
    if (!self) return;

    /* 1. Tear down previous match entities */
    for (int i = 0; i < self->entity_count; i++) {
        if (self->entities[i]) {
            Entity_Destroy(self->entities[i]);
            self->entities[i] = NULL;
        }
    }
    self->entity_count = 0;
    self->player1 = NULL;
    self->player2 = NULL;
    self->ball = NULL;
    self->winner_id = 0;

    /* 2. Configure Controllers via Strategy Pattern */
    Controller* p1_ctrl = NULL;
    Controller* p2_ctrl = NULL;

    switch (self->game_mode) {
        case GAME_MODE_SINGLEPLAYER:
            /* Player 1 Human, Player 2 AI */
            p1_ctrl = HumanController_Create('w', 's', KEY_UP, KEY_DOWN);
            p2_ctrl = AIController_Create(self->ai_difficulty);
            break;

        case GAME_MODE_MULTIPLAYER:
            /* Player 1 W/S, Player 2 Up/Down */
            p1_ctrl = HumanController_Create('w', 's', 'W', 'S');
            p2_ctrl = HumanController_Create(KEY_UP, KEY_DOWN, 'k', 'm');
            break;

        case GAME_MODE_SPECTATOR:
            /* Both AI (Attract mode) */
            p1_ctrl = AIController_Create(self->ai_difficulty);
            p2_ctrl = AIController_Create(self->ai_difficulty);
            break;

        case GAME_MODE_PRACTICE:
            /* Player 1 Human, Player 2 Unbeatable AI Wall */
            p1_ctrl = HumanController_Create('w', 's', KEY_UP, KEY_DOWN);
            p2_ctrl = AIController_Create(AI_UNBEATABLE);
            break;
    }

    /* 3. Instantiate Derived Entity Classes (Paddle, Ball) */
    float court_w = (float)self->court.width;
    float court_h = (float)self->court.height;
    float paddle_h = 5.0f;
    if (paddle_h > court_h - 2.0f) paddle_h = court_h - 2.0f;

    self->player1 = Paddle_Create(1, 2.0f, (court_h - paddle_h) / 2.0f, paddle_h, p1_ctrl);
    self->player2 = Paddle_Create(2, court_w - 3.0f, (court_h - paddle_h) / 2.0f, paddle_h, p2_ctrl);
    self->ball = Ball_Create(court_w / 2.0f, court_h / 2.0f);

    /* 4. Register in Polymorphic Entity Array */
    self->entities[0] = (Entity*)self->player1;
    self->entities[1] = (Entity*)self->player2;
    self->entities[2] = (Entity*)self->ball;
    self->entity_count = 3;

    /* 5. Serve Initial Ball */
    int serve_dir = (rand() % 2 == 0) ? 1 : -1;
    Ball_Serve(self->ball, serve_dir, court_h / 2.0f);
}

void GameApp_OnScore(GameApp* self, int scoring_player) {
    if (!self || !self->ball) return;

    if (scoring_player == 1) {
        if (self->player1) Paddle_AddScore(self->player1, 1);
        Renderer_TriggerBeep(self->renderer, 880, 80);
        Ball_Serve(self->ball, 1, (float)self->court.height / 2.0f);
    } else if (scoring_player == 2) {
        if (self->player2) Paddle_AddScore(self->player2, 1);
        Renderer_TriggerBeep(self->renderer, 440, 80);
        Ball_Serve(self->ball, -1, (float)self->court.height / 2.0f);
    }
}

bool GameApp_IsKeyPressed(const GameApp* self, int key) {
    if (!self) return false;
    if (key >= 0 && key < KEY_BUFFER_SIZE && self->keys[key]) {
        return true;
    }
    return (self->last_key == key);
}

const Ball* GameApp_GetBall(const GameApp* self) {
    return self ? self->ball : NULL;
}

void GameApp_Run(GameApp* self) {
    if (!self || !self->renderer) return;

    uint64_t prev_time = get_time_ns();

    while (self->running) {
        uint64_t frame_start = get_time_ns();
        float dt = (float)(frame_start - prev_time) / 1000000000.0f;
        prev_time = frame_start;

        /* Clamp dt to avoid physics spiral on suspension/lag */
        if (dt > 0.05f) dt = 0.05f;
        if (dt <= 0.0f) dt = 0.001f;

        /* 1. Poll Terminal Input */
        int ch = wgetch(self->renderer->win);
        memset(self->keys, 0, sizeof(self->keys));

        if (ch != ERR) {
            self->last_key = ch;
            if (ch >= 0 && ch < KEY_BUFFER_SIZE) {
                self->keys[ch] = true;
            }

            /* Terminal Window Resize Event */
            if (ch == KEY_RESIZE) {
                int new_w, new_h;
                Renderer_OnResize(self->renderer, &new_w, &new_h);
                Court_Resize(&self->court, new_w, new_h);
            }
        } else {
            self->last_key = ERR;
        }

        /* 2. Scene Input Handling */
        if (self->current_scene) {
            GameScene_HandleInput(self->current_scene, self, ch);
        }

        /* 3. Scene Simulation Update */
        if (self->current_scene) {
            GameScene_Update(self->current_scene, self, dt);
        }

        /* 4. Render Phase */
        Renderer_Clear(self->renderer);

        if (self->current_scene) {
            GameScene_Render(self->current_scene, self);
        }

        Renderer_Present(self->renderer);

        /* 5. Precise Frame Rate Limiter (~60 FPS) */
        uint64_t frame_end = get_time_ns();
        uint64_t elapsed_usec = (frame_end - frame_start) / 1000ULL;
        if (elapsed_usec < FRAME_TIME_USEC) {
            usleep((useconds_t)(FRAME_TIME_USEC - elapsed_usec));
        }
    }
}
