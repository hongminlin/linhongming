import pygame
import random
from moviepy.editor import VideoFileClip
from PIL import Image
import time

pygame.init()

# 設定視窗大小
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('小船game')

WHITE = (255, 255, 255)

clock = pygame.time.Clock()
FPS = 60

font = pygame.font.SysFont(None, 72)

# 載入 GIF 動畫
def load_gif(path):
    img = Image.open(path)
    frames = []
    try:
        while True:
            frame = img.copy().convert('RGBA')
            frames.append(frame)
            img.seek(len(frames))
    except EOFError:
        pass
    return frames

# PIL 轉換為 Pygame 圖像
def pil_to_pygame(pil_image):
    mode = pil_image.mode
    size = pil_image.size
    data = pil_image.tobytes()
    return pygame.image.fromstring(data, size, mode)

# 載入背景海洋
background_frames = load_gif(r"C:\\Users\\user\\Downloads\\海洋.gif")
background_frames = [pil_to_pygame(frame) for frame in background_frames]
background_frames = [pygame.transform.scale(frame, (screen_width, screen_height)) for frame in background_frames]

# 載入小船圖像
boat_image_still = pygame.image.load(r"C:\\Users\\user\\Downloads\\大船.png")  # 靜止時的小船
boat_image_left = pygame.image.load(r"C:\\Users\\user\\Downloads\\大船向左.png")  # 向左的小船
boat_image_right = pygame.image.load(r"C:\\Users\\user\\Downloads\\大船向右.png")  # 向右的小船

boat_image_still = pygame.transform.scale(boat_image_still, (150, 150))
boat_image_left = pygame.transform.scale(boat_image_left, (150, 150))
boat_image_right = pygame.transform.scale(boat_image_right, (150, 150))

boat_width = boat_image_still.get_width()
boat_height = boat_image_still.get_height()
boat_x = screen_width // 2 - boat_width // 2
boat_y = screen_height - boat_height - 10
boat_speed = 5

# 載入障礙物
obstacle_width = 50
obstacle_height = 50
obstacle_speed = 5
obstacles = []

# 障礙物的圖像路徑
obstacle_frames = [pygame.image.load(r"C:\\Users\\user\\Downloads\\金磚.png")]  # 金磚作為障礙物
obstacle_frames = [pygame.transform.scale(frame, (obstacle_width, obstacle_height)) for frame in obstacle_frames]

# 載入金幣和防護罩
coin_image = pygame.image.load(r"C:\\Users\\user\\Downloads\\金幣.png")
coin_image = pygame.transform.scale(coin_image, (150, 150))

shield_image = pygame.image.load(r"C:\\Users\\user\\Downloads\\防護罩.png")
shield_image = pygame.transform.scale(shield_image, (500, 500))

coins = []
shields = []
shield_active = False
shield_timer = 0

lives = 3
score = 0

# 創建障礙物
def create_obstacle():
    x = random.randint(0, screen_width - obstacle_width)
    y = -obstacle_height
    return [x, y]

# 創建金幣
def create_coin():
    x = random.randint(0, screen_width - 150)
    y = -150
    return [x, y]

# 創建防護罩
def create_shield():
    x = random.randint(0, screen_width - 500)
    y = -500
    return [x, y]

# 顯示生命值
def show_lives():
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    screen.blit(lives_text, (screen_width // 2 - 100, 10))

# 顯示分數
def show_score():
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (screen_width - 250, 10))

# 碰撞檢查
def check_collision(boat_rect, obj_rect):
    return boat_rect.colliderect(obj_rect)

# 顯示開始畫面
def show_start_screen():
    # 使用 moviepy 播放影片
    clip = VideoFileClip(r"C:\\Users\\user\\Downloads\\開始畫面.mp4")
    clip_resized = clip.resize(newsize=(screen_width, screen_height))
    clip_resized.preview()

# 遊戲主循環
def game_loop():
    global boat_x, boat_y, lives, score, obstacles, coins, shields, shield_active, shield_timer
    obstacle_frame_index = 0
    background_frame_index = 0
    running = True
    boat_image = boat_image_still
    last_coin_time = 0
    last_shield_time = 0
    shield_duration = 10  # 防護罩持續時間為10秒

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 檢查鍵盤按鍵
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            boat_x -= boat_speed
            boat_image = boat_image_left
        elif keys[pygame.K_RIGHT]:
            boat_x += boat_speed
            boat_image = boat_image_right
        else:
            boat_image = boat_image_still

        # 限制小船在視窗內
        boat_x = max(0, min(boat_x, screen_width - boat_width))

        # 更新背景
        screen.fill(WHITE)
        screen.blit(background_frames[background_frame_index], (0, 0))
        background_frame_index = (background_frame_index + 1) % len(background_frames)

        # 更新障礙物
        if random.randint(1, 30) == 1:
            obstacles.append(create_obstacle())

        boat_rect = pygame.Rect(boat_x, boat_y, boat_width, boat_height)  # 確保在使用前定義 boat_rect

        for obstacle in obstacles:
            obstacle[1] += obstacle_speed
            obstacle_rect = pygame.Rect(obstacle[0], obstacle[1], obstacle_width, obstacle_height)
            screen.blit(obstacle_frames[obstacle_frame_index], (obstacle[0], obstacle[1]))
            obstacle_frame_index = (obstacle_frame_index + 1) % len(obstacle_frames)

            # 檢查碰撞
            if check_collision(boat_rect, obstacle_rect):
                lives -= 1
                obstacles.remove(obstacle)
                if lives == 0:
                    print("Game Over!")
                    running = False

        obstacles = [ob for ob in obstacles if ob[1] < screen_height]

        # 金幣和防護罩掉落邏輯
        current_time = time.time()
        if current_time - last_coin_time > random.randint(10, 30):  # 每 10 到 30 秒掉落金幣
            coins.append(create_coin())
            last_coin_time = current_time

        if current_time - last_shield_time > random.randint(10, 30):  # 每 10 到 30 秒掉落防護罩
            shields.append(create_shield())
            last_shield_time = current_time

        # 金幣顯示和碰撞
        for coin in coins:
            coin[1] += obstacle_speed
            coin_rect = pygame.Rect(coin[0], coin[1], 150, 150)
            screen.blit(coin_image, (coin[0], coin[1]))

            if check_collision(boat_rect, coin_rect):
                score += 1
                coins.remove(coin)

        coins = [coin for coin in coins if coin[1] < screen_height]

        # 防護罩顯示和碰撞
        for shield in shields:
            shield[1] += obstacle_speed
            shield_rect = pygame.Rect(shield[0], shield[1], 500, 500)
            screen.blit(shield_image, (shield[0], shield[1]))

            if check_collision(boat_rect, shield_rect):
                shield_active = True
                shield_timer = time.time() + shield_duration
                shields.remove(shield)

        shields = [shield for shield in shields if shield[1] < screen_height]

        # 檢查防護罩計時
        if shield_active and time.time() > shield_timer:
            shield_active = False

        # 顯示小船
        screen.blit(boat_image, (boat_x, boat_y))

        show_lives()
        show_score()

        if score == 50:
            print("你贏了！")
            running = False

        pygame.display.update()
        clock.tick(FPS)

    pygame.quit()

show_start_screen()  # 顯示影片開始畫面
game_loop()  # 進入
