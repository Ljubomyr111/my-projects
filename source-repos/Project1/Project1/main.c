#include <stdio.h>
#include <stdbool.h>

bool is_palindrome(unsigned int n) {
    int left = 31;
    int right = 0;

    while (left > right && !((n >> left) & 1)) {
        left--;
    }

    while (left > right) {
        if (((n >> left) & 1) != ((n >> right) & 1)) {
            return false;
        }
        left--;
        right++;
    }

    return true;
}

int main() {
    unsigned int number;

    printf("Enter a number: ");
    scanf_s("%u", &number);

    if (is_palindrome(number)) {
        printf("%u IS palindrome\n", number);
    }
    else {
        printf("is NOT palindrome\n", number);
    }

    return 0;
}