#include <stdio.h>
#include "array_utils.h"

int main() {
    const int arr[] = {1, 3, 5, 7, 9, 11};
    const int n = sizeof(arr) / sizeof(arr[0]);

    int target = 7;
    int index = binary_search(arr, n, target);

    if (index != -1)
        printf("Found %d at index %d\n", target, index);
    else
        printf("%d not found\n", target);

    return 0;
}
