/* ===========================================================================
 *  DINO RUN  --  гра "динозавр" (як у Chrome) для командного рядка Windows
 * ---------------------------------------------------------------------------
 *  Збірка (MinGW / gcc) :   gcc dino.c -O2 -o dino.exe
 *  Збірка (MSVC)        :   cl dino.c            (або cl /O2 dino.c /Fe:dino.exe)
 *  Запуск               :   dino.exe
 *
 *  Керування:  SPACE / UP / W .... стрибок
 *              DOWN / S .......... присісти (під птаха)
 *              P ................. пауза
 *              R ................. заново (після Game Over)
 *              Q / ESC ........... вихід
 *
 *  Рекомендовано: вікно терміналу не менше 46 x 17 символів.
 * ===========================================================================
 */

#define _CRT_SECURE_NO_WARNINGS
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX

#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#ifndef ENABLE_VIRTUAL_TERMINAL_PROCESSING
#define ENABLE_VIRTUAL_TERMINAL_PROCESSING 0x0004
#endif
#ifndef ENABLE_EXTENDED_FLAGS
#define ENABLE_EXTENDED_FLAGS 0x0080
#endif

/* --------------------------------------------------------------- налаштування */
#define MAX_W   120          /* максимум колонок, які малюємо            */
#define MAX_H   40           /* максимум рядків                          */
#define MIN_W   46           /* мінімальний робочий розмір вікна         */
#define MIN_H   16
#define MAX_OBS 24           /* максимум перешкод одночасно              */
#define TICK    (1.0 / 60.0) /* крок фізики, секунди                     */
#define HI_FILE "dino_hiscore.txt"

/* ------------------------------------------------------------------- кольори */
enum { A_NONE = 0, A_DINO, A_CACTUS, A_GROUND, A_HUD, A_BIRD, A_DIM, A_ALERT };

static const char *COLOR[] = {
    "\x1b[0m",   /* A_NONE   скидання     */
    "\x1b[92m",  /* A_DINO   яскраво-зел. */
    "\x1b[91m",  /* A_CACTUS яскраво-черв.*/
    "\x1b[90m",  /* A_GROUND сірий        */
    "\x1b[97m",  /* A_HUD    білий        */
    "\x1b[96m",  /* A_BIRD   блакитний    */
    "\x1b[90m",  /* A_DIM    сірий        */
    "\x1b[93m"   /* A_ALERT  жовтий       */
};

/* -------------------------------------------------------------- консоль/буфер */
static HANDLE g_out = NULL, g_in = NULL;
static DWORD  g_out_mode = 0, g_in_mode = 0;
static int    g_have_out_mode = 0, g_have_in_mode = 0;
static int    g_cols = 80, g_rows = 24, g_color = 0;

static char          g_ch[MAX_H][MAX_W];   /* символи кадру  */
static unsigned char g_at[MAX_H][MAX_W];   /* колір кадру    */
static char          g_buf[(MAX_W + 2) * MAX_H * 8 + 4096];
static int           g_len;

/* -------------------------------------------------------------------- спрайти */
#define DINO_W 7
#define DINO_H 4
#define DUCK_W 7
#define DUCK_H 1

static const char *SPR_RUN[2][DINO_H] = {
    { "  ___  ", " (o o) ", " /|_|\\ ", "  ^ ^  " },
    { "  ___  ", " (o o) ", " /|_|\\ ", " ^   ^ " }
};
static const char *SPR_DUCK[DUCK_H] = { " (o__)>" };

static const char *SPR_C1[2] = { " _ ", "| |" };                     /* кактус 3x2 */
static const char *SPR_C2[3] = { " _ ", "| |", "|_|" };              /* кактус 3x3 */
static const char *SPR_C3[3] = { " _   _ ", "| | | |", "|_| |_|" };  /* кактус 7x3 */

static const char *SPR_BIRD[2][2] = {
    { "  ___  ", " (   )>" },
    { "  \\_/  ", " (   )>" }
};
static const char *SPR_CLOUD[2] = { " .--. ", "(    )" };

/* --------------------------------------------------------------- стан гри */
enum { ST_TITLE = 0, ST_PLAY, ST_DEAD, ST_PAUSE };

typedef struct {
    double x;          /* ліва колонка (у символах)   */
    double y0, y1;     /* низ/верх над землею, рядки  */
    int    w;          /* ширина                      */
    int    kind;       /* 0,1,2 кактус; 3 птах         */
} Obstacle;

static Obstacle g_obs[MAX_OBS];
static int    g_nobs;
static int    g_state = ST_TITLE;

