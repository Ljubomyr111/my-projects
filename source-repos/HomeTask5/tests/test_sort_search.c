/*
 * Unit tests for bubble_sort() and binary_search_loop().
 *
 * Build this file together with src/sort_search.c. The exit code is 0 only if
 * every check passes, so the test can be plugged into CTest or CI as is.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "sort_search.h"

#define LEN(a) ((int)(sizeof(a) / sizeof((a)[0])))

static int checks_run = 0;
static int checks_failed = 0;

#define CHECK(condition)                                                       \
    do {                                                                       \
        checks_run++;                                                          \
        if (!(condition)) {                                                    \
            checks_failed++;                                                   \
            printf("    FAILED %s:%d: %s\n", __FILE__, __LINE__, #condition);  \
        }                                                                      \
    } while (0)

#define RUN_TEST(test)                                                         \
    do {                                                                       \
        printf("[ RUN ] %s\n", #test);                                         \
        test();                                                                \
    } while (0)

static int arrays_equal(const int *a, const int *b, int size)
{
    for (int i = 0; i < size; i++) {
        if (a[i] != b[i]) {
            return 0;
        }
    }
    return 1;
}

/* ------------------------------ bubble_sort ------------------------------ */

static void test_bubble_sort_sorts_unsorted_array(void)
{
    int data[]     = {5, 2, 9, 1, 7};
    int expected[] = {1, 2, 5, 7, 9};

    bubble_sort(data, LEN(data));

    CHECK(arrays_equal(data, expected, LEN(expected)));
}

static void test_bubble_sort_keeps_sorted_array_unchanged(void)
{
    int data[]     = {1, 2, 3, 4, 5};
    int expected[] = {1, 2, 3, 4, 5};

    bubble_sort(data, LEN(data));

    CHECK(arrays_equal(data, expected, LEN(expected)));
}

static void test_bubble_sort_sorts_reversed_array(void)
{
    int data[]     = {9, 7, 5, 3, 1};
    int expected[] = {1, 3, 5, 7, 9};

    bubble_sort(data, LEN(data));

    CHECK(arrays_equal(data, expected, LEN(expected)));
}

static void test_bubble_sort_handles_duplicates(void)
{
    int data[]     = {4, 1, 4, 2, 1, 4};
    int expected[] = {1, 1, 2, 4, 4, 4};

    bubble_sort(data, LEN(data));

    CHECK(arrays_equal(data, expected, LEN(expected)));
}

static void test_bubble_sort_handles_negative_numbers(void)
{
    int data[]     = {3, -7, 0, -1, 12, -7};
    int expected[] = {-7, -7, -1, 0, 3, 12};

    bubble_sort(data, LEN(data));

    CHECK(arrays_equal(data, expected, LEN(expected)));
}

static void test_bubble_sort_single_element(void)
{
    int data[]     = {42};
    int expected[] = {42};

    bubble_sort(data, LEN(data));

    CHECK(arrays_equal(data, expected, LEN(expected)));
}

static void test_bubble_sort_empty_array(void)
{
    int data[] = {1}; /* must stay untouched: size is 0 */

    bubble_sort(data, 0);

    CHECK(data[0] == 1);
}

static void test_bubble_sort_ignores_elements_beyond_size(void)
{
    int data[]     = {5, 3, 1, -100}; /* only the first 3 elements are sorted */
    int expected[] = {1, 3, 5, -100};

    bubble_sort(data, 3);

    CHECK(arrays_equal(data, expected, LEN(expected)));
}

/* --------------------------- binary_search_loop --------------------------- */

static void test_binary_search_finds_first_middle_and_last(void)
{
    int data[] = {2, 4, 6, 8, 10, 12, 14};

    CHECK(binary_search_loop(data, LEN(data), 2)  == 0); /* first  */
    CHECK(binary_search_loop(data, LEN(data), 8)  == 3); /* middle */
    CHECK(binary_search_loop(data, LEN(data), 14) == 6); /* last   */
}

static void test_binary_search_finds_every_element(void)
{
    int data[] = {-8, -3, 0, 5, 11, 20, 31, 47, 58, 99}; /* even length */

    for (int i = 0; i < LEN(data); i++) {
        CHECK(binary_search_loop(data, LEN(data), data[i]) == i);
    }
}

