#include "array_utils.h"

/*
 * Recursive binary search.
 *
 * Returns the index of the first occurrence of target in the sorted array
 * arr[left..right], or -1 if the target is not present.
 *
 * Time complexity: O(log n) - the search interval is halved on every call.
 * Space complexity: O(log n) - recursion depth (the call stack).
 */
int binary_search_recursive(const int arr[], int left, int right, int target) {
    if (left > right) {
        return -1;
    }

    int mid = left + (right - left) / 2;  /* avoids overflow of left + right */

    if (arr[mid] == target) {
        /* There may be another occurrence on the left, so find the first one. */
        int first = binary_search_recursive(arr, left, mid - 1, target);
        return (first != -1) ? first : mid;
    }

    if (arr[mid] < target) {
        return binary_search_recursive(arr, mid + 1, right, target);
    }

    return binary_search_recursive(arr, left, mid - 1, target);
}

/* Wrapper function (simpler interface) */
int binary_search(const int arr[], int size, int target) {
    return binary_search_recursive(arr, 0, size - 1, target);
}
