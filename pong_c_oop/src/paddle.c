/**
 * paddle.c - Paddle Class Implementation.
 */

#include "paddle.h"
#include "renderer.h"
#include "game.h"

static void Paddle_VirtualUpdate(Entity* base, float dt, struct GameApp* app) {
    Paddle* self = (Paddle*)base;

    /* Query injected controller strategy */
    int dir = 0;
    if (self->controller && self->controller->vtable && self->controller->vtable->get_direction) {
        dir = self->controller->vtable->get_direction(self->controller, app, self);
    }

    /* Update velocity and position */
    self->base.vel.y = (float)dir * self->speed;
    self->base.pos.y += self->base.vel.y * dt;

    /* Clamp inside court limits */
    self->base.pos.y = Court_ClampY(&app->court, self->base.pos.y, self->base.size.y);

    /* Update hit flash timer */
    if (self->hit_flash_timer > 0.0f) {
        self->hit_flash_timer -= dt;
    }
}

static void Paddle_VirtualRender(const Entity* base, struct Renderer* r) {
    const Paddle* self = (const Paddle*)base;
    Renderer_DrawPaddle(r, self);
}

static void Paddle_VirtualOnCollision(Entity* base, Entity* other, struct GameApp* app) {
    Paddle* self = (Paddle*)base;
    (void)other;
    (void)app;
    self->hit_flash_timer = 0.15f;
    self->consecutive_hits++;
}

static void Paddle_VirtualDestroy(Entity* base) {
    Paddle* self = (Paddle*)base;
    if (self->controller) {
        if (self->controller->vtable && self->controller->vtable->destroy) {
            self->controller->vtable->destroy(self->controller);
        }
        self->controller = NULL;
    }
    Entity_BaseDestroy(base);
    free(self);
}

/* Static Virtual Table for Paddle Class */
static const EntityVTable PADDLE_VTABLE = {
    .update = Paddle_VirtualUpdate,
    .render = Paddle_VirtualRender,
    .on_collision = Paddle_VirtualOnCollision,
    .destroy = Paddle_VirtualDestroy
};

Paddle* Paddle_Create(int player_id, float x, float y, float height, Controller* controller) {
    Paddle* p = (Paddle*)malloc(sizeof(Paddle));
    if (!p) return NULL;

    ColorPairId col = (player_id == 1) ? COLOR_PAIR_PLAYER1 : COLOR_PAIR_PLAYER2;
    Entity_Init(&p->base, &PADDLE_VTABLE, "Paddle", vec2(x, y), vec2(1.0f, height), col);

    p->player_id = player_id;
    p->speed = 22.0f; /* Responsive speed in character cells/sec */
    p->score = 0;
    p->controller = controller;
    p->hit_flash_timer = 0.0f;
    p->consecutive_hits = 0;

    return p;
}

void Paddle_SetController(Paddle* self, Controller* new_controller) {
    if (!self) return;
    if (self->controller && self->controller->vtable && self->controller->vtable->destroy) {
        self->controller->vtable->destroy(self->controller);
    }
    self->controller = new_controller;
}

void Paddle_Reset(Paddle* self, float y) {
    if (!self) return;
    self->base.pos.y = y;
    self->base.vel = vec2(0.0f, 0.0f);
    self->hit_flash_timer = 0.0f;
    self->consecutive_hits = 0;
}

void Paddle_AddScore(Paddle* self, int points) {
    if (!self) return;
    self->score += points;
}
