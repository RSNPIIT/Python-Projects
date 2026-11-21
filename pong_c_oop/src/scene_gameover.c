/**
 * scene_gameover.c - Match Results and Post-Game Victory Screen.
 * Demonstrates GameScene polymorphism in C.
 */

#include "scene_gameover.h"
#include "scene_match.h"
#include "scene_menu.h"
#include "game.h"
#include "renderer.h"

static void GameOverScene_Enter(GameScene* base, struct GameApp* app) {
    (void)base;
    (void)app;
}

static void GameOverScene_HandleInput(GameScene* base, struct GameApp* app, int ch) {
    GameOverScene* self = (GameOverScene*)base;

    switch (ch) {
        case KEY_LEFT:
        case KEY_RIGHT:
        case KEY_UP:
        case KEY_DOWN:
        case '\t':
        case 'a':
        case 'A':
        case 'd':
        case 'D':
            self->selected_button = (self->selected_button == 0) ? 1 : 0;
            break;

        case 10:  /* ENTER */
        case 13:
        case ' ':
            if (self->selected_button == 0) {
                GameApp_SetScene(app, MatchScene_Create());
            } else {
                GameApp_SetScene(app, MenuScene_Create());
            }
            break;

        case 'q':
        case 'Q':
        case 27: /* ESC */
            GameApp_SetScene(app, MenuScene_Create());
            break;

        default:
            break;
    }
}

static void GameOverScene_Update(GameScene* base, struct GameApp* app, float dt) {
    GameOverScene* self = (GameOverScene*)base;
    (void)app;
    self->anim_timer += dt;
}

