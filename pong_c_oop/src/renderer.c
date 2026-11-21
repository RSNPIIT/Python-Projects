/**
 * renderer.c - Ncurses Presentation Implementation.
 */

#include "renderer.h"
#include "paddle.h"
#include "ball.h"
#include "game.h"

Renderer* Renderer_Create(void) {
    Renderer* r = (Renderer*)malloc(sizeof(Renderer));
    if (!r) return NULL;

    r->win = initscr();
    cbreak();
    noecho();
    keypad(stdscr, TRUE);
    nodelay(stdscr, TRUE);
    curs_set(0);

    getmaxyx(stdscr, r->screen_h, r->screen_w);
    r->has_colors = has_colors();

    if (r->has_colors) {
        start_color();
        use_default_colors();

        init_pair(COLOR_PAIR_DEFAULT,       COLOR_WHITE,   -1);
        init_pair(COLOR_PAIR_COURT,         COLOR_GREEN,   -1);
        init_pair(COLOR_PAIR_PLAYER1,       COLOR_CYAN,    -1);
        init_pair(COLOR_PAIR_PLAYER2,       COLOR_MAGENTA, -1);
        init_pair(COLOR_PAIR_BALL,          COLOR_YELLOW,  -1);
        init_pair(COLOR_PAIR_BALL_FAST,     COLOR_RED,     -1);
        init_pair(COLOR_PAIR_SCORE,         COLOR_WHITE,   -1);
        init_pair(COLOR_PAIR_HUD_TITLE,     COLOR_CYAN,    -1);
        init_pair(COLOR_PAIR_HUD_ACCENT,    COLOR_YELLOW,  -1);
        init_pair(COLOR_PAIR_MENU_SELECTED, COLOR_BLACK,   COLOR_CYAN);
        init_pair(COLOR_PAIR_MENU_NORMAL,   COLOR_WHITE,   -1);
        init_pair(COLOR_PAIR_GOLD,          COLOR_YELLOW,  -1);
        init_pair(COLOR_PAIR_TRAIL,         COLOR_BLUE,    -1);
    }

    return r;
}

void Renderer_Destroy(Renderer* self) {
    if (!self) return;
    endwin();
    free(self);
}

void Renderer_Clear(Renderer* self) {
    (void)self;
    erase();
}

void Renderer_Present(Renderer* self) {
    (void)self;
    refresh();
}

void Renderer_OnResize(Renderer* self, int* out_w, int* out_h) {
    getmaxyx(stdscr, self->screen_h, self->screen_w);
    if (out_w) *out_w = self->screen_w;
    if (out_h) *out_h = self->screen_h;
}

void Renderer_DrawBox(Renderer* self, int x, int y, int w, int h, const char* title, ColorPairId color) {
    (void)self;
    attron(COLOR_PAIR(color));

    /* Horizontal lines */
    for (int col = 0; col < w; col++) {
        mvaddch(y, x + col, ACS_HLINE);
        mvaddch(y + h - 1, x + col, ACS_HLINE);
    }
    /* Vertical lines */
    for (int row = 0; row < h; row++) {
        mvaddch(y + row, x, ACS_VLINE);
        mvaddch(y + row, x + w - 1, ACS_VLINE);
    }
    /* Corners */
    mvaddch(y, x, ACS_ULCORNER);
    mvaddch(y, x + w - 1, ACS_URCORNER);
    mvaddch(y + h - 1, x, ACS_LLCORNER);
    mvaddch(y + h - 1, x + w - 1, ACS_LRCORNER);

    /* Optional Title */
    if (title && strlen(title) > 0) {
        int title_len = (int)strlen(title);
        int tx = x + (w - title_len - 2) / 2;
        if (tx > x && tx + title_len + 1 < x + w) {
            mvprintw(y, tx, " %s ", title);
        }
    }

    attroff(COLOR_PAIR(color));
}

void Renderer_DrawPaddle(Renderer* self, const struct Paddle* paddle) {
    (void)self;
    if (!paddle) return;

    int ox = paddle->base.pos.x;
    int oy = paddle->base.pos.y;
    int height = (int)paddle->base.size.y;

    ColorPairId col = paddle->base.color;
    if (paddle->hit_flash_timer > 0.0f) {
        attron(A_REVERSE | A_BOLD);
    }
    attron(COLOR_PAIR(col) | A_BOLD);

    for (int i = 0; i < height; i++) {
        char ch = (paddle->player_id == 1) ? ']' : '[';
        mvaddch(oy + i, ox, ch);
    }

    attroff(COLOR_PAIR(col) | A_BOLD);
    if (paddle->hit_flash_timer > 0.0f) {
        attroff(A_REVERSE | A_BOLD);
    }
}

void Renderer_DrawBall(Renderer* self, const struct Ball* ball) {
    (void)self;
    if (!ball) return;

    /* Render motion trail */
    attron(COLOR_PAIR(COLOR_PAIR_TRAIL) | A_DIM);
    for (int i = 1; i < ball->trail_count; i++) {
        int tx = (int)roundf(ball->trail[i].x);
        int ty = (int)roundf(ball->trail[i].y);
        char trail_ch = (i < 3) ? '*' : '.';
        mvaddch(ty, tx, trail_ch);
    }
    attroff(COLOR_PAIR(COLOR_PAIR_TRAIL) | A_DIM);

    /* Render Ball Core */
    int bx = (int)roundf(ball->base.pos.x);
    int by = (int)roundf(ball->base.pos.y);

    attron(COLOR_PAIR(ball->base.color) | A_BOLD);
    char ball_ch = (ball->current_speed > 36.0f) ? '@' : 'O';
    mvaddch(by, bx, ball_ch);
    attroff(COLOR_PAIR(ball->base.color) | A_BOLD);
}