static double g_dino_x = 6.0;
static double g_dino_y;            /* висота низу динозавра над землею */
static double g_dino_vy;           /* вертикальна швидкість            */
static int    g_on_ground = 1;
static int    g_duck = 0, g_duck_held = 0, g_run_frame = 0, g_bird_frame = 0;

static double g_speed, g_score, g_hi;
static double g_spawn_acc, g_next_gap;

static double g_cloud_x[3];
static int    g_cloud_y[3];

/* ============================================================ дрібні функції */

static int dino_h(void) { return g_duck ? DUCK_H : DINO_H; }
static int dino_w(void) { return g_duck ? DUCK_W : DINO_W; }

static double now_sec(void)
{
    LARGE_INTEGER f, c;
    QueryPerformanceFrequency(&f);
    QueryPerformanceCounter(&c);
    return (double)c.QuadPart / (double)f.QuadPart;
}

static void put(int y, int x, char c, int a)
{
    if (y < 0 || y >= g_rows || x < 0 || x >= g_cols) return;
    g_ch[y][x] = c;
    if (a) g_at[y][x] = (unsigned char)a;
}

/* малює спрайт: art[0] у рядку top, далі вниз; пробіли не чіпаємо */
static void blit_top(int top, int left, const char *const *art, int h, int a)
{
    int i, j;
    for (i = 0; i < h; i++) {
        const char *row = art[i];
        for (j = 0; row[j]; j++)
            if (row[j] != ' ') put(top + i, left + j, row[j], a);
    }
}

static void put_text(int y, int x, const char *s, int a)
{
    while (*s) put(y, x++, *s++, a);
}

static void put_text_center(int y, const char *s, int a)
{
    put_text(y, (g_cols - (int)strlen(s)) / 2, s, a);
}

/* ============================================================== вивід кадру */

static void render(void)
{
    int y, x, cur = -1;
    DWORD written;

    g_len = 0;
    for (y = 0; y < g_rows; y++) {
        for (x = 0; x < g_cols; x++) {
            int a = g_at[y][x];
            if (a != cur) {
                if (g_color) {
                    const char *s = COLOR[a];
                    while (*s) g_buf[g_len++] = *s++;
                }
                cur = a;
            }
            g_buf[g_len++] = g_ch[y][x];
        }
        if (g_color && cur != A_NONE) {
            const char *s = COLOR[A_NONE];
            while (*s) g_buf[g_len++] = *s++;
            cur = A_NONE;
        }
        if (y != g_rows - 1) {           /* останній рядок без \n -> без прокрутки */
            g_buf[g_len++] = '\r';
            g_buf[g_len++] = '\n';
        }
    }

    {
        COORD p;
        p.X = 0;
        p.Y = 0;
        SetConsoleCursorPosition(g_out, p);
    }
    if (!WriteConsoleA(g_out, g_buf, (DWORD)g_len, &written, NULL))
        WriteFile(g_out, g_buf, (DWORD)g_len, &written, NULL);
}

/* ============================================================== розмір вікна */

static void query_size(void)
{
    CONSOLE_SCREEN_BUFFER_INFO bi;
    if (GetConsoleScreenBufferInfo(g_out, &bi)) {
        int w = bi.srWindow.Right - bi.srWindow.Left + 1;
        int h = bi.srWindow.Bottom - bi.srWindow.Top + 1;
        if (w > 0) g_cols = w;
        if (h > 0) g_rows = h - 1;       /* один рядок лишаємо запасним */
    }
    if (g_cols > MAX_W) g_cols = MAX_W;
    if (g_rows > MAX_H) g_rows = MAX_H;
    if (g_cols < 1) g_cols = 1;
    if (g_rows < 1) g_rows = 1;
}

/* ================================================================= життя гри */

static void load_hi(void)
{
    FILE *f = fopen(HI_FILE, "r");
    g_hi = 0.0;
    if (f) {
        if (fscanf(f, "%lf", &g_hi) != 1) g_hi = 0.0;
        fclose(f);
    }
    if (g_hi < 0.0) g_hi = 0.0;
}

static void save_hi(void)
{
    FILE *f = fopen(HI_FILE, "w");
    if (f) {
        fprintf(f, "%d\n", (int)g_hi);
        fclose(f);
    }
}

