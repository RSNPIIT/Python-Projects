/**
 * entity.h - Base Entity Class with Virtual Method Table (VTable).
 * Demonstrates Inheritance and Dynamic Polymorphism in Pure C.
 */

#ifndef ENTITY_H
#define ENTITY_H

#include "common.h"

/* Forward declarations */
struct GameApp;
struct Renderer;
struct Entity;

/* Virtual Method Table (Interface for all Entities) */
typedef struct EntityVTable {
    void (*update)(struct Entity* self, float dt, struct GameApp* app);
    void (*render)(const struct Entity* self, struct Renderer* renderer);
    void (*on_collision)(struct Entity* self, struct Entity* other, struct GameApp* app);
    void (*destroy)(struct Entity* self);
} EntityVTable;

/* Base Entity Class */
typedef struct Entity {
    const EntityVTable* vtable; /* Pointer to Virtual Function Table */
    const char* type_name;      /* Runtime Type Info (RTTI) */
    Vec2 pos;                   /* Sub-character floating-point position in court */
    Vec2 vel;                   /* Movement vector per second */
    Vec2 size;                  /* Width and Height */
    ColorPairId color;          /* Render color */
    bool active;
} Entity;

/* Base Constructor & Destructor */
void Entity_Init(Entity* self, const EntityVTable* vtable, const char* type_name, Vec2 pos, Vec2 size, ColorPairId color);
void Entity_BaseDestroy(Entity* self);

/* Polymorphic Dispatch Helper Wrappers */
static inline void Entity_Update(Entity* self, float dt, struct GameApp* app) {
    if (self && self->vtable && self->vtable->update) {
        self->vtable->update(self, dt, app);
    }
}

static inline void Entity_Render(const Entity* self, struct Renderer* renderer) {
    if (self && self->vtable && self->vtable->render) {
        self->vtable->render(self, renderer);
    }
}

static inline void Entity_OnCollision(Entity* self, Entity* other, struct GameApp* app) {
    if (self && self->vtable && self->vtable->on_collision) {
        self->vtable->on_collision(self, other, app);
    }
}

static inline void Entity_Destroy(Entity* self) {
    if (self && self->vtable && self->vtable->destroy) {
        self->vtable->destroy(self);
    }
}

static inline Rect Entity_GetBounds(const Entity* self) {
    return rect_create(self->pos.x, self->pos.y, self->size.x, self->size.y);
}

#endif /* ENTITY_H */
