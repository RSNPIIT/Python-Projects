/**
 * scene_match.c - Active Match Scene Implementation.
 * Demonstrates Polymorphic Entity Processing and Collision Dispatch in Pure C.
 */

#include "scene_match.h"
#include "scene_menu.h"
#include "scene_gameover.h"
#include "game.h"
#include "renderer.h"

static void MatchScene_Enter(GameScene* base, struct GameApp* app) {
    MatchScene* self = (MatchScene*)base;
    self->paused = false;
    self->pause_selected = 0;
    self->match_timer = 0.0f;

    /* Initialize paddles and ball for this match */
    GameApp_SetupMatch(app);
}

static void MatchScene_HandleInput(GameScene* base, struct GameApp* app, int ch) {
    MatchScene* self = (MatchScene*)base;

    if (self->paused) {
        switch (ch) {
            case KEY_UP:
            case 'w':
            case 'W':
                self->pause_selected = (self->pause_selected - 1 + 3) % 3;
                break;

            case KEY_DOWN:
            case 's':
            case 'S':
                self->pause_selected = (self->pause_selected + 1) % 3;
                break;

            case 10: /* Enter */
            case 13:
            case ' ':
                if (self->pause_selected == 0) {
                    self->paused = false; /* Resume */
                } else if (self->pause_selected == 1) {
                    GameApp_SetupMatch(app); /* Restart match */
                    self->paused = false;
                } else if (self->pause_selected == 2) {
                    GameApp_SetScene(app, MenuScene_Create()); /* Back to Menu */
                }
                break;

            case 27: /* Esc */
            case 'p':
            case 'P':
                self->paused = false;
                break;
        }
        return;
    }

    /* Gameplay Hotkeys */
    if (ch == 27 || ch == 'p' || ch == 'P') {
        self->paused = true;
        self->pause_selected = 0;
    } else if (ch == 'r' || ch == 'R') {
        GameApp_SetupMatch(app);
    }
}

static void MatchScene_Update(GameScene* base, struct GameApp* app, float dt) {
    MatchScene* self = (MatchScene*)base;
    if (self->paused) return;

    self->match_timer += dt;

    /* 1. POLYMORPHIC ENTITY UPDATE LOOP:
     * Iterates through any entity (Paddles, Ball) calling its virtual update function! */
    for (int i = 0; i < app->entity_count; i++) {
        Entity* e = app->entities[i];
        if (e && e->active) {
            Entity_Update(e, dt, app);
        }
    }

    /* 2. BROAD-PHASE / NARROW-PHASE AABB COLLISION DETECTION:
     * Check Ball against each Paddle polymorphically */
    Ball* ball = app->ball;
    if (ball && ball->base.active) {
        Rect ball_box = Entity_GetBounds(&ball->base);

        for (int i = 0; i < app->entity_count; i++) {
            Entity* other = app->entities[i];
            if (other && other->active && (Entity*)ball != other) {
                Rect other_box = Entity_GetBounds(other);
                if (rect_intersects(ball_box, other_box)) {
                    /* Dynamic Polymorphic Dispatch on collision! */
                    Entity_OnCollision((Entity*)ball, other, app);
                    Entity_OnCollision(other, (Entity*)ball, app);
                }
            }
        }
    }

    /* 3. CHECK VICTORY CONDITION */
    if (app->player1->score >= app->score_limit) {
        app->winner_id = 1;
        GameApp_SetScene(app, GameOverScene_Create(1, self->match_timer));
    } else if (app->player2->score >= app->score_limit) {
        app->winner_id = 2;
        GameApp_SetScene(app, GameOverScene_Create(2, self->match_timer));
    }
}

static void MatchScene_Render(GameScene* base, struct GameApp* app) {
    MatchScene* self = (MatchScene*)base;

    /* 1. Render Court and Net */
    Court_Render(&app->court);

    /* 2. Render Scoreboard and HUD */
    Renderer_DrawScoreboard(app->renderer, app);
    Renderer_DrawHUD(app->renderer, app);

    /* 3. POLYMORPHIC ENTITY RENDER LOOP:
     * Iterates through all entities and invokes their custom virtual render implementations! */
    for (int i = 0; i < app->entity_count; i++) {
        Entity* e = app->entities[i];
        if (e && e->active) {
            Entity_Render(e, app->renderer);
        }
    }

    /* 4. Render Pause Modal if active */
    if (self->paused) {
        int cx = app->court.origin_x + (app->court.width / 2);
        int cy = app->court.origin_y + (app->court.height / 2);
        int pw = 28;
        int ph = 10;
        int px = cx - (pw / 2);
        int py = cy - (ph / 2);

        Renderer_DrawBox(app->renderer, px, py, pw, ph, "MATCH PAUSED", COLOR_PAIR_HUD_TITLE);

        const char* opts[] = { "Resume Game", "Restart Match", "Quit to Menu" };
        for (int i = 0; i < 3; i++) {
            if (self->pause_selected == i) {
                attron(COLOR_PAIR(COLOR_PAIR_MENU_SELECTED) | A_BOLD);
                mvprintw(py + 3 + i * 2, px + 4, " > %-16s < ", opts[i]);
                attroff(COLOR_PAIR(COLOR_PAIR_MENU_SELECTED) | A_BOLD);
            } else {
                attron(COLOR_PAIR(COLOR_PAIR_MENU_NORMAL));
                mvprintw(py + 3 + i * 2, px + 6, "%-16s", opts[i]);
                attroff(COLOR_PAIR(COLOR_PAIR_MENU_NORMAL));
            }
        }
    }
}

static void MatchScene_Exit(GameScene* base, struct GameApp* app) {
    (void)base;
    (void)app;
}

static void MatchScene_Destroy(GameScene* base) {
    if (base) free(base);
}

static const GameSceneVTable MATCH_SCENE_VTABLE = {
    .enter = MatchScene_Enter,
    .handle_input = MatchScene_HandleInput,
    .update = MatchScene_Update,
    .render = MatchScene_Render,
    .exit = MatchScene_Exit,
    .destroy = MatchScene_Destroy
};

GameScene* MatchScene_Create(void) {
    MatchScene* scene = (MatchScene*)malloc(sizeof(MatchScene));
    if (!scene) return NULL;
    scene->base.vtable = &MATCH_SCENE_VTABLE;
    scene->paused = false;
    scene->pause_selected = 0;
    scene->match_timer = 0.0f;
    return (GameScene*)scene;
}
