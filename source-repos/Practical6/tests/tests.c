#include <assert.h>
#include <limits.h>
#include "array_utils.h"
#include <stdio.h>

// Test 1: 0 elements in array
void test_empty_array() {
    const int arr[] = {};
    assert(binary_search(arr, 0, 5) == -1);
}

// Test 2: 1 element
void test_one_element() {
    const int arr[] = {42};
    int n = 1;
    assert(binary_search(arr, n, 42) == 0);
    assert(binary_search(arr, n, 43) == -1);
    assert(binary_search(arr, n, 41) == -1);
}

// Test 3: 2 elements
void test_two_elements() {
    const int arr[] = {10, 20};
    int n = 2;
    assert(binary_search(arr, n, 10) == 0);
    assert(binary_search(arr, n, 20) == 1);
    assert(binary_search(arr, n, 15) == -1);
}

// Test 4: 3 elements
void test_three_elements() {
    const int arr[] = {5, 15, 25};
    int n = 3;
    assert(binary_search(arr, n, 5) == 0);
    assert(binary_search(arr, n, 15) == 1);
    assert(binary_search(arr, n, 25) == 2);
    assert(binary_search(arr, n, 10) == -1);
}

// Test 5: even number of elements
void test_elements_even() {
    const int arr[] = {2, 4, 6, 8, 10, 12, 14};
    int n = 7;
    for (int i = 0; i < n; i++)
        assert(binary_search(arr, n, arr[i]) == i);
    assert(binary_search(arr, n, 3) == -1);
}

// Test 6: odd numbers of elements
void test_elements_odd() {
    const int arr[] = {1, 3, 5, 7, 9, 11, 13, 15, 17, 19};
    int n = 10;
    for (int i = 0; i < n; i++)
        assert(binary_search(arr, n, arr[i]) == i);
    assert(binary_search(arr, n, 2) == -1);
}

// Test 7: Looking for INT_MAX
void test_search_max_int() {
    const int arr[] = {0, 1, 2, 5, 10, INT_MAX};
    int n = sizeof(arr) / sizeof(arr[0]);
    assert(binary_search(arr, n, INT_MAX) == 5);
    assert(binary_search(arr, n, INT_MAX - 1) == -1);
}

// Test 8: Looking for INT_MIN
void test_search_min_int() {
    const int arr[] = {INT_MIN, -10, -5, 0, 5};
    int n = sizeof(arr) / sizeof(arr[0]);
    assert(binary_search(arr, n, INT_MIN) == 0);
    assert(binary_search(arr, n, INT_MIN + 1) == -1);
}

// Test 9: Duplicate elements (want first occurrence)
void test_duplicates_first_occurrence() {
    const int arr[] = {1, 3, 5, 5, 5, 7, 9};
    int n = sizeof(arr) / sizeof(arr[0]);
    int result = binary_search(arr, n, 5);
    assert(result == 2); 
}

// Test 10: All elements are the same
void test_all_duplicates() {
    const int arr[] = {5, 5, 5, 5, 5, 5};
    int n = sizeof(arr) / sizeof(arr[0]);
    int result = binary_search(arr, n, 5);
    assert(result == 0); // Will likely fail with current recursive search
}

int main() {
    printf("Running binary_search tests...\n");

    test_empty_array();
    test_one_element();
    test_two_elements();
    test_three_elements();
    test_elements_even();
    test_elements_odd();
    test_search_max_int();
    test_search_min_int();
    // pay attention to these test cases, you have two options:
    // 1. make your code working with this test case
    // 2. update documentation (array_utils.h) and remove this test case after it
    test_duplicates_first_occurrence();
    test_all_duplicates();

    printf("All tests passed!\n");
    return 0;
}