static void reset_game(void)
{
    int i;
    g_dino_y = 0.0;
    g_dino_vy = 0.0;
    g_on_ground = 1;
    g_duck = 0;
    g_duck_held = 0;
    g_run_frame = 0;
    g_bird_frame = 0;
    g_speed = 9.0;
    g_score = 0.0;
    g_spawn_acc = 0.0;
    g_next_gap = 22.0 + (double)(rand() % 14);

    g_nobs = 1;
    g_obs[0].kind = 0;
    g_obs[0].x = g_cols * 0.65;
    g_obs[0].w = 3;
    g_obs[0].y0 = 0.0;
    g_obs[0].y1 = 2.0;

    for (i = 0; i < 3; i++) {
        g_cloud_x[i] = (double)(rand() % (g_cols > 8 ? g_cols - 8 : 1));
        g_cloud_y[i] = 2 + rand() % 4;
    }
}

static void spawn_obstacle(void)
{
    Obstacle *o;
    double r;
    int can_bird = (g_score > 80.0);    /* птеродактиль: тільки присісти   */
    int can_tall = (g_score > 120.0);   /* високий кактус: треба стрибати  */
    int can_wide = (g_score > 500.0);   /* широкий кактус                  */

    if (g_nobs >= MAX_OBS) return;

    o = &g_obs[g_nobs++];
    o->x = (double)(g_cols - 1);
    r = (double)rand() / ((double)RAND_MAX + 1.0);

    /* Складніші перешкоди вмикаються поступово: на малій швидкості вони
       проходили б повз динозавра надто довго, і стрибок був би нереальний. */
    if (can_bird && r < 0.25) {
        o->kind = 3; o->w = 7; o->y0 = 2.0; o->y1 = 4.0;
    } else if (can_wide && r < 0.35) {
        o->kind = 2; o->w = 7; o->y0 = 0.0; o->y1 = 3.0;
    } else if (can_tall && r < 0.65) {
        o->kind = 1; o->w = 3; o->y0 = 0.0; o->y1 = 3.0;
    } else {
        o->kind = 0; o->w = 3; o->y0 = 0.0; o->y1 = 2.0;
    }
}

static int hit(const Obstacle *o)
{
    /* хітбокси навмисно вужчі за спрайти - так гра "прощає" дрібні помилки */
    double dx0 = g_dino_x + 2.0;
    double dx1 = g_dino_x + dino_w() - 2.0;
    double ox0 = o->x + 0.5;
    double ox1 = o->x + o->w - 0.5;
    double dy0 = g_dino_y + 0.15;
    double dy1 = g_dino_y + dino_h() - 0.15;

    if (dx0 >= ox1 || ox0 >= dx1) return 0;
    if (dy0 >= o->y1 || o->y0 >= dy1) return 0;
    return 1;
}

static void do_jump(void)
{
    if (g_on_ground) {
        g_dino_vy = 33.5;      /* ~7.5 рядка висоти, ~0.90 с у повітрі */
        g_on_ground = 0;
        g_duck = 0;
    }
}

static void die(void)
{
    g_state = ST_DEAD;
    if (g_score > g_hi) {
        g_hi = g_score;
        save_hi();
    }
}

static void update(double dt)
{
    int i, n;

    g_duck = (g_duck_held && g_on_ground) ? 1 : 0;

    /* вертикальна фізика */
    if (!g_on_ground) {
        g_dino_vy -= 74.0 * dt;
        g_dino_y += g_dino_vy * dt;
        if (g_dino_y <= 0.0) {
            g_dino_y = 0.0;
            g_dino_vy = 0.0;
            g_on_ground = 1;
        }
    }

    /* рахунок та швидкість */
    g_score += dt * 12.0;
    g_speed = 10.5 + g_score * 0.022;
    if (g_speed > 27.0) g_speed = 27.0;

    /* перешкоди */
    for (i = 0; i < g_nobs; i++) g_obs[i].x -= g_speed * dt;
    n = 0;
    for (i = 0; i < g_nobs; i++)
        if (g_obs[i].x + g_obs[i].w > -1.0) g_obs[n++] = g_obs[i];
    g_nobs = n;

    g_spawn_acc += g_speed * dt;
    if (g_spawn_acc >= g_next_gap) {
        g_spawn_acc = 0.0;
        g_next_gap = g_speed * (1.35 + (double)rand() / ((double)RAND_MAX + 1.0) * 0.9);
        spawn_obstacle();
    }

    /* хмаринки */
    for (i = 0; i < 3; i++) {
        g_cloud_x[i] -= g_speed * 0.18 * dt;
        if (g_cloud_x[i] < -7.0) {
            g_cloud_x[i] = (double)g_cols + (double)(rand() % 25);
            g_cloud_y[i] = 2 + rand() % 4;
        }
    }

    /* анімація */
    g_run_frame = ((int)(g_score * 0.7)) & 1;
    g_bird_frame = ((int)(g_score * 0.5)) & 1;

    /* зіткнення */
    for (i = 0; i < g_nobs; i++) {
        if (hit(&g_obs[i])) { die(); break; }
    }
}

