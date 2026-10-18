/*
 * Practical 5 - Practical task #2
 *
 * Generate 1000 random integers in the range [1..10], count how many times
 * each number occurs and print the numbers in descending order.
 *
 * Complexity: time O(N), space O(1) (only 10 counters).
 */

#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define N 1000

int main(void)
{
    int counts[11] = { 0 };  /* counts[1]..counts[10] */
    int i, j, best;

    srand((unsigned int)time(NULL));

    for (i = 0; i < N; i++) {
        int value = rand() % 10 + 1;  /* 1..10 */
        counts[value]++;
    }

    /* Print numbers in descending order of their occurrences */
    for (i = 0; i < 10; i++) {
        best = 1;
        for (j = 2; j <= 10; j++) {
            if (counts[j] > counts[best]) {
                best = j;
            }
        }
        printf("Number %d: %d times\n", best, counts[best]);
        counts[best] = -1;  /* mark as printed */
    }

    return 0;
}
