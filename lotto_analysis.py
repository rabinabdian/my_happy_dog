import csv
import random
from collections import Counter
from itertools import combinations


def load_lotto_data(filename, main_cols=6, has_header=True):
    """
    Load lotto data from a CSV file.

    Args:
        filename (str): Path to the CSV.
        main_cols (int): Number of main-number columns (typically 6).
        has_header (bool): Whether the first row is a header.

    Returns:
        main_rows (list[list[int]]): Each inner list contains the main numbers of a draw.
        strong_numbers (list[int]): List of strong numbers (column main_cols).
    """
    main_rows = []
    strong_numbers = []

    with open(filename, mode='r', newline='') as file:
        reader = csv.reader(file)
        if has_header:
            next(reader, None)  # Skip header

        for row in reader:
            # Skip empty/blank lines
            if not row or all(col.strip() == "" for col in row):
                continue

            # Need at least main_cols + 1 (for strong)
            if len(row) <= main_cols:
                continue

            try:
                main_nums = [int(row[i]) for i in range(main_cols)]
                strong_num = int(row[main_cols])
            except ValueError:
                # Bad/dirty row – skip
                continue

            main_rows.append(main_nums)
            strong_numbers.append(strong_num)

    return main_rows, strong_numbers


def most_repeated_main_numbers(main_rows):
    """
    Count how often each main number appears across all draws.

    Returns:
        list[(int, int)]: (number, frequency), sorted desc by frequency.
    """
    all_numbers = []
    for nums in main_rows:
        all_numbers.extend(nums)

    count = Counter(all_numbers)
    return count.most_common()


def strong_number_frequencies(strong_numbers):
    """
    Count how often each strong number appears.

    Returns:
        list[(int, int)]: (number, frequency), sorted desc by frequency.
    """
    count = Counter(strong_numbers)
    return count.most_common()


def combo_frequencies(main_rows, size=2, min_freq=2):
    """
    Frequency of combinations (pairs, triplets, etc.) of main numbers
    that appear together in the same row.

    Args:
        main_rows (list[list[int]]): Main numbers per draw.
        size (int): Combination size (2=pairs, 3=triplets, ...).
        min_freq (int): Minimum frequency filter.

    Returns:
        list[(tuple[int], int)]: (combo, frequency), sorted desc by frequency.
    """
    combo_counter = Counter()

    for row in main_rows:
        unique_nums = sorted(set(row))
        for combo in combinations(unique_nums, size):
            combo_counter[combo] += 1

    return [
        (combo, freq)
        for combo, freq in combo_counter.most_common()
        if freq >= min_freq
    ]


def generate_suggested_combinations(
    main_rows,
    strong_numbers,
    num_suggestions=10,
    main_top_n=15,
    pair_top_n=30,
    trip_top_n=30,
    strong_top_n=5
):
    """
    Generate suggested combinations based on:
    - top single main-number frequencies
    - top pair frequencies
    - top triplet frequencies
    - top strong-number frequencies (column 7)

    Returns:
        list[(list[int], int)]: list of (6 main numbers, strong_number)
    """
    # 1. Single-number frequencies (main)
    all_nums = [n for row in main_rows for n in row]
    single_counter = Counter(all_nums)

    # 2. Pair & triplet counters (main)
    pair_counter = Counter()
    trip_counter = Counter()

    for row in main_rows:
        unique_nums = sorted(set(row))
        for combo in combinations(unique_nums, 2):
            pair_counter[combo] += 1
        for combo in combinations(unique_nums, 3):
            trip_counter[combo] += 1

    # 3. Strong-number frequencies
    strong_counter = Counter(strong_numbers)

    # 4. Top elements
    top_singles = [num for num, _ in single_counter.most_common(main_top_n)]
    top_pairs = [combo for combo, _ in pair_counter.most_common(pair_top_n)]
    top_trips = [combo for combo, _ in trip_counter.most_common(trip_top_n)]
    top_strongs = [num for num, _ in strong_counter.most_common(strong_top_n)]

    suggestions = []
    seen_main_rows = set()  # to avoid exact duplicate main combinations

    if not top_singles:
        return suggestions

    for _ in range(num_suggestions * 5):  # extra attempts to avoid duplicates
        row_set = set()

        # Seed with a strong triplet if available
        if top_trips:
            trip = random.choice(top_trips)
            row_set.update(trip)

        # Add pairs & singles until we hit at least 6 main numbers
        while len(row_set) < 6:
            if top_pairs:
                pair = random.choice(top_pairs)
                row_set.update(pair)

            if len(row_set) < 6:
                row_set.add(random.choice(top_singles))

            # Safety valve in case something goes weird
            if len(row_set) > 10:
                break

        # Normalize to exactly 6 main numbers
        row_list = sorted(list(row_set))
        if len(row_list) > 6:
            row_list = sorted(random.sample(row_list, 6))

        row_tuple = tuple(row_list)
        if row_tuple in seen_main_rows:
            continue

        seen_main_rows.add(row_tuple)

        # Choose a strong number based on top frequencies in column 7
        if top_strongs:
            strong_num = random.choice(top_strongs)
        else:
            # Fallback: pick any strong number from data
            strong_num = random.choice(strong_numbers) if strong_numbers else None

        suggestions.append((row_list, strong_num))

        if len(suggestions) >= num_suggestions:
            break

    return suggestions


