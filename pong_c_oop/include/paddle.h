/**
 * paddle.h - Paddle Class Inheriting from Entity (OOP in C).
 */

#ifndef PADDLE_H
#define PADDLE_H

#include "entity.h"
#include "controller.h"

typedef struct Paddle {
    Entity base;                /* Inheritance: First member enables polymorphic casting */
    int player_id;              /* 1 for Player 1 (Left), 2 for Player 2/CPU (Right) */
    float speed;                /* Movement units per second */
    int score;                  /* Match points scored */
    Controller* controller;     /* Injected control strategy */
    float hit_flash_timer;      /* Visual hit feedback timer */
    int consecutive_hits;       /* Defensive saves counter */
} Paddle;

/* Constructor & Specialized Methods */
Paddle* Paddle_Create(int player_id, float x, float y, float height, Controller* controller);
void Paddle_SetController(Paddle* self, Controller* new_controller);
void Paddle_Reset(Paddle* self, float y);
void Paddle_AddScore(Paddle* self, int points);

#endif /* PADDLE_H */
