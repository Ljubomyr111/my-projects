/*
 * Practical 4 - Task #2 (INTERACTIVE version)
 * Introduction to Programming
 *
 * You type your own x and epsilon, and the program compares
 * the two square-root algorithms (exhaustive vs bisection).
 *
 * Compile (gcc):  gcc sqrt_interactive.c -o sqrt_interactive -lm
 * Compile (MSVC): cl sqrt_interactive.c
 */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

 /* 1) Exhaustive search (Lecture 4, slide #8) */
double squareRootExhaustive(double x, double epsilon, long* iterations) {
    double step = epsilon * epsilon;
    double ans = 0.0;
    long i = 0;

    while (fabs(ans * ans - x) >= epsilon && ans * ans <= x) {
        ans += step;
        ++i;
    }

    if (iterations) *iterations = i;
    return ans;
}

/* 2) Bisection search (Lecture 4, slide #45) */
double squareRootBisection(double x, double epsilon, long* iterations) {
    double low = 0.0;
    double high = (x > 1.0) ? x : 1.0;
    double mid = (low + high) / 2.0;
    long i = 0;

    while (fabs(mid * mid - x) >= epsilon) {
        if (mid * mid > x) high = mid;
        else               low = mid;
        mid = (low + high) / 2.0;
        ++i;
    }

    if (iterations) *iterations = i;
    return mid;
}

/* run a function, measure its time, return answer + iterations + seconds */
double measure(double x, double eps, double (*fn)(double, double, long*),
    long* iters, double* seconds) {
    clock_t start = clock();
    double result = fn(x, eps, iters);
    clock_t end = clock();
    *seconds = (double)(end - start) / CLOCKS_PER_SEC;
    return result;
}

/* read one non-negative / positive double from the user (with retry) */
double readDouble(const char* prompt, int mustBePositive) {
    double value;
    while (1) {
        printf("%s", prompt);
        if (scanf("%lf", &value) == 1 &&
            (!mustBePositive || value > 0.0) &&
            (mustBePositive || value >= 0.0)) {
            while (getchar() != '\n');  /* clear the rest of the line */
            return value;
        }
        printf("  Invalid input, try again.\n");
        while (getchar() != '\n');
    }
}

int main(void) {
    printf("=====================================================\n");
    printf("  Square root: exhaustive search vs bisection search\n");
    printf("=====================================================\n\n");

    char again;
    do {
        double x = readDouble("Enter x (number, x >= 0):      ", 0);
        double eps = readDouble("Enter epsilon (precision > 0): ", 1);

        /* quick estimate of the work each algorithm will do */
        double estExh = sqrt(x) / (eps * eps);
        double estBis = log2(sqrt(x) / eps);

        printf("\nEstimated iterations:\n");
        printf("  exhaustive ~ %.0f\n", estExh);
        printf("  bisection  ~ %.0f\n\n", estBis);

        int runExh = 1;
        if (estExh > 300000000.0) {
            printf("WARNING: exhaustive needs ~%.0f iterations (very slow).\n", estExh);
            printf("Run exhaustive anyway? (y/n): ");
            char c;
            scanf(" %c", &c);
            while (getchar() != '\n');
            runExh = (c == 'y' || c == 'Y');
            printf("\n");
        }

        long it1 = 0, it2 = 0;
        double sec1 = 0.0, sec2 = 0.0;

        if (runExh) {
            double a1 = measure(x, eps, squareRootExhaustive, &it1, &sec1);
            printf("--- Exhaustive ---\n");
            printf("  answer     = %.6f\n", a1);
            printf("  iterations = %ld\n", it1);
            printf("  time       = %.4f s\n\n", sec1);
        }
        else {
            printf("--- Exhaustive ---\n  (skipped)\n\n");
        }

        double a2 = measure(x, eps, squareRootBisection, &it2, &sec2);
        printf("--- Bisection ---\n");
        printf("  answer     = %.6f\n", a2);
        printf("  iterations = %ld\n", it2);
        printf("  time       = %.4f s\n\n", sec2);

        if (runExh && sec2 > 0.0) {
            printf(">>> Exhaustive is %.0f times slower than bisection.\n",
                sec1 / sec2);
        }
        else if (runExh) {
            printf(">>> Bisection is effectively instant (under 1 ms).\n");
        }

        printf("\nTest another pair? (y/n): ");
        scanf(" %c", &again);
        while (getchar() != '\n');
        printf("\n");
    } while (again == 'y' || again == 'Y');

    return 0;
}
