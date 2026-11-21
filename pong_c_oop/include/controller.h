/**
 * controller.h - Controller Interface (Strategy Pattern).
 * Abstracts Human Keyboard Controls and Intelligent AI Behaviors.
 */

#ifndef CONTROLLER_H
#define CONTROLLER_H

#include "common.h"

struct GameApp;
struct Paddle;
struct Controller;

/* Virtual Table for Controller Interface */
typedef struct ControllerVTable {
    int (*get_direction)(struct Controller* self, struct GameApp* app, const struct Paddle* paddle);
    void (*destroy)(struct Controller* self);
} ControllerVTable;

/* Base Controller Interface Struct */
typedef struct Controller {
    const ControllerVTable* vtable;
} Controller;

/* Concrete Human Controller */
typedef struct HumanController {
    Controller base;        /* First member = Inheritance */
    int up_key;
    int down_key;
    int alt_up_key;
    int alt_down_key;
} HumanController;

Controller* HumanController_Create(int up_key, int down_key, int alt_up_key, int alt_down_key);

/* Concrete AI Controller */
typedef struct AIController {
    Controller base;        /* First member = Inheritance */
    AIDifficulty difficulty;
    float reaction_timer;
    float reaction_delay;
    float target_y;
    float error_offset;
} AIController;

Controller* AIController_Create(AIDifficulty difficulty);
void AIController_SetDifficulty(Controller* self, AIDifficulty difficulty);

#endif /* CONTROLLER_H */
