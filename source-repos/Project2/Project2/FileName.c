#include <stdio.h>
#include <stdbool.h>

int number;
int dil = 0;

bool isPrime(int n) {
    n = 1;
    dil = 0;

    while (number >= n) {
        if (number % n == 0) {
            dil++; 
        }
        n++;
    }

    if (dil > 2) {
        return false;
    }
    else {
        return true;
    }
}

int main() {
    printf("Enter a number: ");
    scanf_s("%d", &number);

    if (isPrime(1)) {
        printf("prime\n", number);
    }
    else {
        printf("NOT prime\n", number);
    }

    return 0;
}