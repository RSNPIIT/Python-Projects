/**
 * scene_gameover.h - Post-Match Summary & Victory Scene.
 */

#ifndef SCENE_GAMEOVER_H
#define SCENE_GAMEOVER_H

#include "scene.h"

typedef struct GameOverScene {
    GameScene base;
    int winner_id;
    float match_duration;
    int selected_button;
    float anim_timer;
} GameOverScene;

GameScene* GameOverScene_Create(int winner_id, float match_duration);

#endif /* SCENE_GAMEOVER_H */