static void GameOverScene_Render(GameScene* base, struct GameApp* app) {
    GameOverScene* self = (GameOverScene*)base;

    /* 1. Render Court and Sidebar in dim/frozen state */
    Court_Render(&app->court);
    Renderer_DrawScoreboard(app->renderer, app);
    Renderer_DrawHUD(app->renderer, app);

    /* 2. Compute Centered Box Coordinates */
    int screen_w, screen_h;
    getmaxyx(stdscr, screen_h, screen_w);
    (void)screen_w;
    (void)screen_h;

    int bw = 46;
    int bh = 15;
    int bx = app->court.origin_x + (app->court.width - bw) / 2;
    int by = app->court.origin_y + (app->court.height - bh) / 2;
    if (by < 2) by = 2;

    /* Modal Frame */
    Renderer_DrawBox(app->renderer, bx, by, bw, bh, "MATCH COMPLETE", COLOR_PAIR_GOLD);

    /* Winner Title Banner */
    const char* winner_title = "✦ MATCH ENDED ✦";
    if (app->game_mode == GAME_MODE_SINGLEPLAYER) {
        winner_title = (self->winner_id == 1) ? "★ ★ PLAYER 1 VICTORIOUS! ★ ★" : "✦ CPU OPPONENT WINS! ✦";
    } else if (app->game_mode == GAME_MODE_SPECTATOR) {
        winner_title = (self->winner_id == 1) ? "★ CPU ALPHA TAKES THE CROWN! ★" : "★ CPU BETA TAKES THE CROWN! ★";
    } else {
        winner_title = (self->winner_id == 1) ? "★ ★ PLAYER 1 WINS THE SET! ★ ★" : "★ ★ PLAYER 2 WINS THE SET! ★ ★";
    }

    int title_color = (self->winner_id == 1) ? COLOR_PAIR_PLAYER1 : COLOR_PAIR_PLAYER2;
    attron(COLOR_PAIR(title_color) | A_BOLD);
    int title_x = bx + (bw - (int)strlen(winner_title)) / 2;
    mvprintw(by + 2, title_x, "%s", winner_title);
    attroff(COLOR_PAIR(title_color) | A_BOLD);

    /* Separator line */
    attron(COLOR_PAIR(COLOR_PAIR_COURT));
    for (int col = bx + 3; col < bx + bw - 3; col++) {
        mvaddch(by + 3, col, ACS_HLINE);
    }
    attroff(COLOR_PAIR(COLOR_PAIR_COURT));

    /* Match Statistics */
    int minutes = (int)self->match_duration / 60;
    int seconds = (int)self->match_duration % 60;
    int p1_score = app->player1 ? app->player1->score : 0;
    int p2_score = app->player2 ? app->player2->score : 0;
    int max_rally = app->ball ? app->ball->max_rally : 0;

    attron(COLOR_PAIR(COLOR_PAIR_HUD_ACCENT));
    mvprintw(by + 5, bx + 5, "Final Score :  P1 [%d]  vs  P2 [%d]", p1_score, p2_score);
    mvprintw(by + 6, bx + 5, "Match Time  :  %02d:%02d", minutes, seconds);
    mvprintw(by + 7, bx + 5, "Peak Rally  :  %d consecutive volleys", max_rally);

    const char* mode_name = "1P vs CPU";
    if (app->game_mode == GAME_MODE_MULTIPLAYER) mode_name = "2P Local";
    else if (app->game_mode == GAME_MODE_SPECTATOR) mode_name = "Spectator (AI vs AI)";
    else if (app->game_mode == GAME_MODE_PRACTICE) mode_name = "Solo Practice";
    mvprintw(by + 8, bx + 5, "Mode        :  %s", mode_name);
    attroff(COLOR_PAIR(COLOR_PAIR_HUD_ACCENT));

    /* Navigation Buttons */
    int btn_y = by + 11;
    const char* btn1 = "[ Play Again ]";
    const char* btn2 = "[ Main Menu ]";

    int btn1_x = bx + 6;
    int btn2_x = bx + 26;

    if (self->selected_button == 0) {
        attron(COLOR_PAIR(COLOR_PAIR_MENU_SELECTED) | A_BOLD);
        mvprintw(btn_y, btn1_x - 2, " >%s< ", btn1);
        attroff(COLOR_PAIR(COLOR_PAIR_MENU_SELECTED) | A_BOLD);

        attron(COLOR_PAIR(COLOR_PAIR_MENU_NORMAL));
        mvprintw(btn_y, btn2_x, "  %s  ", btn2);
        attroff(COLOR_PAIR(COLOR_PAIR_MENU_NORMAL));
    } else {
        attron(COLOR_PAIR(COLOR_PAIR_MENU_NORMAL));
        mvprintw(btn_y, btn1_x, "  %s  ", btn1);
        attroff(COLOR_PAIR(COLOR_PAIR_MENU_NORMAL));

        attron(COLOR_PAIR(COLOR_PAIR_MENU_SELECTED) | A_BOLD);
        mvprintw(btn_y, btn2_x - 2, " >%s< ", btn2);
        attroff(COLOR_PAIR(COLOR_PAIR_MENU_SELECTED) | A_BOLD);
    }

    /* Prompt Hint */
    attron(COLOR_PAIR(COLOR_PAIR_COURT));
    mvprintw(by + 13, bx + 6, "Press [ENTER] to confirm | [ARROWS] to pick");
    attroff(COLOR_PAIR(COLOR_PAIR_COURT));
}

static void GameOverScene_Exit(GameScene* base, struct GameApp* app) {
    (void)base;
    (void)app;
}

static void GameOverScene_Destroy(GameScene* base) {
    if (base) free(base);
}

static const GameSceneVTable GAMEOVER_SCENE_VTABLE = {
    .enter = GameOverScene_Enter,
    .handle_input = GameOverScene_HandleInput,
    .update = GameOverScene_Update,
    .render = GameOverScene_Render,
    .exit = GameOverScene_Exit,
    .destroy = GameOverScene_Destroy
};

GameScene* GameOverScene_Create(int winner_id, float match_duration) {
    GameOverScene* scene = (GameOverScene*)malloc(sizeof(GameOverScene));
    if (!scene) return NULL;
    scene->base.vtable = &GAMEOVER_SCENE_VTABLE;
    scene->winner_id = winner_id;
    scene->match_duration = match_duration;
    scene->selected_button = 0;
    scene->anim_timer = 0.0f;
    return (GameScene*)scene;
}
