/**
 * entity.c - Base Entity Class Implementation.
 */

#include "entity.h"

void Entity_Init(Entity* self, const EntityVTable* vtable, const char* type_name, Vec2 pos, Vec2 size, ColorPairId color) {
    if (!self) return;
    self->vtable = vtable;
    self->type_name = type_name;
    self->pos = pos;
    self->vel = vec2(0.0f, 0.0f);
    self->size = size;
    self->color = color;
    self->active = true;
}

void Entity_BaseDestroy(Entity* self) {
    if (!self) return;
    self->active = false;
    /* In a larger engine, release components or free resources here */
}
