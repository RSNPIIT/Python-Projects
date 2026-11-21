/**
 * ball.c - Ball Class Implementation.
 */

#include "ball.h"
#include "paddle.h"
#include "renderer.h"
#include "game.h"

static void Ball_VirtualUpdate(Entity* base, float dt, struct GameApp* app) {
    Ball* self = (Ball*)base;

    /* Handle serve delay pause */
    if (self->serve_timer > 0.0f) {
        self->serve_timer -= dt;
        return;
    }

    /* Record trail history */
    for (int i = BALL_TRAIL_CAPACITY - 1; i > 0; i--) {
        self->trail[i] = self->trail[i - 1];
    }
    self->trail[0] = self->base.pos;
    if (self->trail_count < BALL_TRAIL_CAPACITY) {
        self->trail_count++;
    }

    /* Integrate movement */
    self->base.pos.x += self->base.vel.x * dt;
    self->base.pos.y += self->base.vel.y * dt;

    /* Top & Bottom Wall Bounces */
    float court_h = (float)app->court.height;
    if (self->base.pos.y <= 0.0f) {
        self->base.pos.y = 0.0f;
        self->base.vel.y = fabsf(self->base.vel.y); /* Bounce down */
        Renderer_TriggerBeep(app->renderer, 800, 20);
    } else if (self->base.pos.y >= court_h - 1.0f) {
        self->base.pos.y = court_h - 1.0f;
        self->base.vel.y = -fabsf(self->base.vel.y); /* Bounce up */
        Renderer_TriggerBeep(app->renderer, 800, 20);
    }

    /* Dynamic color shift when ball accelerates */
    if (self->current_speed > 32.0f) {
        self->base.color = COLOR_PAIR_BALL_FAST;
    } else {
        self->base.color = COLOR_PAIR_BALL;
    }

    /* Goal Detection: Left wall (P2 scores) or Right wall (P1 scores) */
    float court_w = (float)app->court.width;
    if (self->base.pos.x <= 0.0f) {
        /* Player 2 / CPU Scores! */
        GameApp_OnScore(app, 2);
    } else if (self->base.pos.x >= court_w - 0.5f) {
        /* Player 1 Scores! */
        GameApp_OnScore(app, 1);
    }
}

static void Ball_VirtualRender(const Entity* base, struct Renderer* r) {
    const Ball* self = (const Ball*)base;
    Renderer_DrawBall(r, self);
}

static void Ball_VirtualOnCollision(Entity* base, Entity* other, struct GameApp* app) {
    Ball* self = (Ball*)base;

    /* Verify collision is with a Paddle */
    if (strcmp(other->type_name, "Paddle") == 0) {
        Paddle* paddle = (Paddle*)other;

        /* Calculate hit position relative to paddle center (-1.0 to +1.0) */
        float paddle_center_y = paddle->base.pos.y + (paddle->base.size.y * 0.5f);
        float relative_hit = (self->base.pos.y - paddle_center_y) / (paddle->base.size.y * 0.5f);
        relative_hit = clampf(relative_hit, -1.0f, 1.0f);

        /* Deflection angle up to 55 degrees (0.96 radians) */
        float max_angle = 55.0f * (M_PI / 180.0f);
        float bounce_angle = relative_hit * max_angle;

        /* Increment rally and accelerate speed */
        self->rally_count++;
        if (self->rally_count > self->max_rally) {
            self->max_rally = self->rally_count;
        }

        self->current_speed = minf(self->max_speed, self->current_speed + 1.2f);

        /* Set new velocity vector */
        float dir_x = (paddle->player_id == 1) ? 1.0f : -1.0f;
        self->base.vel.x = dir_x * self->current_speed * cosf(bounce_angle);
        self->base.vel.y = self->current_speed * sinf(bounce_angle);

        /* Push ball outside paddle to avoid tunneling/double hits */
        if (paddle->player_id == 1) {
            self->base.pos.x = paddle->base.pos.x + paddle->base.size.x + 0.1f;
        } else {
            self->base.pos.x = paddle->base.pos.x - self->base.size.x - 0.1f;
        }

        /* Hit sound feedback */
        int pitch = 1000 + (self->rally_count * 50);
        Renderer_TriggerBeep(app->renderer, pitch, 35);
    }
}

static void Ball_VirtualDestroy(Entity* base) {
    Ball* self = (Ball*)base;
    Entity_BaseDestroy(base);
    free(self);
}

static const EntityVTable BALL_VTABLE = {
    .update = Ball_VirtualUpdate,
    .render = Ball_VirtualRender,
    .on_collision = Ball_VirtualOnCollision,
    .destroy = Ball_VirtualDestroy
};

Ball* Ball_Create(float x, float y) {
    Ball* b = (Ball*)malloc(sizeof(Ball));
    if (!b) return NULL;

    Entity_Init(&b->base, &BALL_VTABLE, "Ball", vec2(x, y), vec2(1.0f, 1.0f), COLOR_PAIR_BALL);

    b->base_speed = 24.0f;
    b->current_speed = b->base_speed;
    b->max_speed = 48.0f;
    b->rally_count = 0;
    b->max_rally = 0;
    b->serve_timer = 0.8f;
    b->last_scorer = 1;
    b->trail_count = 0;

    return b;
}

void Ball_Serve(Ball* self, int direction_x, float start_y) {
    if (!self) return;
    self->current_speed = self->base_speed;
    self->rally_count = 0;
    self->trail_count = 0;
    self->serve_timer = 0.8f;

    /* Random serve angle between -25 and +25 degrees */
    float rand_ang = ((float)(rand() % 50) - 25.0f) * (M_PI / 180.0f);
    float dir = (direction_x >= 0) ? 1.0f : -1.0f;

    self->base.vel.x = dir * self->current_speed * cosf(rand_ang);
    self->base.vel.y = self->current_speed * sinf(rand_ang);
    self->base.pos.y = start_y;
}

void Ball_Reset(Ball* self, float center_x, float center_y) {
    if (!self) return;
    self->base.pos = vec2(center_x, center_y);
    self->base.vel = vec2(0.0f, 0.0f);
    self->trail_count = 0;
}

float Ball_GetSpeed(const Ball* self) {
    return self ? self->current_speed : 0.0f;
}
