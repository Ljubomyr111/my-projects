/*
 * Practical 5 - Static arrays and strings
 * Introduction to Programming
 *
 * Реалізовано всі частини завдання з конспекту P5:
 *   1) одновимірний статичний масив, заповнений випадковими числами;
 *   2) двовимірний масив N x N;
 *   3) Practical task #1 - ВИПРАВЛЕНА програма пошуку найчастішого символу;
 *   4) Practical task #2 - 1000 випадкових чисел [1..10], підрахунок
 *      входжень і виведення за спаданням + оцінка складності Big-O.
 *
 * Збірка у Visual Studio 2026: відкрити Practical5.slnx, натиснути F5.
 * Збірка через gcc:            gcc main.c -o practical5
 *
 * Примітка щодо сумісності: у конспекті розмір масиву задається змінною
 * (int arr[N]) - це VLA, які MSVC не підтримує. Тому тут використано
 * масив фіксованої місткості з перевіркою межі введеного N.
 */

/* Стандартний C замість scanf_s, щоб код збирався і в MSVC, і в gcc. */
#define _CRT_SECURE_NO_WARNINGS

#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define MAX_N      1000   /* максимум для одновимірного масиву */
#define MAX_N2D    100    /* максимум для N x N: 100*100*4 Б = 40 КБ */
#define MAX_STR_LEN 1000  /* як у конспекті */
#define ASCII_SYMBOLS 128 /* як у конспекті */

#define TASK2_N   1000    /* Practical task #2: N = 1000 */
#define TASK2_MIN    1
#define TASK2_MAX   10

/* ------------------------------------------------------------------ */
/* 1) Одновимірний масив: N вводить користувач, значення 0..4          */
/* ------------------------------------------------------------------ */
static void task1_array_1d(void)
{
    int n = 0;
    int arr[MAX_N];

    printf("Enter the size of the array (1..%d): ", MAX_N);
    if (scanf("%d", &n) != 1 || n < 1 || n > MAX_N) {
        printf("Invalid size.\n");
        return;
    }

    /* Initialize the array with random values in range 0-4 */
    for (int i = 0; i < n; i++) {
        arr[i] = rand() % 5;
    }

    printf("Array elements are:\n");
    for (int i = 0; i < n; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");
}

/* ------------------------------------------------------------------ */
/* 2) Двовимірний масив N x N: arr[i][j] = i + j                       */
/* ------------------------------------------------------------------ */
static void task2_array_2d(void)
{
    static int arr[MAX_N2D][MAX_N2D];
    int n = 0;

    printf("Enter the size of the 2D array (NxN), 1..%d: ", MAX_N2D);
    if (scanf("%d", &n) != 1 || n < 1 || n > MAX_N2D) {
        printf("Invalid size.\n");
        return;
    }

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            arr[i][j] = i + j;
        }
    }

    printf("2D Array elements are:\n");
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            printf("%d ", arr[i][j]);
        }
        printf("\n");
    }
}

/* ------------------------------------------------------------------ */
/* 3) Practical task #1 - найчастіший символ у рядку                   */
/*                                                                     */
/* ВИПРАВЛЕННЯ: у конспекті масив частот оголошено як                   */
/*     int frequency[number_of_ascii_symbols];                          */
/* тобто БЕЗ ініціалізації. Елементи містять сміття зі стека, а отже    */
/* frequency[...]++ рахує від випадкових початкових значень.            */
/* Достатньо занулити масив - і алгоритм стає правильним.               */
/* ------------------------------------------------------------------ */
static void task3_most_popular_symbol(void)
{
    char str[MAX_STR_LEN];
    int frequency[ASCII_SYMBOLS] = { 0 };   /* <-- ВИПРАВЛЕННЯ */
    int max_freq = 0;
    char most_popular = '\0';

    printf("Enter a string: ");
    if (scanf("%999s", str) != 1) {
        printf("No input.\n");
        return;
    }
    getchar();

    /* Calculate the frequency of each character */
    for (int i = 0; str[i] != '\0'; i++) {
        frequency[(unsigned char)str[i]]++;
    }

    /* Find the most popular character */
    for (int i = 0; i < ASCII_SYMBOLS; i++) {
        if (frequency[i] > max_freq) {
            max_freq = frequency[i];
            most_popular = (char)i;
        }
    }

    printf("Most popular symbol: '%c' (%d times)\n", most_popular, max_freq);
}

/* ------------------------------------------------------------------ */
/* 4) Practical task #2 - 1000 чисел [1..10], виведення за спаданням   */
/* ------------------------------------------------------------------ */
typedef struct {
    int number;
    int count;
} CountEntry;

static int cmp_by_count_desc(const void *a, const void *b)
{
    const CountEntry *x = (const CountEntry *)a;
    const CountEntry *y = (const CountEntry *)b;

    if (y->count != x->count) {
        return y->count - x->count;   /* більша кількість - вище */
    }
    return x->number - y->number;     /* за рівної кількості - менший номер */
}

static void task4_number_counts(void)
{
    int counts[TASK2_MAX + 1] = { 0 };
    CountEntry entries[TASK2_MAX];
    int k = 0;

    for (int i = 0; i < TASK2_N; i++) {
        int value = TASK2_MIN + rand() % (TASK2_MAX - TASK2_MIN + 1);
        counts[value]++;
    }

    for (int v = TASK2_MIN; v <= TASK2_MAX; v++) {
        entries[k].number = v;
        entries[k].count = counts[v];
        k++;
    }

    qsort(entries, (size_t)k, sizeof(entries[0]), cmp_by_count_desc);

    for (int i = 0; i < k; i++) {
        printf("Number %d: %d times\n", entries[i].number, entries[i].count);
    }

    printf("\nComplexity:\n");
    printf("  time  O(N + K log K) = O(N)   (N = %d, K = %d)\n", TASK2_N, TASK2_MAX);
    printf("  space O(K)\n");
    printf("  Counting pass over the array is O(N); sorting only K = 10\n");
    printf("  counters is constant work, so the algorithm is linear in N.\n");
}

/* ------------------------------------------------------------------ */
static void print_menu(void)
{
    printf("\n=== Practical 5 - Static arrays and strings ===\n");
    printf("  1 - 1D array of N random values\n");
    printf("  2 - 2D array N x N\n");
    printf("  3 - Practical task #1: most popular symbol\n");
    printf("  4 - Practical task #2: counts in descending order\n");
    printf("  0 - exit\n");
    printf("Your choice: ");
}

int main(void)
{
    srand((unsigned)time(NULL));

    for (;;) {
        int choice = 0;

        print_menu();
        if (scanf("%d", &choice) != 1) {
            printf("Invalid input.\n");
            return 1;
        }

        switch (choice) {
        case 1:
            task1_array_1d();
            break;
        case 2:
            task2_array_2d();
            break;
        case 3:
            task3_most_popular_symbol();
            break;
        case 4:
            task4_number_counts();
            break;
        case 0:
            printf("Bye.\n");
            return 0;
        default:
            printf("Unknown option.\n");
            break;
        }
    }
}
