#include "sort_search.h"

void bubble_sort(int *arr, int size)
{
    for (int pass = 0; pass < size - 1; pass++) {
        int swapped = 0;

        /* After every pass the largest remaining element is in its final
           place, so the inner loop can stop one element earlier each time. */
        for (int i = 0; i < size - 1 - pass; i++) {
            if (arr[i] > arr[i + 1]) {
                int tmp = arr[i];
                arr[i] = arr[i + 1];
                arr[i + 1] = tmp;
                swapped = 1;
            }
        }

        if (!swapped) {
            break; /* no swaps in this pass -> the array is already sorted */
        }
    }
}

int binary_search_loop(const int *arr, int size, int target)
{
    int low = 0;
    int high = size - 1;

    while (low <= high) {
        int mid = low + (high - low) / 2; /* avoids overflow of (low + high) */

        if (arr[mid] == target) {
            return mid;
        }

        if (arr[mid] < target) {
            low = mid + 1;  /* target can only be in the right half */
        } else {
            high = mid - 1; /* target can only be in the left half */
        }
    }

    return -1; /* search range is empty -> target is not in the array */
}
