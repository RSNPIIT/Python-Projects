/**
 * scene.h - Game Scene Interface (State Pattern in OOP).
 * Allows Seamless Transitions Between Menu, Gameplay, Pause, and GameOver.
 */

#ifndef SCENE_H
#define SCENE_H

#include "common.h"

struct GameApp;
struct GameScene;

typedef struct GameSceneVTable {
    void (*enter)(struct GameScene* self, struct GameApp* app);
    void (*handle_input)(struct GameScene* self, struct GameApp* app, int ch);
    void (*update)(struct GameScene* self, struct GameApp* app, float dt);
    void (*render)(struct GameScene* self, struct GameApp* app);
    void (*exit)(struct GameScene* self, struct GameApp* app);
    void (*destroy)(struct GameScene* self);
} GameSceneVTable;

typedef struct GameScene {
    const GameSceneVTable* vtable;
} GameScene;

static inline void GameScene_Enter(GameScene* self, struct GameApp* app) {
    if (self && self->vtable && self->vtable->enter) self->vtable->enter(self, app);
}

static inline void GameScene_HandleInput(GameScene* self, struct GameApp* app, int ch) {
    if (self && self->vtable && self->vtable->handle_input) self->vtable->handle_input(self, app, ch);
}

static inline void GameScene_Update(GameScene* self, struct GameApp* app, float dt) {
    if (self && self->vtable && self->vtable->update) self->vtable->update(self, app, dt);
}

static inline void GameScene_Render(GameScene* self, struct GameApp* app) {
    if (self && self->vtable && self->vtable->render) self->vtable->render(self, app);
}

static inline void GameScene_Exit(GameScene* self, struct GameApp* app) {
    if (self && self->vtable && self->vtable->exit) self->vtable->exit(self, app);
}

static inline void GameScene_Destroy(GameScene* self) {
    if (self && self->vtable && self->vtable->destroy) self->vtable->destroy(self);
}

#endif /* SCENE_H */
