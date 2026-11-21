/**
 * main.c - Pong OOP in Pure C Entry Point.
 */

#include <locale.h>
#include <stdlib.h>
#include <time.h>
#include "game.h"
#include "scene_menu.h"

int main(void) {
    /* Enable Unicode / wide characters for clean court rendering */
    setlocale(LC_ALL, "");

    /* Seed pseudo-random number generator */
    srand((unsigned int)time(NULL));

    /* Instantiate Game Application Coordinator */
    GameApp* app = GameApp_Create();
    if (!app) {
        return 1;
    }

    /* Start with the Interactive Main Menu Scene */
    GameApp_SetScene(app, MenuScene_Create());

    /* Enter 60 FPS Game Loop */
    GameApp_Run(app);

    /* Clean up all OOP memory allocations and restore terminal */
    GameApp_Destroy(app);

    return 0;
}
