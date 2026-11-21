/**
 * renderer.h - Ncurses TUI Renderer & Double-Buffered Visual Presentation.
 */

#ifndef RENDERER_H
#define RENDERER_H

#include "common.h"

struct Court;
struct Paddle;
struct Ball;
struct GameApp;

typedef struct Renderer {
    WINDOW* win;
    int screen_w;
    int screen_h;
    bool has_colors;
} Renderer;

/* Constructor & Methods */
Renderer* Renderer_Create(void);
void Renderer_Destroy(Renderer* self);
void Renderer_Clear(Renderer* self);
void Renderer_Present(Renderer* self);
void Renderer_OnResize(Renderer* self, int* out_w, int* out_h);

/* Scene Drawing Primitives */
void Renderer_DrawPaddle(Renderer* self, const struct Paddle* paddle);
void Renderer_DrawBall(Renderer* self, const struct Ball* ball);
void Renderer_DrawScoreboard(Renderer* self, const struct GameApp* app);
void Renderer_DrawHUD(Renderer* self, const struct GameApp* app);
void Renderer_DrawBox(Renderer* self, int x, int y, int w, int h, const char* title, ColorPairId color);
void Renderer_TriggerBeep(Renderer* self, int pitch, int duration_ms);

#endif /* RENDERER_H */
