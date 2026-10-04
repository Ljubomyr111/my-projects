#include <stdio.h>
#include <math.h>

int main(void) {
    int task;

    printf("Enter task number (1 or 2): ");
    if (scanf_s("%d", &task) != 1) {
        printf("Error reading task number.\n");
        return 1;
    }

    if (task == 1) {
        float number;

        printf("Enter a float number: ");
        if (scanf_s("%f", &number) != 1) {
            printf("Error reading input.\n");
            return 1;
        }

        unsigned int* zamina = (unsigned int*)&number;
        unsigned int maska = 1U << 31;

        *zamina = *zamina ^ maska;

        printf("Float with reversed sign: %.3f\n", number);
    }
    else if (task == 2) {
        double max_mantissa_float = 2.0 - pow(2.0, -23.0);
        double max_mantissa_double = 2.0 - pow(2.0, -52.0);

        printf("Max mantissa for float (32 bits):  %.23lf\n", max_mantissa_float);
        printf("Max mantissa for double (64 bits): %.52lf\n", max_mantissa_double);
    }
    else {
        printf("Invalid task number.\n");
    }

    return 0;
}