def print_main_number_stats(main_freq):
    print("=== Main numbers (columns 1–6), most frequent at top ===")
    for num, freq in main_freq:
        print(f"Number {num} appears {freq} times.")
    print()


def print_strong_number_stats(strong_freq):
    print("=== Strong numbers (column 7), most frequent at top ===")
    for num, freq in strong_freq:
        print(f"Strong number {num} appears {freq} times.")
    print()


def print_combo_stats(combo_freq, size):
    label = "pairs" if size == 2 else f"combinations of size {size}"
    print(f"=== Most frequent {label} of main numbers (same row) ===")
    if not combo_freq:
        print("No combinations meet the minimum frequency.\n")
        return

    for combo, freq in combo_freq:
        nums_str = ", ".join(str(n) for n in combo)
        print(f"({nums_str}) appear together {freq} times.")
    print()


def print_suggestions(suggestions):
    print("=== Suggested combinations (6 main + strong) ===")
    if not suggestions:
        print("No suggestions generated.")
        return

    for i, (main_nums, strong_num) in enumerate(suggestions, start=1):
        mains_str = ", ".join(str(n) for n in main_nums)
        if strong_num is not None:
            print(f"{i:2d}) {mains_str}  |  Strong: {strong_num}")
        else:
            print(f"{i:2d}) {mains_str}")
    print()


if __name__ == "__main__":
    # OPTIONAL: fix random seed for reproducibility
    # random.seed(42)

    # 👉 Change this to your actual file path
    # For your case: remove header = False, because cleaned CSV has no header.
    filename = r"C:\Users\user\Documents\loto_project\lotto_results_2024_cleaned.csv"

    main_rows, strong_numbers = load_lotto_data(
        filename,
        main_cols=6,
        has_header=False  # set True if first line is a header row
    )

    if not main_rows:
        print("No valid rows found in the file. Check the CSV formatting.")
        raise SystemExit(1)

    # 1) Single-number stats (main)
    main_freq = most_repeated_main_numbers(main_rows)
    print_main_number_stats(main_freq)

    # 2) Strong-number stats (column 7)
    strong_freq = strong_number_frequencies(strong_numbers)
    print_strong_number_stats(strong_freq)

    # 3) Pairs of main numbers
    pairs_freq = combo_frequencies(main_rows, size=2, min_freq=2)
    print_combo_stats(pairs_freq, size=2)

    # 4) Triplets of main numbers
    triplets_freq = combo_frequencies(main_rows, size=3, min_freq=2)
    print_combo_stats(triplets_freq, size=3)

    # 5) Suggested combinations using both main + strong stats
    suggestions = generate_suggested_combinations(
        main_rows,
        strong_numbers,
        num_suggestions=10,
        main_top_n=15,
        pair_top_n=30,
        trip_top_n=30,
        strong_top_n=5
    )
    print_suggestions(suggestions)
