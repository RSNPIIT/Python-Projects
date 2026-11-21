/**
 * ball.h - Ball Class Inheriting from Entity (OOP in C).
 * Sub-Cell Precision Physics, Angle Deflection & Motion Trail.
 */

#ifndef BALL_H
#define BALL_H

#include "entity.h"

#define BALL_TRAIL_CAPACITY 8

typedef struct Ball {
    Entity base;                        /* Inheritance: First member enables polymorphic casting */
    float base_speed;                   /* Starting serve velocity */
    float current_speed;                /* Speed with rally acceleration */
    float max_speed;                    /* Speed cap */
    int rally_count;                    /* Current uninterrupted rally hits */
    int max_rally;                      /* Longest rally in match */
    float serve_timer;                  /* Countdown pause before launch */
    int last_scorer;                    /* Player id who scored last */
    Vec2 trail[BALL_TRAIL_CAPACITY];    /* History buffer for fading particle trail */
    int trail_count;
} Ball;

/* Constructor & Methods */
Ball* Ball_Create(float x, float y);
void Ball_Serve(Ball* self, int direction_x, float start_y);
void Ball_Reset(Ball* self, float center_x, float center_y);
float Ball_GetSpeed(const Ball* self);

#endif /* BALL_H */
