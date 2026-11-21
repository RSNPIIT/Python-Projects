/**
 * common.h - Core Data Structures, Geometry, and Math Helpers.
 * Part of Pong C OOP - Demonstrating Object-Oriented Programming in C.
 */

#ifndef COMMON_H
#define COMMON_H

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <math.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <ncurses.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* 2D Vector */
typedef struct Vec2 {
    float x;
    float y;
} Vec2;

static inline Vec2 vec2(float x, float y) {
    Vec2 v = { x, y };
    return v;
}

static inline Vec2 vec2_add(Vec2 a, Vec2 b) {
    return vec2(a.x + b.x, a.y + b.y);
}

static inline Vec2 vec2_sub(Vec2 a, Vec2 b) {
    return vec2(a.x - b.x, a.y - b.y);
}

static inline Vec2 vec2_scale(Vec2 v, float s) {
    return vec2(v.x * s, v.y * s);
}

static inline float vec2_length(Vec2 v) {
    return sqrtf(v.x * v.x + v.y * v.y);
}

static inline Vec2 vec2_normalize(Vec2 v) {
    float len = vec2_length(v);
    if (len > 0.0001f) {
        return vec2(v.x / len, v.y / len);
    }
    return vec2(0.0f, 0.0f);
}

/* 2D AABB Rectangle */
typedef struct Rect {
    float x;
    float y;
    float w;
    float h;
} Rect;

static inline Rect rect_create(float x, float y, float w, float h) {
    Rect r = { x, y, w, h };
    return r;
}

static inline bool rect_intersects(Rect a, Rect b) {
    return (a.x < b.x + b.w &&
            a.x + a.w > b.x &&
            a.y < b.y + b.h &&
            a.y + a.h > b.y);
}

/* Float Math Helpers */
static inline float clampf(float val, float min_val, float max_val) {
    if (val < min_val) return min_val;
    if (val > max_val) return max_val;
    return val;
}

static inline float minf(float a, float b) {
    return (a < b) ? a : b;
}

static inline float maxf(float a, float b) {
    return (a > b) ? a : b;
}

/* Color Pairs Enum for ncurses */
typedef enum ColorPairId {
    COLOR_PAIR_DEFAULT = 1,
    COLOR_PAIR_COURT,
    COLOR_PAIR_PLAYER1,
    COLOR_PAIR_PLAYER2,
    COLOR_PAIR_BALL,
    COLOR_PAIR_BALL_FAST,
    COLOR_PAIR_SCORE,
    COLOR_PAIR_HUD_TITLE,
    COLOR_PAIR_HUD_ACCENT,
    COLOR_PAIR_MENU_SELECTED,
    COLOR_PAIR_MENU_NORMAL,
    COLOR_PAIR_GOLD,
    COLOR_PAIR_TRAIL
} ColorPairId;

/* Game Modes */
typedef enum GameMode {
    GAME_MODE_SINGLEPLAYER = 0, /* Player vs CPU */
    GAME_MODE_MULTIPLAYER,      /* Local 2-Player (W/S vs Up/Down) */
    GAME_MODE_SPECTATOR,        /* CPU vs CPU Attract Mode */
    GAME_MODE_PRACTICE          /* Player solo rally against solid wall */
} GameMode;

/* AI Difficulties */
typedef enum AIDifficulty {
    AI_EASY = 0,   /* Relaxed, slower reaction, slight aiming error */
    AI_MEDIUM,     /* Balanced rally partner */
    AI_HARD,       /* Sharp angle prediction, fast tracking */
    AI_UNBEATABLE  /* Millimeter perfect interception */
} AIDifficulty;

#endif /* COMMON_H */
