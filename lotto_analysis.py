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


def build_cooccurrence_matrix(main_rows, max_number=49):
    """
    Build a co-occurrence matrix showing how often pairs of numbers appear together.

    Args:
        main_rows (list[list[int]]): Main numbers per draw.
        max_number (int): Maximum possible lottery number.

    Returns:
        dict: {(num1, num2): frequency} for all pairs that appeared together
    """
    cooccurrence = Counter()

    for row in main_rows:
        unique_nums = sorted(set(row))
        for pair in combinations(unique_nums, 2):
            cooccurrence[pair] += 1

    return cooccurrence


def score_combination(combo, main_rows, pair_counter=None, single_counter=None):
    """
    Score a combination based on how often the numbers appear together historically.

    Args:
        combo (list[int]): List of 6 numbers to score.
        main_rows (list[list[int]]): Historical lottery data.
        pair_counter (Counter): Pre-computed pair frequencies (optional).
        single_counter (Counter): Pre-computed single number frequencies (optional).

    Returns:
        dict: Score breakdown with total, pair_score, and frequency_score
    """
    if pair_counter is None:
        pair_counter = Counter()
        for row in main_rows:
            unique_nums = sorted(set(row))
            for pair in combinations(unique_nums, 2):
                pair_counter[pair] += 1

    if single_counter is None:
        single_counter = Counter()
        for row in main_rows:
            single_counter.update(row)

    # Score based on pair co-occurrences
    pair_score = 0
    combo_pairs = list(combinations(sorted(combo), 2))
    for pair in combo_pairs:
        pair_score += pair_counter.get(pair, 0)

    # Score based on individual number frequencies
    frequency_score = sum(single_counter.get(num, 0) for num in combo)

    # Combined score (weighted)
    total_score = (pair_score * 2) + frequency_score

    return {
        'total': total_score,
        'pair_score': pair_score,
        'frequency_score': frequency_score,
        'avg_pair_freq': pair_score / len(combo_pairs) if combo_pairs else 0
    }


def analyze_all_cooccurrence_sizes(main_rows, min_freq=2):
    """
    Analyze co-occurring groups of all sizes (2-6 numbers).

    Args:
        main_rows (list[list[int]]): Historical lottery data.
        min_freq (int): Minimum frequency to include.

    Returns:
        dict: {size: Counter({combo: frequency})} for sizes 2-6
    """
    size_counters = {
        2: Counter(),
        3: Counter(),
        4: Counter(),
        5: Counter(),
        6: Counter()
    }

    for row in main_rows:
        unique_nums = sorted(set(row))
        # Generate combinations of all sizes
        for size in range(2, 7):
            if len(unique_nums) >= size:
                for combo in combinations(unique_nums, size):
                    size_counters[size][combo] += 1

    # Filter by minimum frequency
    for size in size_counters:
        size_counters[size] = Counter({
            combo: freq
            for combo, freq in size_counters[size].items()
            if freq >= min_freq
        })

    return size_counters


