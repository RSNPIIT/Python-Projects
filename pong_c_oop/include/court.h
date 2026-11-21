/**
 * court.h - Tennis Court Geometry and Responsive Terminal Boundary Manager.
 */

#ifndef COURT_H
#define COURT_H

#include "common.h"

typedef struct Court {
    int origin_x;   /* Screen X where court starts */
    int origin_y;   /* Screen Y where court starts */
    int width;      /* Internal court width (columns) */
    int height;     /* Internal court height (rows) */
    int hud_width;  /* Width of sidebar dashboard */
    int hud_x;      /* Screen X where HUD begins */
} Court;

/* Constructor & Methods */
void Court_Init(Court* self, int term_cols, int term_lines);
void Court_Resize(Court* self, int term_cols, int term_lines);
void Court_Render(const Court* self);
float Court_ClampY(const Court* self, float y, float obj_height);

#endif /* COURT_H */
