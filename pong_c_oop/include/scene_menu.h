/**
 * scene_menu.h - Interactive Main Menu Scene.
 */

#ifndef SCENE_MENU_H
#define SCENE_MENU_H

#include "scene.h"

typedef struct MenuScene {
    GameScene base;
    int selected_item;
    float anim_pulse;
} MenuScene;

GameScene* MenuScene_Create(void);

#endif /* SCENE_MENU_H */