static void test_binary_search_returns_minus_one_when_missing(void)
{
    int data[] = {2, 4, 6, 8, 10};

    CHECK(binary_search_loop(data, LEN(data), 1)  == -1); /* below the minimum */
    CHECK(binary_search_loop(data, LEN(data), 11) == -1); /* above the maximum */
    CHECK(binary_search_loop(data, LEN(data), 5)  == -1); /* between two values */
}

static void test_binary_search_single_element(void)
{
    int data[] = {7};

    CHECK(binary_search_loop(data, LEN(data), 7) == 0);
    CHECK(binary_search_loop(data, LEN(data), 8) == -1);
}

static void test_binary_search_empty_array(void)
{
    int data[] = {1}; /* never read: size is 0 */

    CHECK(binary_search_loop(data, 0, 1) == -1);
}

static void test_binary_search_with_duplicates(void)
{
    int data[] = {1, 3, 3, 3, 3, 8};
    int index = binary_search_loop(data, LEN(data), 3);

    CHECK(index >= 1 && index <= 4); /* any of the equal elements is fine */
}

static void test_binary_search_ignores_elements_beyond_size(void)
{
    int data[] = {1, 2, 3, 4}; /* only the first 3 elements are searched */

    CHECK(binary_search_loop(data, 3, 3) == 2);
    CHECK(binary_search_loop(data, 3, 4) == -1);
}

/* ------------------------- sort + search together ------------------------- */

static int compare_ints(const void *a, const void *b)
{
    int x = *(const int *)a;
    int y = *(const int *)b;

    return (x > y) - (x < y);
}

/* Compares bubble_sort() with qsort() and binary_search_loop() with a plain
   linear scan on many random arrays (fixed seed, so the test is repeatable). */
static void test_sort_then_search_on_random_arrays(void)
{
    enum { SIZE = 10, ITERATIONS = 200, MAX_VALUE = 30 };

    srand(12345);

    for (int iteration = 0; iteration < ITERATIONS; iteration++) {
        int data[SIZE];
        int reference[SIZE];

        for (int i = 0; i < SIZE; i++) {
            data[i] = rand() % (MAX_VALUE + 1);
        }
        memcpy(reference, data, sizeof(data));

        bubble_sort(data, SIZE);
        qsort(reference, SIZE, sizeof(int), compare_ints);
        CHECK(arrays_equal(data, reference, SIZE));

        for (int value = -1; value <= MAX_VALUE + 1; value++) {
            int present = 0;
            for (int i = 0; i < SIZE; i++) {
                if (data[i] == value) {
                    present = 1;
                }
            }

            int index = binary_search_loop(data, SIZE, value);

            if (present) {
                CHECK(index >= 0 && index < SIZE && data[index] == value);
            } else {
                CHECK(index == -1);
            }
        }
    }
}

int main(void)
{
    RUN_TEST(test_bubble_sort_sorts_unsorted_array);
    RUN_TEST(test_bubble_sort_keeps_sorted_array_unchanged);
    RUN_TEST(test_bubble_sort_sorts_reversed_array);
    RUN_TEST(test_bubble_sort_handles_duplicates);
    RUN_TEST(test_bubble_sort_handles_negative_numbers);
    RUN_TEST(test_bubble_sort_single_element);
    RUN_TEST(test_bubble_sort_empty_array);
    RUN_TEST(test_bubble_sort_ignores_elements_beyond_size);

    RUN_TEST(test_binary_search_finds_first_middle_and_last);
    RUN_TEST(test_binary_search_finds_every_element);
    RUN_TEST(test_binary_search_returns_minus_one_when_missing);
    RUN_TEST(test_binary_search_single_element);
    RUN_TEST(test_binary_search_empty_array);
    RUN_TEST(test_binary_search_with_duplicates);
    RUN_TEST(test_binary_search_ignores_elements_beyond_size);

    RUN_TEST(test_sort_then_search_on_random_arrays);

    printf("\n%d checks, %d failed\n", checks_run, checks_failed);
    return checks_failed == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
