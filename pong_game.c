#include <unistd.h>
#include <ncurses.h>
#include <math.h>

typedef struct {
    int y;
    int x;
} vec2;

typedef struct {
    int player;
    int computer;
} score;

int main(){
    int screen_width = 50;
    int screen_height = 15;
    double y_incrementer = 0;
    int bounce_rate = 4;

    WINDOW *win = initscr();

    keypad(win,true);
    nodelay(win,true);
    curs_set(0);

    vec2 paddle = {0,0};
    vec2 paddle_direction = {0,0};

    vec2 CPUpaddle = {0,0};
    vec2 CPUpaddle_direction = {0,0};

    vec2 ball = {screen_height / 2,screen_width / 2};
    vec2 ball_direction = {1,1};
    
    
    
    score scoreScore = {0,0};

    int set_CPUPaddle__Timer = 10;
    int CPU_paddleTimer = set_CPUPaddle__Timer;

    while(true){
        int activeKey = wgetch(win);
        if(CPU_paddleTimer == 0){
            CPU_paddleTimer = set_CPUPaddle__Timer;
        }
        else{
            CPU_paddleTimer -= 1;
        }
        if (activeKey == KEY_DOWN && paddle.y <= screen_height - 6){
            paddle_direction.x = 0;
            paddle_direction.y = 1;
        }
        else if(activeKey == KEY_UP && paddle.y >=1){
            paddle_direction.x = 0;
            paddle_direction.y = -1;
        }
        else {
            paddle_direction.y=0;
        }
        if (activeKey == '\e'){
            break;
        }
        if (activeKey == KEY_BACKSPACE){
            ball.x = screen_width /2;
            ball.y = screen_height /2;
            ball_direction.x = 1;
            ball_direction.y = 1;
            scoreScore.player += 1;
            bounce_rate = 4;
            scoreScore.computer = 0;
            scoreScore.player = 0;
            paddle.y = 0;
            CPUpaddle.y = 0;
        }

        if (CPUpaddle.y > ball.y - 2 && CPU_paddleTimer == 0){
            CPUpaddle_direction.y = -1;
        }
        if (CPUpaddle.y < ball.y - 2 && CPU_paddleTimer == 0){
            CPUpaddle_direction.y = 1;
        }
        
        paddle.y += paddle_direction.y;
        
        if(CPUpaddle_direction.y == 1 && CPUpaddle.y <= screen_height - 6 && CPU_paddleTimer >= 5){
            CPUpaddle.y += CPUpaddle_direction.y;
        }
        if(CPUpaddle_direction.y == -1 && CPUpaddle.y >= 1 && CPU_paddleTimer >=5){
            CPUpaddle.y += CPUpaddle_direction.y;
        }

        if (ball.x != screen_width - 2 && ball_direction.x == 1){
            ball.x += ball_direction.x;
        }
        else if(ball_direction.x == 1 && (ball.y == CPUpaddle.y + 1 || ball.y == CPUpaddle.y + 2 || ball.y == CPUpaddle.y + 3 || ball.y == CPUpaddle.y +4)){ // BOUNCE OFF CPU PADDLE
            ball_direction.x = -1;
            if (CPUpaddle_direction.y == 0){
                ;
            }
            else if(CPUpaddle_direction.y == ball_direction.y){
                bounce_rate -= 1;
                if(bounce_rate == 0){
                    bounce_rate = 1;
                }
            }
            else if(!(CPUpaddle_direction.y == ball_direction.y)){
                bounce_rate += 1;
                if(bounce_rate == 0){
                    bounce_rate = 1
                    ;
                }
            }
        }
        else if(ball_direction.x == 1){
            ball.x = screen_width /2;
            ball.y = screen_height /2;
            ball_direction.x = -1;
            ball_direction.y = 1;
            scoreScore.player += 1;
            bounce_rate = 4;
        }
        

        if (ball.x != 2 && ball_direction.x == -1){
            ball.x += ball_direction.x;
        }
        else if(ball_direction.x == -1 && (ball.y == paddle.y + 1 || 
            ball.y == paddle.y + 2 || 
            ball.y == paddle.y + 3 || 
            ball.y == paddle.y +4)){ // BOUNCE OFF PLAYER PADDLE
            ball_direction.x = 1;
            if (paddle_direction.y == 0){
                ; 
            }
            else if(paddle_direction.y == ball_direction.y){
                bounce_rate -= 1;
                if(bounce_rate == 0){
                    bounce_rate = 1;
                }
            }
            else if(!(paddle_direction.y == ball_direction.y)){
                bounce_rate += 1;
                if(bounce_rate == 0){
                    bounce_rate = 1;
                }
            }
        }
        else if (ball_direction.x == - 1){
            ball.x = screen_width /2;
            ball.y = screen_height /2;
            ball_direction.x = 1;
            ball_direction.y = -1;
            scoreScore.computer += 1;
            bounce_rate = 4;
        }

        y_incrementer += (double)ball_direction.y / bounce_rate;
        int y_incrementerInteger = (int)trunc(y_incrementer);
        if (y_incrementerInteger != 0){
            ball.y += y_incrementerInteger;
            y_incrementer -= (double)y_incrementerInteger;
        }

        if (ball.y >= screen_height){
            ball.y = screen_height - 1;
            y_incrementer = 0;
            ball_direction.y = -1;
            ball.y += -1;
        }
        else if (ball.y <= 0){
            ball.y = 1;
            y_incrementer = 0;
            ball_direction.y = 1;
            ball.y += 1;
        }

        erase();

        if(scoreScore.player >= 10){
            mvprintw(screen_height / 2, screen_width / 2 - 4, "YOU WIN!!!");
            mvprintw(screen_height / 2 + 1, screen_width / 2 - 11, "Press Backspace to Reset");
        }

        if(scoreScore.computer >= 10){
            mvprintw(screen_height / 2, screen_width / 2 - 4, "YOU LOSE!!!");
            mvprintw(screen_height / 2 + 1, screen_width / 2 - 11, "Press Backspace to Reset");
        }

        mvprintw(3, screen_width + 5, "bounce_rate: %d", bounce_rate);
        mvprintw(5, screen_width + 5, "ball x position: %d", ball.x);
        mvprintw(6, screen_width + 5, "ball y position: %d", ball.y);
        mvprintw(8, screen_width + 5, "player score: %d", scoreScore.player);
        mvprintw(9, screen_width + 5, "computer score: %d", scoreScore.computer);
        mvprintw(11, screen_width + 5, "y_incrementer: %lf", y_incrementer);
        mvprintw(13, screen_width + 5, "CPU Paddle Timer: %d", CPU_paddleTimer);
        mvprintw(0, screen_width + 5, "Welcome to P O N G!");
        mvprintw(1, screen_width + 5, "First to 10 Wins!! GLHF");

        for(int i = 0;i < screen_height; i++){
            mvaddch(i,0, '|');
            mvaddch(i,screen_width, '|');
        }
        for(int i = 0;i < screen_width + 1; i++){
            mvaddch(0,i, '-');
            mvaddch(screen_height,i, '-');
        }

        mvaddch(paddle.y + 1,paddle.x + 1, ']');
        mvaddch(paddle.y + 2,paddle.x + 1, ']');
        mvaddch(paddle.y + 3,paddle.x + 1, ']');
        mvaddch(paddle.y + 4,paddle.x + 1, ']');

        mvaddch(CPUpaddle.y + 1,CPUpaddle.x + screen_width - 1, '[');
        mvaddch(CPUpaddle.y + 2,CPUpaddle.x + screen_width - 1, '[');
        mvaddch(CPUpaddle.y + 3,CPUpaddle.x + screen_width - 1, '[');
        mvaddch(CPUpaddle.y + 4,CPUpaddle.x + screen_width - 1, '[');

        mvaddch(ball.y,ball.x, 'o');

        usleep(50000);
    }

    endwin();
    return 0;
}
