#ifndef SORT_SEARCH_H
#define SORT_SEARCH_H

/**
 * Sorts arr in ascending order, in place, using bubble sort.
 * Stops early when a full pass makes no swaps.
 *
 * Time:  O(n^2) worst and average case, O(n) best case (already sorted).
 * Space: O(1).
 */
void bubble_sort(int *arr, int size);

/**
 * Searches a sorted (ascending) array for target using an iterative binary search.
 *
 * Returns the index of an element equal to target, or -1 if there is none.
 * If target occurs several times, any matching index may be returned.
 * The array MUST already be sorted, otherwise the result is meaningless.
 *
 * Time:  O(log n) worst case, O(1) best case.
 * Space: O(1) - a loop instead of recursion, no extra memory.
 */
int binary_search_loop(const int *arr, int size, int target);

#endif /* SORT_SEARCH_H */
