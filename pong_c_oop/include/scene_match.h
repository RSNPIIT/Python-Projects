/**
 * scene_match.h - Active Match Gameplay Scene.
 */

#ifndef SCENE_MATCH_H
#define SCENE_MATCH_H

#include "scene.h"

typedef struct MatchScene {
    GameScene base;
    bool paused;
    int pause_selected;
    float match_timer;
} MatchScene;

GameScene* MatchScene_Create(void);

#endif /* SCENE_MATCH_H */
