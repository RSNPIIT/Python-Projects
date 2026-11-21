/**
 * court.c - Implementation of the Court Arena and Boundaries.
 */

#include "court.h"

void Court_Init(Court* self, int term_cols, int term_lines) {
    Court_Resize(self, term_cols, term_lines);
}

void Court_Resize(Court* self, int term_cols, int term_lines) {
    /* Determine ideal court size while leaving room for the HUD dashboard on the right */
    self->hud_width = 28;
    int available_w = term_cols - self->hud_width - 4;
    int available_h = term_lines - 4;

    /* Clamp to reasonable bounds */
    self->width = clampf(available_w, 40, 72);
    self->height = clampf(available_h, 16, 26);

    /* Center court + HUD horizontally and vertically */
    int total_width = self->width + 2 + self->hud_width;
    self->origin_x = maxf(1, (term_cols - total_width) / 2);
    self->origin_y = maxf(1, (term_lines - (self->height + 2)) / 2);

    self->hud_x = self->origin_x + self->width + 2 + 1;
}

float Court_ClampY(const Court* self, float y, float obj_height) {
    if (y < 0.0f) return 0.0f;
    if (y + obj_height > (float)self->height) {
        return (float)self->height - obj_height;
    }
    return y;
}

void Court_Render(const Court* self) {
    attron(COLOR_PAIR(COLOR_PAIR_COURT));

    int ox = self->origin_x;
    int oy = self->origin_y;
    int w = self->width;
    int h = self->height;

    /* Top and Bottom Horizontal Borders */
    for (int col = 0; col <= w + 1; col++) {
        mvaddch(oy, ox + col, ACS_HLINE);
        mvaddch(oy + h + 1, ox + col, ACS_HLINE);
    }

    /* Left and Right Vertical Goal Lines */
    for (int row = 0; row <= h + 1; row++) {
        mvaddch(oy + row, ox, ACS_VLINE);
        mvaddch(oy + row, ox + w + 1, ACS_VLINE);
    }

    /* Corners */
    mvaddch(oy, ox, ACS_ULCORNER);
    mvaddch(oy, ox + w + 1, ACS_URCORNER);
    mvaddch(oy + h + 1, ox, ACS_LLCORNER);
    mvaddch(oy + h + 1, ox + w + 1, ACS_LRCORNER);

    /* Center Net (Dashed line) */
    int center_x = ox + 1 + (w / 2);
    for (int row = 1; row <= h; row++) {
        if (row % 2 == 1) {
            mvaddch(oy + row, center_x, ':');
        }
    }

    attroff(COLOR_PAIR(COLOR_PAIR_COURT));
}