def generate_combinations_from_cooccurrence(
    main_rows,
    strong_numbers,
    num_suggestions=10,
    top_n_per_size=20,
    strong_top_n=5,
    min_cooccurrence_freq=2
):
    """
    IMPROVED: Generate combinations by analyzing co-occurring groups of ALL sizes (2-6).
    Prioritizes larger groups that appeared together more frequently.

    Args:
        main_rows (list[list[int]]): Historical lottery data.
        strong_numbers (list[int]): Strong numbers from historical data.
        num_suggestions (int): Number of combinations to generate.
        top_n_per_size (int): Top N combinations to consider per size.
        strong_top_n (int): Consider top N strong numbers.
        min_cooccurrence_freq (int): Minimum times a group must appear together.

    Returns:
        list[(list[int], int, dict)]: (6 main numbers, strong_number, score_dict)
    """
    # Build frequency counters for ALL combination sizes
    print(f"Analyzing co-occurring groups of all sizes (2-6 numbers)...")
    size_counters = analyze_all_cooccurrence_sizes(main_rows, min_freq=min_cooccurrence_freq)

    # Also get single number frequencies
    single_counter = Counter()
    for row in main_rows:
        single_counter.update(row)

    strong_counter = Counter(strong_numbers)
    top_strongs = [num for num, _ in strong_counter.most_common(strong_top_n)]

    # Build co-occurrence lookup for pairs (for filling incomplete combinations)
    pair_counter = size_counters[2]
    cooccurrence = {}
    for (num1, num2), freq in pair_counter.items():
        if num1 not in cooccurrence:
            cooccurrence[num1] = []
        if num2 not in cooccurrence:
            cooccurrence[num2] = []
        cooccurrence[num1].append((num2, freq))
        cooccurrence[num2].append((num1, freq))

    # Sort co-occurrence lists by frequency
    for num in cooccurrence:
        cooccurrence[num].sort(key=lambda x: x[1], reverse=True)

    suggestions = []
    seen_combos = set()

    # Print statistics about co-occurring groups
    for size in [6, 5, 4, 3]:
        count = len(size_counters[size])
        if count > 0:
            top_freq = size_counters[size].most_common(1)[0][1] if size_counters[size] else 0
            print(f"  Found {count} groups of {size} numbers (top frequency: {top_freq})")

    # Strategy: Start with LARGEST groups first (6, then 5, then 4, then 3)
    # This prioritizes numbers that appeared together most often

    # 1. Check for complete 6-number combinations that appeared multiple times
    if size_counters[6]:
        print(f"\n  Using {len(size_counters[6])} complete 6-number groups that appeared together!")
        for combo, freq in size_counters[6].most_common(top_n_per_size):
            if len(suggestions) >= num_suggestions:
                break

            combo_tuple = tuple(sorted(combo))
            if combo_tuple in seen_combos:
                continue
            seen_combos.add(combo_tuple)

            score_dict = score_combination(list(combo), main_rows, pair_counter, single_counter)
            strong_num = random.choice(top_strongs) if top_strongs else (
                random.choice(strong_numbers) if strong_numbers else None
            )
            suggestions.append((list(combo), strong_num, score_dict))

    # 2. Use 5-number combinations, add 1 more number
    if len(suggestions) < num_suggestions and size_counters[5]:
        print(f"  Using 5-number groups, adding 1 more number...")
        for combo, freq in size_counters[5].most_common(top_n_per_size):
            if len(suggestions) >= num_suggestions:
                break

            combo_set = set(combo)

            # Find the best number to add based on co-occurrence
            candidates = Counter()
            for num in combo_set:
                if num in cooccurrence:
                    for other_num, cofreq in cooccurrence[num]:
                        if other_num not in combo_set:
                            candidates[other_num] += cofreq

            if candidates:
                best_num = candidates.most_common(1)[0][0]
                combo_set.add(best_num)
            else:
                # Fallback: add most frequent single
                remaining = [n for n, _ in single_counter.most_common(49) if n not in combo_set]
                if remaining:
                    combo_set.add(remaining[0])

            if len(combo_set) == 6:
                combo_tuple = tuple(sorted(combo_set))
                if combo_tuple not in seen_combos:
                    seen_combos.add(combo_tuple)
                    score_dict = score_combination(list(combo_tuple), main_rows, pair_counter, single_counter)
                    strong_num = random.choice(top_strongs) if top_strongs else (
                        random.choice(strong_numbers) if strong_numbers else None
                    )
                    suggestions.append((list(combo_tuple), strong_num, score_dict))

    # 3. Use 4-number combinations, add 2 more numbers
    if len(suggestions) < num_suggestions and size_counters[4]:
        print(f"  Using 4-number groups, adding 2 more numbers...")
        for combo, freq in size_counters[4].most_common(top_n_per_size):
            if len(suggestions) >= num_suggestions:
                break

            combo_set = set(combo)

            # Add 2 numbers that co-occur most with this group
            for _ in range(2):
                candidates = Counter()
                for num in combo_set:
                    if num in cooccurrence:
                        for other_num, cofreq in cooccurrence[num]:
                            if other_num not in combo_set:
                                candidates[other_num] += cofreq

                if candidates:
                    best_num = candidates.most_common(1)[0][0]
                    combo_set.add(best_num)
                else:
                    remaining = [n for n, _ in single_counter.most_common(49) if n not in combo_set]
                    if remaining:
                        combo_set.add(remaining[0])

            if len(combo_set) == 6:
                combo_tuple = tuple(sorted(combo_set))
                if combo_tuple not in seen_combos:
                    seen_combos.add(combo_tuple)
                    score_dict = score_combination(list(combo_tuple), main_rows, pair_counter, single_counter)
                    strong_num = random.choice(top_strongs) if top_strongs else (
                        random.choice(strong_numbers) if strong_numbers else None
                    )
                    suggestions.append((list(combo_tuple), strong_num, score_dict))

    # 4. Use 3-number combinations (original approach), add 3 more numbers
    if len(suggestions) < num_suggestions and size_counters[3]:
        print(f"  Using 3-number groups, adding 3 more numbers...")
        for combo, freq in size_counters[3].most_common(top_n_per_size):
            if len(suggestions) >= num_suggestions:
                break

            combo_set = set(combo)

            # Add 3 numbers that co-occur most with this group
            for _ in range(3):
                candidates = Counter()
                for num in combo_set:
                    if num in cooccurrence:
                        for other_num, cofreq in cooccurrence[num]:
                            if other_num not in combo_set:
                                candidates[other_num] += cofreq

                if candidates:
                    best_num = candidates.most_common(1)[0][0]
                    combo_set.add(best_num)
                else:
                    remaining = [n for n, _ in single_counter.most_common(49) if n not in combo_set]
                    if remaining:
                        combo_set.add(remaining[0])

            if len(combo_set) == 6:
                combo_tuple = tuple(sorted(combo_set))
                if combo_tuple not in seen_combos:
                    seen_combos.add(combo_tuple)
                    score_dict = score_combination(list(combo_tuple), main_rows, pair_counter, single_counter)
                    strong_num = random.choice(top_strongs) if top_strongs else (
                        random.choice(strong_numbers) if strong_numbers else None
                    )
                    suggestions.append((list(combo_tuple), strong_num, score_dict))

    # Sort by score (highest first)
    suggestions.sort(key=lambda x: x[2]['total'], reverse=True)

    return suggestions[:num_suggestions]


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
        list[(list[int], int, dict)]: list of (6 main numbers, strong_number, score_dict)
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

        # Score this combination
        score_dict = score_combination(row_list, main_rows, pair_counter, single_counter)

        # Choose a strong number based on top frequencies in column 7
        if top_strongs:
            strong_num = random.choice(top_strongs)
        else:
            # Fallback: pick any strong number from data
            strong_num = random.choice(strong_numbers) if strong_numbers else None

        suggestions.append((row_list, strong_num, score_dict))

        if len(suggestions) >= num_suggestions:
            break

    # Sort by score
    suggestions.sort(key=lambda x: x[2]['total'], reverse=True)

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


