/**
 * scene_menu.c - Interactive Main Menu Scene Implementation.
 */

#include "scene_menu.h"
#include "scene_match.h"
#include "game.h"
#include "renderer.h"

#define MENU_ITEM_COUNT 5

static void MenuScene_Enter(GameScene* base, struct GameApp* app) {
    (void)base;
    (void)app;
}

static void MenuScene_HandleInput(GameScene* base, struct GameApp* app, int ch) {
    MenuScene* self = (MenuScene*)base;

    switch (ch) {
        case KEY_UP:
        case 'w':
        case 'W':
            self->selected_item = (self->selected_item - 1 + MENU_ITEM_COUNT) % MENU_ITEM_COUNT;
            break;

        case KEY_DOWN:
        case 's':
        case 'S':
            self->selected_item = (self->selected_item + 1) % MENU_ITEM_COUNT;
            break;

        case KEY_LEFT:
        case 'a':
        case 'A':
            if (self->selected_item == 0) {
                app->game_mode = (GameMode)((app->game_mode - 1 + 4) % 4);
            } else if (self->selected_item == 1) {
                app->ai_difficulty = (AIDifficulty)((app->ai_difficulty - 1 + 4) % 4);
            } else if (self->selected_item == 2) {
                if (app->score_limit == 21) app->score_limit = 10;
                else if (app->score_limit == 10) app->score_limit = 5;
                else app->score_limit = 21;
            }
            break;

        case KEY_RIGHT:
        case 'd':
        case 'D':
            if (self->selected_item == 0) {
                app->game_mode = (GameMode)((app->game_mode + 1) % 4);
            } else if (self->selected_item == 1) {
                app->ai_difficulty = (AIDifficulty)((app->ai_difficulty + 1) % 4);
            } else if (self->selected_item == 2) {
                if (app->score_limit == 5) app->score_limit = 10;
                else if (app->score_limit == 10) app->score_limit = 21;
                else app->score_limit = 5;
            }
            break;

        case 10: /* Enter */
        case 13:
        case ' ':
            if (self->selected_item == 3) {
                /* Launch Match Scene */
                GameApp_SetScene(app, MatchScene_Create());
            } else if (self->selected_item == 4) {
                app->running = false;
            }
            break;

        case 'q':
        case 'Q':
        case 27: /* Esc */
            app->running = false;
            break;
    }
}

static void MenuScene_Update(GameScene* base, struct GameApp* app, float dt) {
    MenuScene* self = (MenuScene*)base;
    (void)app;
    self->anim_pulse += dt * 3.0f;
}

static void MenuScene_Render(GameScene* base, struct GameApp* app) {
    MenuScene* self = (MenuScene*)base;

    int sw = app->renderer->screen_w;
    int sh = app->renderer->screen_h;

    int box_w = 48;
    int box_h = 20;
    int box_x = (sw - box_w) / 2;
    int box_y = (sh - box_h) / 2;

    Renderer_DrawBox(app->renderer, box_x, box_y, box_w, box_h, "PONG OOP // C EDITION", COLOR_PAIR_HUD_TITLE);

    /* Retro Header Banner */
    attron(COLOR_PAIR(COLOR_PAIR_GOLD) | A_BOLD);
    mvprintw(box_y + 2, box_x + (box_w - 24) / 2, "=== P O N G   O O P ===");
    attroff(COLOR_PAIR(COLOR_PAIR_GOLD) | A_BOLD);

    attron(COLOR_PAIR(COLOR_PAIR_COURT));
    mvprintw(box_y + 3, box_x + (box_w - 38) / 2, "Object-Oriented Architecture in Pure C");
    attroff(COLOR_PAIR(COLOR_PAIR_COURT));

    /* Menu Rows */
    const char* mode_labels[] = { "< 1P vs CPU >", "< 2P Local PvP >", "< CPU vs CPU >", "< Solo Practice >" };
    const char* diff_labels[] = { "< Casual >", "< Pro >", "< Master >", "< Unbeatable >" };
    char limit_str[32];
    snprintf(limit_str, sizeof(limit_str), "< First to %d >", app->score_limit);

    const char* items[MENU_ITEM_COUNT];
    char item0[64], item1[64], item2[64];
    snprintf(item0, sizeof(item0), "Game Mode   : %-18s", mode_labels[app->game_mode]);
    snprintf(item1, sizeof(item1), "Difficulty  : %-18s", diff_labels[app->ai_difficulty]);
    snprintf(item2, sizeof(item2), "Score Limit : %-18s", limit_str);

    items[0] = item0;
    items[1] = item1;
    items[2] = item2;
    items[3] = "[ START MATCH ]";
    items[4] = "[ QUIT TO DESKTOP ]";

    for (int i = 0; i < MENU_ITEM_COUNT; i++) {
        int row_y = box_y + 6 + (i * 2) + (i >= 3 ? 1 : 0);
        bool is_sel = (self->selected_item == i);

        if (is_sel) {
            attron(COLOR_PAIR(COLOR_PAIR_MENU_SELECTED) | A_BOLD);
            mvprintw(row_y, box_x + 5, " > %-36s < ", items[i]);
            attroff(COLOR_PAIR(COLOR_PAIR_MENU_SELECTED) | A_BOLD);
        } else {
            attron(COLOR_PAIR(COLOR_PAIR_MENU_NORMAL));
            mvprintw(row_y, box_x + 7, "%-36s", items[i]);
            attroff(COLOR_PAIR(COLOR_PAIR_MENU_NORMAL));
        }
    }

    /* Help & Navigation Tips */
    attron(A_DIM);
    mvprintw(box_y + box_h - 3, box_x + (box_w - 36) / 2, "UP/DOWN: Navigate  LEFT/RIGHT: Change");
    mvprintw(box_y + box_h - 2, box_x + (box_w - 28) / 2, "ENTER: Select   Q: Quit");
    attroff(A_DIM);
}

static void MenuScene_Exit(GameScene* base, struct GameApp* app) {
    (void)base;
    (void)app;
}

static void MenuScene_Destroy(GameScene* base) {
    if (base) free(base);
}

static const GameSceneVTable MENU_SCENE_VTABLE = {
    .enter = MenuScene_Enter,
    .handle_input = MenuScene_HandleInput,
    .update = MenuScene_Update,
    .render = MenuScene_Render,
    .exit = MenuScene_Exit,
    .destroy = MenuScene_Destroy
};

GameScene* MenuScene_Create(void) {
    MenuScene* scene = (MenuScene*)malloc(sizeof(MenuScene));
    if (!scene) return NULL;
    scene->base.vtable = &MENU_SCENE_VTABLE;
    scene->selected_item = 3; /* Default focused on START MATCH */
    scene->anim_pulse = 0.0f;
    return (GameScene*)scene;
}
