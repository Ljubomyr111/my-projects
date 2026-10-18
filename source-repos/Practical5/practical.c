#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>

void initialize_and_print_array(int N)
{
    // Ask the user for the size of the array
    printf("Enter the size of the array: ");
    scanf("%d", &N);

    // Declare an array of size N
    int arr[N];

    // Initialize the array with some random values in range 0-4
    for (int i = 0; i < N; i++) {
        arr[i] = rand() % 5;  // Initializing the array
    }

    // Print the array
    printf("Array elements are:\n");
    for (int i = 0; i < N; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");  // New line after printing the array
}

void initialize_and_print_2D_array(int N)
{
    printf("Enter the size of the 2D array (NxN): ");
    scanf("%d", &N);
    // Declare a 2D array of size N x N
    int arr[N][N];
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            arr[i][j] = i + j;  // Initializing the array
        }
    }
    printf("2D Array elements are:\n");
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            printf("%d ", arr[i][j]);
        }
        printf("\n");  // Move to the next row after printing each row
    }
}

void find_most_popular_character()
{
    const int max_str_len = 1000;
    char str[max_str_len];
    printf("Enter a string: ");
    scanf("%s", str); 
    getchar();
    
    const int  number_of_ascii_symbols = 128;
    int frequency[number_of_ascii_symbols];
    /* FIX: the frequency array must be initialized with zeros before counting.
       (It is a variable-length array here, so it cannot use = { 0 }.) */
    memset(frequency, 0, sizeof frequency);
    for (int i = 0; str[i] != '\0'; i++) { // Calculate the frequency of each character
        frequency[(unsigned char)str[i]]++;
    }
    int max_freq = 0;
    char most_popular = '\0';   /* initialize to avoid a compiler warning */
    for (int i = 0; i < number_of_ascii_symbols; i++) {
        if (frequency[i] > max_freq) {    // Find the most popular character
            max_freq = frequency[i];
            most_popular = i;
        }
    }
    printf("The most popular character is '%c' with frequency %d\n", most_popular, max_freq);
}



int main() {
    initialize_and_print_array(5);
    initialize_and_print_2D_array(3);
    find_most_popular_character();

    return 0;
}
