#include <unistd.h>
#include <ncurses.h>
#include <math.h>
#include <stdbool.h>

typedef struct {
    int y;
    int x;
} vec2;

typedef struct {
    int player;
    int computer;
} score;

int main(void) {
    int screen_width = 50;
    int screen_height = 15;
    double y_incrementer = 0;
    int bounce_rate = 4;

    WINDOW *win = initscr();

    cbreak();            // Read characters immediately without waiting for Enter
    noecho();            // Don't echo typed characters to the screen
    keypad(win, true);   // Enable arrow keys
    nodelay(win, true);  // Non-blocking wgetch()
    curs_set(0);         // Hide cursor

    vec2 paddle = {0, 0};
    vec2 paddle_direction = {0, 0};

    vec2 CPUpaddle = {0, 0};
    vec2 CPUpaddle_direction = {0, 0};

    vec2 ball = {screen_height / 2, screen_width / 2};
    vec2 ball_direction = {1, 1};

    score scoreScore = {0, 0};

    int set_CPUPaddle__Timer = 10;
    int CPU_paddleTimer = set_CPUPaddle__Timer;

    while (true) {
        int activeKey = wgetch(win);

        if (CPU_paddleTimer == 0) {
            CPU_paddleTimer = set_CPUPaddle__Timer;
        } else {
            CPU_paddleTimer -= 1;
        }

        // Player Paddle controls
        if (activeKey == KEY_DOWN && paddle.y <= screen_height - 6) {
            paddle_direction.x = 0;
            paddle_direction.y = 1;
        } else if (activeKey == KEY_UP && paddle.y >= 1) {
            paddle_direction.x = 0;
            paddle_direction.y = -1;
        } else {
            paddle_direction.y = 0;
        }

        // Escape key (27) to quit
        if (activeKey == 27 || activeKey == 'q' || activeKey == 'Q') {
            break;
        }

        // Backspace or 'r' to reset
        if (activeKey == KEY_BACKSPACE || activeKey == 127 || activeKey == 'r') {
            ball.x = screen_width / 2;
            ball.y = screen_height / 2;
            ball_direction.x = 1;
            ball_direction.y = 1;
            bounce_rate = 4;
            scoreScore.computer = 0;
            scoreScore.player = 0;
            paddle.y = 0;
            CPUpaddle.y = 0;
        }

        // CPU AI logic
        if (CPUpaddle.y > ball.y - 2 && CPU_paddleTimer == 0) {
            CPUpaddle_direction.y = -1;
        }
        if (CPUpaddle.y < ball.y - 2 && CPU_paddleTimer == 0) {
            CPUpaddle_direction.y = 1;
        }

        paddle.y += paddle_direction.y;

        if (CPUpaddle_direction.y == 1 && CPUpaddle.y <= screen_height - 6 && CPU_paddleTimer >= 5) {
            CPUpaddle.y += CPUpaddle_direction.y;
        }
        if (CPUpaddle_direction.y == -1 && CPUpaddle.y >= 1 && CPU_paddleTimer >= 5) {
            CPUpaddle.y += CPUpaddle_direction.y;
        }

        // Ball X collision with CPU Paddle
        if (ball.x != screen_width - 2 && ball_direction.x == 1) {
            ball.x += ball_direction.x;
        } else if (ball_direction.x == 1 && (ball.y >= CPUpaddle.y + 1 && ball.y <= CPUpaddle.y + 4)) {
            ball_direction.x = -1;
            if (CPUpaddle_direction.y != 0) {
                if (CPUpaddle_direction.y == ball_direction.y) {
                    bounce_rate -= 1;
                    if (bounce_rate <= 0) bounce_rate = 1;
                } else {
                    bounce_rate += 1;
                    if (bounce_rate <= 0) bounce_rate = 1;
                }
            }
        } else if (ball_direction.x == 1) {
            // Player scores
            ball.x = screen_width / 2;
            ball.y = screen_height / 2;
            ball_direction.x = -1;
            ball_direction.y = 1;
            scoreScore.player += 1;
            bounce_rate = 4;
        }

        // Ball X collision with Player Paddle
        if (ball.x != 2 && ball_direction.x == -1) {
            ball.x += ball_direction.x;
        } else if (ball_direction.x == -1 && (ball.y >= paddle.y + 1 && ball.y <= paddle.y + 4)) {
            ball_direction.x = 1;
            if (paddle_direction.y != 0) {
                if (paddle_direction.y == ball_direction.y) {
                    bounce_rate -= 1;
                    if (bounce_rate <= 0) bounce_rate = 1;
                } else {
                    bounce_rate += 1;
                    if (bounce_rate <= 0) bounce_rate = 1;
                }
            }
        } else if (ball_direction.x == -1) {
            // CPU scores
            ball.x = screen_width / 2;
            ball.y = screen_height / 2;
            ball_direction.x = 1;
            ball_direction.y = -1;
            scoreScore.computer += 1;
            bounce_rate = 4;
        }

        // Y position sub-pixel increments
        y_incrementer += (double)ball_direction.y / bounce_rate;
        int y_incrementerInteger = (int)trunc(y_incrementer);
        if (y_incrementerInteger != 0) {
            ball.y += y_incrementerInteger;
            y_incrementer -= (double)y_incrementerInteger;
        }

        // Top / Bottom wall bounce
        if (ball.y >= screen_height) {
            ball.y = screen_height - 1;
            y_incrementer = 0;
            ball_direction.y = -1;
        } else if (ball.y <= 0) {
            ball.y = 1;
            y_incrementer = 0;
            ball_direction.y = 1;
        }

        erase();

        // Win / Loss banners
        if (scoreScore.player >= 10) {
            mvprintw(screen_height / 2, screen_width / 2 - 4, "YOU WIN!!!");
            mvprintw(screen_height / 2 + 1, screen_width / 2 - 11, "Press Backspace to Reset");
        } else if (scoreScore.computer >= 10) {
            mvprintw(screen_height / 2, screen_width / 2 - 4, "YOU LOSE!!!");
            mvprintw(screen_height / 2 + 1, screen_width / 2 - 11, "Press Backspace to Reset");
        }

        // HUD Dashboard
        mvprintw(0, screen_width + 5, "=== P O N G ===");
        mvprintw(1, screen_width + 5, "First to 10 Wins! [Q] to quit");
        mvprintw(3, screen_width + 5, "Bounce Rate     : %d", bounce_rate);
        mvprintw(5, screen_width + 5, "Ball X Position : %d", ball.x);
        mvprintw(6, screen_width + 5, "Ball Y Position : %d", ball.y);
        mvprintw(8, screen_width + 5, "Player Score    : %d", scoreScore.player);
        mvprintw(9, screen_width + 5, "Computer Score  : %d", scoreScore.computer);
        mvprintw(11, screen_width + 5, "CPU Paddle Timer: %d", CPU_paddleTimer);

        // Draw Court Walls
        for (int i = 0; i <= screen_height; i++) {
            mvaddch(i, 0, '|');
            mvaddch(i, screen_width, '|');
        }
        for (int i = 0; i <= screen_width; i++) {
            mvaddch(0, i, '-');
            mvaddch(screen_height, i, '-');
        }

        // Draw Player Paddle
        for (int i = 1; i <= 4; i++) {
            mvaddch(paddle.y + i, paddle.x + 1, ']');
        }

        // Draw CPU Paddle
        for (int i = 1; i <= 4; i++) {
            mvaddch(CPUpaddle.y + i, CPUpaddle.x + screen_width - 1, '[');
        }

        // Draw Ball
        mvaddch(ball.y, ball.x, 'o');

        refresh();
        usleep(40000); // ~25 FPS
    }

    endwin();
    return 0;
}