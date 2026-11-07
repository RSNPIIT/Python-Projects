"""A simple plane dodger controlled by the index fingertip."""
import argparse
import random
import cv2
import mediapipe as mp
import pygame
from camera_utils import open_camera

WIDTH, HEIGHT = 800, 600

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--camera", type=int, default=0)
    args = parser.parse_args()
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Hand Plane - move your index finger to steer")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 34)
    try:
        camera = open_camera(args.camera)
    except RuntimeError:
        pygame.quit()
        raise
    hands = mp.solutions.hands.Hands(max_num_hands=1, min_detection_confidence=.6, min_tracking_confidence=.55)
    plane_x, plane_y = WIDTH // 2, HEIGHT - 90
    obstacles, score, frame_count, game_over = [], 0, 0, False
    try:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    obstacles, score, game_over = [], 0, False
            ok, frame = camera.read()
            if not ok:
                break
            frame = cv2.flip(frame, 1)
            result = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            boost = False
            if result.multi_hand_landmarks:
                lm = result.multi_hand_landmarks[0].landmark
                plane_x = int(max(28, min(WIDTH-28, lm[8].x * WIDTH)))
                plane_y = int(max(100, min(HEIGHT-45, lm[8].y * HEIGHT)))
                boost = lm[12].y < lm[10].y and lm[16].y < lm[14].y and lm[20].y < lm[18].y
            frame_count += 1
            if not game_over:
                if frame_count % 38 == 0:
                    obstacles.append([random.randint(25, WIDTH-25), -25, random.randint(16,25)])
                speed = 7 if boost else 4
                for obstacle in obstacles:
                    obstacle[1] += speed
                    if (obstacle[0]-plane_x)**2 + (obstacle[1]-plane_y)**2 < (obstacle[2]+23)**2:
                        game_over = True
                passed = [o for o in obstacles if o[1] > HEIGHT+30]
                score += len(passed)
                obstacles = [o for o in obstacles if o[1] <= HEIGHT+30]
            screen.fill((13, 23, 48))
            for y in range(0, HEIGHT, 60):
                pygame.draw.line(screen, (22, 38, 68), (0,y), (WIDTH,y), 1)
            for x, y, radius in obstacles:
                pygame.draw.circle(screen, (245, 75, 83), (x,y), radius)
            # Simple airplane silhouette.
            pygame.draw.polygon(screen, (75, 205, 255), [(plane_x,plane_y-28),(plane_x-9,plane_y+13),(plane_x-28,plane_y+25),(plane_x-27,plane_y+32),(plane_x-5,plane_y+25),(plane_x,plane_y+34),(plane_x+5,plane_y+25),(plane_x+27,plane_y+32),(plane_x+28,plane_y+25),(plane_x+9,plane_y+13)])
            screen.blit(font.render(f"Score: {score}", True, (240,245,255)), (18,16))
            screen.blit(font.render("Open hand = boost | R = restart | Q = quit", True, (180,195,220)), (18,52))
            if game_over:
                title = font.render("CRASH! Press R to try again", True, (255,220,220))
                screen.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//2)))
            pygame.display.flip()
            clock.tick(30)
            if pygame.key.get_pressed()[pygame.K_q]:
                running = False
    finally:
        hands.close()
        camera.release()
        pygame.quit()

if __name__ == "__main__":
    main()
