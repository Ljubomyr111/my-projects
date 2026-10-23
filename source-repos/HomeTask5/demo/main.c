/*
 * Home task #5 - demo program (functions).
 *
 * 1) Task 2: 10 random numbers, bubble sort and binary search in a loop.
 * 2) Additional task: 10x10 random array [0..100]; if an element is 0,
 *    its row and column are set to 0.
 *
 * Complexity:
 *   Task 2: bubble_sort O(n^2), binary_search_loop O(log n).
 *   Additional task: time O(n^2), space O(n).
 */
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#include "sort_search.h"

#define ARRAY_SIZE  10
#define MIN_VALUE   1
#define MAX_VALUE   50
#define N           10
#define MATRIX_MAX  100

static void fill_random(int *arr, int size)
{
    for (int i = 0; i < size; i++) {
        arr[i] = MIN_VALUE + rand() % (MAX_VALUE - MIN_VALUE + 1);
    }
}

static void print_array(const int *arr, int size)
{
    printf("[");
    for (int i = 0; i < size; i++) {
        printf("%d%s", arr[i], (i < size - 1) ? ", " : "");
    }
    printf("]\n");
}

/* -------------------------- Task 2 -------------------------- */

static void task2(void)
{
    int numbers[ARRAY_SIZE];
    int target;

    fill_random(numbers, ARRAY_SIZE);

    printf("Array:        ");
    print_array(numbers, ARRAY_SIZE);

    printf("Enter a value to search for: ");
    if (scanf("%d", &target) != 1) {
        printf("Invalid input.\n");
        return;
    }

    bubble_sort(numbers, ARRAY_SIZE);
    printf("Sorted array: ");
    print_array(numbers, ARRAY_SIZE);

    int index = binary_search_loop(numbers, ARRAY_SIZE, target);
    if (index != -1) {
        printf("The array contains %d (index %d in the sorted array).\n",
               target, index);
    } else {
        printf("The array does not contain %d.\n", target);
    }
}

/* --------------------- Additional task ---------------------- */

static void fill_matrix(int a[N][N])
{
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            a[i][j] = rand() % (MATRIX_MAX + 1);  /* 0..100 */
        }
    }
}

static void print_matrix(const int a[N][N], const char *title)
{
    printf("%s\n", title);
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            printf("%4d", a[i][j]);
        }
        printf("\n");
    }
}

static void zero_rows_and_columns(int a[N][N])
{
    int rows[N] = { 0 };
    int cols[N] = { 0 };

    /* Remember which rows and columns contain a zero */
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            if (a[i][j] == 0) {
                rows[i] = 1;
                cols[j] = 1;
            }
        }
    }

    /* Zero out the marked rows and columns */
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            if (rows[i] || cols[j]) {
                a[i][j] = 0;
            }
        }
    }
}

static void additional_task(void)
{
    int a[N][N];

    fill_matrix(a);
    a[rand() % N][rand() % N] = 0;  /* ensure at least one zero for the demo */

    print_matrix(a, "Original array:");
    zero_rows_and_columns(a);
    print_matrix(a, "\nArray after zeroing rows and columns:");
}

/* ---------------------------- menu -------------------------- */

int main(void)
{
    int choice;

    srand((unsigned int)time(NULL));

    do {
        printf("\n1 - Task 2: bubble sort + binary search\n");
        printf("2 - Additional task: 2D array, zero rows and columns\n");
        printf("0 - exit\n");
        printf("Your choice: ");

        if (scanf("%d", &choice) != 1) {
            break;
        }

        switch (choice) {
        case 1:
            task2();
            break;
        case 2:
            additional_task();
            break;
        case 0:
            break;
        default:
            printf("Wrong choice.\n");
            break;
        }
    } while (choice != 0);

    return 0;
}
