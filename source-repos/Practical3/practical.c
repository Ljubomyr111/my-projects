/*
 * Practical 3 - Task #2
 * Introduction to Programming
 *
 * Complete practical.c
 *
 * The program continuously asks the user for a letter of the English
 * alphabet and prints the position of that letter in the alphabet.
 * As soon as the input is not an English letter, the program stops.
 *
 * Example:
 *   Enter a letter: b
 *   The letter b is at position 2 in the alphabet.
 *   Enter a letter: z
 *   The letter z is at position 26 in the alphabet.
 *   Enter a letter: 2
 *   Invalid input. Stopping...
 *
 * Compile:
 *   gcc -g practical.c -o practical.exe
 */

#include <stdio.h>
#include <ctype.h>
#include <stdbool.h>

/*
 * Returns true when c is a letter of the English alphabet.
 * isalpha() alone is not enough: in some locales it also accepts
 * non-ASCII letters (for example Cyrillic ones), but the task asks
 * only for English letters.
 */
static bool isEnglishLetter(char c) {
    return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z');
}

int main(void) {
    while (true) {
        char letter;

        printf("Enter a letter: ");
        fflush(stdout);

        if (scanf(" %c", &letter) != 1) {
            /* End of input (Ctrl+Z / Ctrl+D) or read error. */
            printf("Invalid input. Stopping...\n");
            break;
        }

        if (!isalpha((unsigned char)letter) || !isEnglishLetter(letter)) {
            printf("Invalid input. Stopping...\n");
            break;
        }

        /* For lowercase letters ASCII codes follow the alphabet order:
           'a' = 97, 'b' = 98, ... so position = letter - 'a' + 1. */
        int position = tolower((unsigned char)letter) - 'a' + 1;
        printf("The letter %c is at position %d in the alphabet.\n", letter, position);
    }

    return 0;
}