void Renderer_DrawScoreboard(Renderer* self, const struct GameApp* app) {
    (void)self;
    int cx = app->court.origin_x + (app->court.width / 2);
    int cy = app->court.origin_y - 1;
    if (cy < 0) cy = 0;

    /* Score banner */
    attron(COLOR_PAIR(COLOR_PAIR_SCORE) | A_BOLD);
    mvprintw(cy, cx - 10, "  %02d   |   %02d  ", app->player1->score, app->player2->score);
    attroff(COLOR_PAIR(COLOR_PAIR_SCORE) | A_BOLD);

    /* Player tags below score */
    attron(COLOR_PAIR(COLOR_PAIR_PLAYER1));
    mvprintw(cy, cx - 18, "PLAYER 1");
    attroff(COLOR_PAIR(COLOR_PAIR_PLAYER1));

    attron(COLOR_PAIR(COLOR_PAIR_PLAYER2));
    const char* p2_label = (app->game_mode == GAME_MODE_MULTIPLAYER) ? "PLAYER 2" : "CPU AI";
    mvprintw(cy, cx + 11, "%s", p2_label);
    attroff(COLOR_PAIR(COLOR_PAIR_PLAYER2));
}

void Renderer_DrawHUD(Renderer* self, const struct GameApp* app) {
    int hx = app->court.hud_x;
    int hy = app->court.origin_y;
    int hw = app->court.hud_width;
    int hh = app->court.height + 2;

    /* Outer HUD Glassmorphic Border */
    Renderer_DrawBox(self, hx, hy, hw, hh, "TELEMETRY", COLOR_PAIR_HUD_TITLE);

    int row = hy + 2;

    /* Match Info */
    attron(COLOR_PAIR(COLOR_PAIR_HUD_TITLE) | A_BOLD);
    mvprintw(row++, hx + 2, "=== P O N G   O O P ===");
    attroff(COLOR_PAIR(COLOR_PAIR_HUD_TITLE) | A_BOLD);
    row++;

    /* Mode & Target */
    const char* mode_names[] = { "1P vs CPU", "2P Local PvP", "CPU Spectator", "Solo Practice" };
    mvprintw(row++, hx + 2, "Mode     : %s", mode_names[app->game_mode]);
    mvprintw(row++, hx + 2, "Goal     : First to %d", app->score_limit);

    if (app->game_mode != GAME_MODE_MULTIPLAYER) {
        const char* diff_names[] = { "Casual", "Pro", "Master", "Unbeatable" };
        mvprintw(row++, hx + 2, "CPU Rank : %s", diff_names[app->ai_difficulty]);
    }
    row++;

    /* Live Ball Telemetry */
    attron(COLOR_PAIR(COLOR_PAIR_HUD_ACCENT) | A_BOLD);
    mvprintw(row++, hx + 2, "BALL METRICS:");
    attroff(COLOR_PAIR(COLOR_PAIR_HUD_ACCENT) | A_BOLD);

    float spd = Ball_GetSpeed(app->ball);
    mvprintw(row++, hx + 2, "Velocity : %.1f u/s", spd);
    mvprintw(row++, hx + 2, "Rally    : %02d hits", app->ball->rally_count);
    mvprintw(row++, hx + 2, "Max Rally: %02d hits", app->ball->max_rally);

    /* Angle deflection visualization */
    float ang_deg = atan2f(app->ball->base.vel.y, app->ball->base.vel.x) * (180.0f / M_PI);
    mvprintw(row++, hx + 2, "Deflect  : %+.1f deg", ang_deg);
    row++;

    /* Speed gauge meter bar */
    mvprintw(row++, hx + 2, "Speed Gauge:");
    int gauge_w = hw - 6;
    float pct = clampf((spd - app->ball->base_speed) / (app->ball->max_speed - app->ball->base_speed), 0.0f, 1.0f);
    int filled = (int)(pct * gauge_w);

    mvaddch(row, hx + 2, '[');
    for (int i = 0; i < gauge_w; i++) {
        if (i < filled) {
            attron(COLOR_PAIR(COLOR_PAIR_BALL_FAST) | A_BOLD);
            mvaddch(row, hx + 3 + i, '=');
            attroff(COLOR_PAIR(COLOR_PAIR_BALL_FAST) | A_BOLD);
        } else {
            attron(A_DIM);
            mvaddch(row, hx + 3 + i, '-');
            attroff(A_DIM);
        }
    }
    mvaddch(row++, hx + 3 + gauge_w, ']');
    row += 2;

    /* Controls Guide */
    attron(COLOR_PAIR(COLOR_PAIR_HUD_TITLE) | A_BOLD);
    mvprintw(row++, hx + 2, "CONTROLS:");
    attroff(COLOR_PAIR(COLOR_PAIR_HUD_TITLE) | A_BOLD);

    if (app->game_mode == GAME_MODE_MULTIPLAYER) {
        mvprintw(row++, hx + 2, "P1: W / S");
        mvprintw(row++, hx + 2, "P2: UP / DOWN");
    } else {
        mvprintw(row++, hx + 2, "Move  : UP / DOWN / W / S");
    }
    mvprintw(row++, hx + 2, "Pause : ESC / P");
    mvprintw(row++, hx + 2, "Reset : R");
}

void Renderer_TriggerBeep(Renderer* self, int pitch, int duration_ms) {
    (void)self;
    (void)pitch;
    (void)duration_ms;
    /* Flash terminal bell */
    beep();
}