/* ================================================================== малювання */

static void draw_world(void)
{
    int i, x, G;
    int off;

    G = g_rows - 2;                       /* рядок землі */

    /* земля + рухомі позначки */
    off = (int)(g_score * 1.1) % 23;
    for (x = 0; x < g_cols; x++)
        put(G, x, (((x + off) % 23) == 0) ? '^' : '_', A_GROUND);

    /* хмаринки (тільки під час гри, щоб не наїжджали на написи меню) */
    if (g_state == ST_PLAY) {
        for (i = 0; i < 3; i++) {
            int cx = (int)(g_cloud_x[i] + 0.5);
            if (g_cloud_y[i] + 1 < G - 3)
                blit_top(g_cloud_y[i], cx, SPR_CLOUD, 2, A_DIM);
        }
    }

    /* перешкоди */
    for (i = 0; i < g_nobs; i++) {
        Obstacle *o = &g_obs[i];
        int ox = (int)(o->x + 0.5);
        if (o->kind == 3)
            blit_top(G - 4, ox, SPR_BIRD[g_bird_frame], 2, A_BIRD);
        else if (o->kind == 0)
            blit_top(G - 2, ox, SPR_C1, 2, A_CACTUS);
        else if (o->kind == 1)
            blit_top(G - 3, ox, SPR_C2, 3, A_CACTUS);
        else
            blit_top(G - 3, ox, SPR_C3, 3, A_CACTUS);
    }

    /* динозавр */
    {
        int h = dino_h();
        int hop = (int)(g_dino_y + 0.5);
        int top = G - h - hop;
        if (g_duck)
            blit_top(top, (int)g_dino_x, SPR_DUCK, DUCK_H, A_DINO);
        else
            blit_top(top, (int)g_dino_x, SPR_RUN[g_run_frame], DINO_H, A_DINO);
    }
}

static void draw_hud(void)
{
    char hud[80];
    if (g_hi > 0.5)
        sprintf(hud, "HI %05d  %05d", (int)g_hi, (int)g_score);
    else
        sprintf(hud, "%05d", (int)g_score);
    put_text(0, g_cols - (int)strlen(hud) - 2, hud, A_HUD);
}

static void draw(void)
{
    int i, cy;
    char buf[96];

    for (i = 0; i < g_rows; i++) {
        memset(g_ch[i], ' ', (size_t)g_cols);
        memset(g_at[i], 0, (size_t)g_cols);
    }

    if (g_cols < MIN_W || g_rows < MIN_H) {
        cy = g_rows / 2;
        put_text_center(cy - 1, "TERMINAL IS TOO SMALL", A_ALERT);
        put_text_center(cy + 1, "please enlarge the window", A_DIM);
        sprintf(buf, "need %d x %d   now %d x %d", MIN_W, MIN_H, g_cols, g_rows);
        put_text_center(cy + 2, buf, A_DIM);
        render();
        return;
    }

    draw_world();
    draw_hud();

    cy = g_rows / 2;

    if (g_state == ST_TITLE) {
        put_text_center(cy - 6, "D I N O   R U N", A_DINO);
        put_text_center(cy - 4, "a tiny console game written in C", A_DIM);
        put_text_center(cy - 1, "SPACE / UP / W   - jump", A_HUD);
        put_text_center(cy + 0, "DOWN / S         - duck", A_HUD);
        put_text_center(cy + 1, "P                - pause", A_HUD);
        put_text_center(cy + 2, "Q / ESC          - quit", A_HUD);
        put_text_center(cy + 4, "press SPACE to start", A_ALERT);
    } else if (g_state == ST_DEAD) {
        put_text_center(cy - 3, "G A M E   O V E R", A_CACTUS);
        sprintf(buf, "score %d     best %d", (int)g_score, (int)g_hi);
        put_text_center(cy - 1, buf, A_HUD);
        put_text_center(cy + 2, "press R to play again, Q to quit", A_ALERT);
    } else if (g_state == ST_PAUSE) {
        put_text_center(cy, "P A U S E D", A_ALERT);
        put_text_center(cy + 2, "press P to continue", A_DIM);
    }

    render();
}

/* ==================================================================== введення */

static void restore_console(void)
{
    CONSOLE_CURSOR_INFO ci;
    if (g_out) {
        if (GetConsoleCursorInfo(g_out, &ci)) {
            ci.bVisible = TRUE;
            SetConsoleCursorInfo(g_out, &ci);
        }
        if (g_have_out_mode) SetConsoleMode(g_out, g_out_mode);
    }
    if (g_in && g_have_in_mode) SetConsoleMode(g_in, g_in_mode);
}