def print_all_cooccurrence_stats(main_rows, min_freq=2, top_n=10):
    """
    Print statistics about co-occurring groups of all sizes.
    """
    print("=" * 70)
    print("ANALYZING ALL CO-OCCURRENCE PATTERNS (2-6 NUMBERS)")
    print("=" * 70)

    size_counters = analyze_all_cooccurrence_sizes(main_rows, min_freq=min_freq)

    for size in [6, 5, 4, 3, 2]:
        counter = size_counters[size]
        total_count = len(counter)

        if total_count == 0:
            print(f"\n{size}-number groups: None found with freq >= {min_freq}")
            continue

        print(f"\n{size}-number groups: {total_count} found")
        print(f"Top {min(top_n, total_count)} most frequent:")

        for i, (combo, freq) in enumerate(counter.most_common(top_n), 1):
            nums_str = ", ".join(str(n) for n in combo)
            print(f"  {i:2d}) ({nums_str}) appeared together {freq} times")

    print()


def print_suggestions(suggestions, show_scores=True):
    print("=== Suggested combinations (6 main + strong) ===")
    if not suggestions:
        print("No suggestions generated.")
        return

    for i, suggestion in enumerate(suggestions, start=1):
        # Handle both old format (main_nums, strong_num) and new format with scores
        if len(suggestion) == 3:
            main_nums, strong_num, score_dict = suggestion
        else:
            main_nums, strong_num = suggestion
            score_dict = None

        mains_str = ", ".join(str(n) for n in main_nums)

        if strong_num is not None:
            output = f"{i:2d}) {mains_str}  |  Strong: {strong_num}"
        else:
            output = f"{i:2d}) {mains_str}"

        if show_scores and score_dict:
            output += f"  |  Score: {score_dict['total']}"
            output += f" (pairs: {score_dict['pair_score']}, avg: {score_dict['avg_pair_freq']:.1f})"

        print(output)
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

    # 5) DETAILED analysis of ALL co-occurrence patterns (2-6 numbers)
    print_all_cooccurrence_stats(main_rows, min_freq=2, top_n=10)

    # 6) Co-occurrence based suggestions (IMPROVED ALGORITHM)
    print("=" * 70)
    print("IMPROVED ALGORITHM: Analyzes groups of ALL sizes (2-6 numbers)")
    print("Prioritizes larger groups that appeared together more frequently")
    print("=" * 70)
    cooccurrence_suggestions = generate_combinations_from_cooccurrence(
        main_rows,
        strong_numbers,
        num_suggestions=10,
        top_n_per_size=20,
        strong_top_n=5,
        min_cooccurrence_freq=2
    )
    print_suggestions(cooccurrence_suggestions, show_scores=True)

    # 7) Random mix suggestions (original algorithm with scoring)
    print("=" * 70)
    print("ALTERNATIVE: Random mix of top pairs/triplets with scoring")
    print("=" * 70)
    random_suggestions = generate_suggested_combinations(
        main_rows,
        strong_numbers,
        num_suggestions=10,
        main_top_n=15,
        pair_top_n=30,
        trip_top_n=30,
        strong_top_n=5
    )
    print_suggestions(random_suggestions, show_scores=True)
