/**
 * controller.c - Implementation of Human Keyboard & Intelligent AI Controllers.
 */

#include "controller.h"
#include "game.h"
#include "paddle.h"
#include "ball.h"

/* =========================================================================
 * HumanController Implementation
 * ========================================================================= */
static int HumanController_GetDirection(Controller* base, struct GameApp* app, const struct Paddle* paddle) {
    HumanController* self = (HumanController*)base;
    (void)paddle;

    int dir = 0;
    if (GameApp_IsKeyPressed(app, self->up_key) || (self->alt_up_key && GameApp_IsKeyPressed(app, self->alt_up_key))) {
        dir -= 1;
    }
    if (GameApp_IsKeyPressed(app, self->down_key) || (self->alt_down_key && GameApp_IsKeyPressed(app, self->alt_down_key))) {
        dir += 1;
    }
    return dir;
}

static void HumanController_Destroy(Controller* base) {
    if (base) {
        free(base);
    }
}

static const ControllerVTable HUMAN_CONTROLLER_VTABLE = {
    .get_direction = HumanController_GetDirection,
    .destroy = HumanController_Destroy
};

Controller* HumanController_Create(int up_key, int down_key, int alt_up_key, int alt_down_key) {
    HumanController* ctrl = (HumanController*)malloc(sizeof(HumanController));
    if (!ctrl) return NULL;
    ctrl->base.vtable = &HUMAN_CONTROLLER_VTABLE;
    ctrl->up_key = up_key;
    ctrl->down_key = down_key;
    ctrl->alt_up_key = alt_up_key;
    ctrl->alt_down_key = alt_down_key;
    return (Controller*)ctrl;
}

/* =========================================================================
 * AIController Implementation
 * ========================================================================= */
static int AIController_GetDirection(Controller* base, struct GameApp* app, const struct Paddle* paddle) {
    AIController* self = (AIController*)base;
    const Ball* ball = GameApp_GetBall(app);
    if (!ball) return 0;

    float paddle_center_y = paddle->base.pos.y + (paddle->base.size.y * 0.5f);
    float ball_y = ball->base.pos.y;
    float ball_x = ball->base.pos.x;
    float court_w = (float)app->court.width;

    /* Check if ball is moving towards this paddle */
    bool moving_towards = false;
    if (paddle->player_id == 1 && ball->base.vel.x < 0.0f) {
        moving_towards = true;
    } else if (paddle->player_id == 2 && ball->base.vel.x > 0.0f) {
        moving_towards = true;
    }

    /* Target calculation */
    float target_y = ball_y;

    switch (self->difficulty) {
        case AI_EASY:
            /* Only reacts when ball is past mid-court */
            if (!moving_towards || (paddle->player_id == 2 && ball_x < court_w * 0.45f) ||
                (paddle->player_id == 1 && ball_x > court_w * 0.55f)) {
                target_y = (float)app->court.height * 0.5f; /* Idle near center */
            } else {
                target_y = ball_y + self->error_offset;
            }
            break;

        case AI_MEDIUM:
            if (!moving_towards) {
                target_y = (float)app->court.height * 0.5f;
            } else {
                target_y = ball_y;
            }
            break;

        case AI_HARD:
            if (moving_towards) {
                /* Linear trajectory projection to predict arrival Y */
                float dx = (paddle->base.pos.x - ball_x);
                if (fabsf(ball->base.vel.x) > 0.001f) {
                    float time_to_reach = dx / ball->base.vel.x;
                    if (time_to_reach > 0.0f) {
                        float predicted_y = ball_y + ball->base.vel.y * time_to_reach;
                        /* Simulate wall bounces */
                        float court_h = (float)app->court.height;
                        while (predicted_y < 0.0f || predicted_y > court_h) {
                            if (predicted_y < 0.0f) predicted_y = -predicted_y;
                            if (predicted_y > court_h) predicted_y = 2.0f * court_h - predicted_y;
                        }
                        target_y = predicted_y;
                    }
                }
            } else {
                target_y = (float)app->court.height * 0.5f;
            }
            break;

        case AI_UNBEATABLE:
            /* Pinpoint edge aiming to return aggressive deflection angles */
            target_y = ball_y + (ball->base.vel.y > 0 ? -1.0f : 1.0f);
            break;
    }

    /* Dead zone to prevent high-frequency jittering */
    float diff = target_y - paddle_center_y;
    float deadzone = (self->difficulty == AI_EASY) ? 1.0f : 0.4f;

    if (diff > deadzone) {
        return 1;
    } else if (diff < -deadzone) {
        return -1;
    }
    return 0;
}

static void AIController_Destroy(Controller* base) {
    if (base) {
        free(base);
    }
}

static const ControllerVTable AI_CONTROLLER_VTABLE = {
    .get_direction = AIController_GetDirection,
    .destroy = AIController_Destroy
};

Controller* AIController_Create(AIDifficulty difficulty) {
    AIController* ctrl = (AIController*)malloc(sizeof(AIController));
    if (!ctrl) return NULL;
    ctrl->base.vtable = &AI_CONTROLLER_VTABLE;
    ctrl->difficulty = difficulty;
    ctrl->reaction_timer = 0.0f;
    ctrl->reaction_delay = (difficulty == AI_EASY) ? 0.18f : 0.05f;
    ctrl->target_y = 0.0f;
    ctrl->error_offset = (difficulty == AI_EASY) ? 1.5f : 0.0f;
    return (Controller*)ctrl;
}

void AIController_SetDifficulty(Controller* base, AIDifficulty difficulty) {
    if (!base || base->vtable != &AI_CONTROLLER_VTABLE) return;
    AIController* self = (AIController*)base;
    self->difficulty = difficulty;
    self->reaction_delay = (difficulty == AI_EASY) ? 0.18f : 0.05f;
    self->error_offset = (difficulty == AI_EASY) ? 1.5f : 0.0f;
}