static void quit_game(void)
{
    restore_console();
    exit(0);
}

static BOOL WINAPI ctrl_handler(DWORD type)
{
    (void)type;
    restore_console();
    ExitProcess(0);
}

static void on_key(int vk, int down)
{
    if (!down) {
        if (vk == VK_DOWN || vk == 'S' || vk == 's') g_duck_held = 0;
        return;
    }

    if (vk == 'Q' || vk == 'q' || vk == VK_ESCAPE) quit_game();

    if (g_state == ST_TITLE) {
        if (vk == VK_SPACE || vk == VK_RETURN || vk == VK_UP || vk == 'W' || vk == 'w')
            g_state = ST_PLAY;
        return;
    }

    if (g_state == ST_DEAD) {
        if (vk == 'R' || vk == 'r' || vk == VK_SPACE || vk == VK_RETURN) {
            reset_game();
            g_state = ST_PLAY;
        }
        return;
    }

    if (vk == 'P' || vk == 'p') {
        g_state = (g_state == ST_PAUSE) ? ST_PLAY : ST_PAUSE;
        return;
    }

    if (g_state != ST_PLAY) return;

    if (vk == VK_SPACE || vk == VK_UP || vk == 'W' || vk == 'w') do_jump();
    if (vk == VK_DOWN || vk == 'S' || vk == 's') g_duck_held = 1;
}

static void read_input(void)
{
    INPUT_RECORD rec;
    DWORD n = 0;
    int guard = 0;

    while (guard++ < 64) {
        if (!PeekConsoleInputA(g_in, &rec, 1, &n) || n == 0) break;
        if (!ReadConsoleInputA(g_in, &rec, 1, &n) || n == 0) break;
        if (rec.EventType == KEY_EVENT)
            on_key((int)rec.Event.KeyEvent.wVirtualKeyCode,
                   rec.Event.KeyEvent.bKeyDown ? 1 : 0);
    }
}

static void setup_console(void)
{
    CONSOLE_CURSOR_INFO ci;
    DWORD m;

    g_color = 0;
    if (GetConsoleMode(g_out, &m)) {
        g_out_mode = m;
        g_have_out_mode = 1;
        if (SetConsoleMode(g_out, m | ENABLE_PROCESSED_OUTPUT |
                                    ENABLE_VIRTUAL_TERMINAL_PROCESSING))
            g_color = 1;                       /* кольори підтримуються */
        else
            SetConsoleMode(g_out, m | ENABLE_PROCESSED_OUTPUT);
    }
    if (GetConsoleMode(g_in, &m)) {
        g_in_mode = m;
        g_have_in_mode = 1;
        m &= ~(ENABLE_LINE_INPUT | ENABLE_ECHO_INPUT |
               ENABLE_QUICK_EDIT_MODE | ENABLE_MOUSE_INPUT);
        m |= ENABLE_EXTENDED_FLAGS;
        SetConsoleMode(g_in, m);
    }
    if (GetConsoleCursorInfo(g_out, &ci)) {
        ci.bVisible = FALSE;
        SetConsoleCursorInfo(g_out, &ci);
    }
    SetConsoleTitleA("Dino Run");
    SetConsoleCtrlHandler(ctrl_handler, TRUE);
    query_size();
}

/* ======================================================================== main */

int main(void)
{
    double last, acc;
    int steps;

    g_out = GetStdHandle(STD_OUTPUT_HANDLE);
    g_in = GetStdHandle(STD_INPUT_HANDLE);

    if (g_out == NULL || g_out == INVALID_HANDLE_VALUE) {
        printf("Dino Run needs a Windows console (cmd.exe / Windows Terminal).\n");
        return 1;
    }

    setup_console();
    srand((unsigned)time(NULL) ^ (unsigned)GetTickCount());

    load_hi();
    reset_game();
    g_state = ST_TITLE;

    last = now_sec();
    acc = 0.0;

    for (;;) {
        query_size();       /* якщо вікно змінили - підлаштовуємось */
        read_input();

        if (g_state == ST_PLAY) {
            double t = now_sec();
            double dt = t - last;
            last = t;
            if (dt > 0.25) dt = 0.25;
            acc += dt;
            steps = 0;
            while (acc >= TICK && steps < 6) {
                update(TICK);
                acc -= TICK;
                steps++;
                if (g_state != ST_PLAY) break;
            }
            if (acc > TICK) acc = 0.0;
        } else {
            last = now_sec();
            acc = 0.0;
        }

        draw();
        Sleep(1);
    }
}
