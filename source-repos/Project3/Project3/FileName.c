/*
 * Practical 4 — Task #2
 * Introduction to Programming
 *
 * Compare two square-root algorithms:
 *   1) exhaustive search  (Lecture 4, slide #8)
 *   2) bisection search   (Lecture 4, slide #45)
 *
 * Compile (gcc):  gcc sqrt_compare.c -o sqrt_compare -lm
 * Compile (MSVC): cl sqrt_compare.c
 *
 * NOTE: the lecture's exhaustive search calls exit(1) when the answer
 * "overshoots" x (a floating-point edge case). Here we RETURN the value
 * instead of exiting, so the timing comparison runs on arbitrary inputs.
 * The search loop itself is identical to the slides.
 */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

 /* ------------------------------------------------------------------ */
 /* 1) Exhaustive search — guesses every value with a small step        */
 /*    step = epsilon * epsilon  (as in the lecture slides)             */
 /* ------------------------------------------------------------------ */
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

/* ------------------------------------------------------------------ */
/* 2) Bisection search — repeatedly halve the search interval          */
/* ------------------------------------------------------------------ */
double squareRootBisection(double x, double epsilon, long* iterations) {
    double low = 0.0;
    double high = (x > 1.0) ? x : 1.0;
    double mid = (low + high) / 2.0;
    long i = 0;

    while (fabs(mid * mid - x) >= epsilon) {
        if (mid * mid > x) {
            high = mid;          /* search the lower half */
        }
        else {
            low = mid;           /* search the upper half */
        }
        mid = (low + high) / 2.0;
        ++i;
    }

    if (iterations) *iterations = i;
    return mid;
}

/* ------------------------------------------------------------------ */
/* helper: measure running time of one function                        */
/* ------------------------------------------------------------------ */
double timeFunction(double x, double epsilon, double (*fn)(double, double, long*), long* iters) {
    clock_t start = clock();
    double result = fn(x, epsilon, iters);
    clock_t end = clock();
    (void)result;
    return (double)(end - start) / CLOCKS_PER_SEC;
}

int main(void) {
    struct { double x; double eps; } cases[] = {
        { 100.0,    0.01  },
        { 1000.0,   0.01  },
        { 1000.0,   0.001 },
        { 10000.0,  0.001 },
        { 100000.0, 0.01  },
        { 2.0,      0.0001 },
    };

    int n = sizeof(cases) / sizeof(cases[0]);

    printf("%-9s %-9s | %-13s %-12s | %-13s %-12s | %s\n",
        "x", "epsilon",
        "exh_time(s)", "exh_iters",
        "bis_time(s)", "bis_iters",
        "ratio");
    printf("-----------------------------------------------------------------------------------\n");

    for (int i = 0; i < n; i++) {
        double x = cases[i].x;
        double eps = cases[i].eps;
        long exh_iters = 0, bis_iters = 0;

        double t_exh = timeFunction(x, eps, squareRootExhaustive, &exh_iters);
        double t_bis = timeFunction(x, eps, squareRootBisection, &bis_iters);

        printf("%-9g %-9g | %-13.6f %-12ld | %-13.6f %-12ld | ",
            x, eps, t_exh, exh_iters, t_bis, bis_iters);
        if (t_bis > 0.0) {
            printf("%.0fx\n", t_exh / t_bis);
        }
        else {
            printf("bis ~0 s\n");
        }
    }

    printf("\nWhere exhaustive search becomes impractical:\n");
    printf("  iterations_exhaustive ~ sqrt(x) / epsilon^2\n");
    printf("  iterations_bisection  ~ log2(sqrt(x) / epsilon)\n");
    printf("  e.g. x=1000, epsilon=0.0001 -> exhaustive ~ %.0e iterations (too slow),\n",
        sqrt(1000.0) / (0.0001 * 0.0001));
    printf("       while bisection needs only ~ %.0f iterations.\n",
        ceil(log2(sqrt(1000.0) / 0.0001)));

    return 0;
}