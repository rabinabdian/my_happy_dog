# Lotto Data Analysis

A Python tool for analyzing lottery draw data to identify patterns, frequencies, and generate suggested combinations based on historical data.

## Features

- Load and parse lottery data from CSV files
- Analyze frequency of individual numbers
- **NEW: Analyze co-occurring groups of ALL sizes** (2-6 numbers)
- Identify not just pairs and triplets, but also 4-number, 5-number, and even complete 6-number groups that appeared together
- Identify most common strong numbers
- **IMPROVED: Smart algorithm that prioritizes larger co-occurring groups**
  - Starts with complete 6-number combinations that appeared together multiple times
  - Falls back to 5-number groups (adds 1 number), then 4-number groups (adds 2), etc.
  - Numbers that appeared together historically are more likely to be suggested together
- Score combinations based on historical co-occurrence strength
- Multiple algorithm strategies for generating suggestions

## Requirements

- Python 3.6 or higher
- No external dependencies (uses only Python standard library)

## Usage

### Basic Usage

1. Prepare your CSV file with lottery data:
   - Columns 1-6: Main lottery numbers
   - Column 7: Strong number
   - Optional header row

2. Update the filename in `lotto_analysis.py`:
   ```python
   filename = "path/to/your/lotto_results.csv"
   ```

3. Set the `has_header` parameter:
   ```python
   main_rows, strong_numbers = load_lotto_data(
       filename,
       main_cols=6,
       has_header=False  # Set True if your CSV has a header row
   )
   ```

4. Run the analysis:
   ```bash
   python lotto_analysis.py
   ```

### Output

The script provides:
1. Main number frequency statistics
2. Strong number frequency statistics
3. Most common pairs of numbers appearing together
4. Most common triplets of numbers appearing together
5. **DETAILED CO-OCCURRENCE ANALYSIS**: Shows groups of all sizes (2-6 numbers)
   - Displays which 6-number combinations appeared together multiple times
   - Shows 5-number, 4-number, 3-number, and 2-number groups
   - Lists top 10 most frequent groups for each size
6. **IMPROVED ALGORITHM**: Smart combinations prioritizing larger co-occurring groups
   - Starts with actual 6-number combinations from historical data
   - Uses 5-number groups and intelligently adds the best 6th number
   - Uses 4-number groups and adds the 2 most co-occurring numbers
7. **ALTERNATIVE**: Random mix combinations with scoring

Each suggested combination includes:
- The 6 main numbers
- The strong number
- A quality score showing how often those numbers appeared together historically
- Pair co-occurrence score and average pair frequency

The improved algorithm will tell you which strategy it used:
- "Using X complete 6-number groups that appeared together!"
- "Using 5-number groups, adding 1 more number..."
- "Using 4-number groups, adding 2 more numbers..."
- "Using 3-number groups, adding 3 more numbers..."

## Functions

### Core Data Loading

#### `load_lotto_data(filename, main_cols=6, has_header=True)`
Loads lottery data from a CSV file.

### Analysis Functions

#### `most_repeated_main_numbers(main_rows)`
Returns frequency count of all main numbers.

#### `strong_number_frequencies(strong_numbers)`
Returns frequency count of strong numbers.

#### `combo_frequencies(main_rows, size=2, min_freq=2)`
Returns frequency of number combinations (pairs, triplets, etc.).

#### `build_cooccurrence_matrix(main_rows, max_number=49)`
Builds a matrix showing how often each pair of numbers appears together.

#### `analyze_all_cooccurrence_sizes(main_rows, min_freq=2)` **[NEW]**
Analyzes co-occurring groups of ALL sizes (2-6 numbers). Returns a dictionary with counters for each size showing which groups appeared together and how often.

This is the key function that enables analyzing larger groups beyond just pairs and triplets!

#### `score_combination(combo, main_rows, pair_counter=None, single_counter=None)`
Scores a combination based on historical co-occurrence patterns. Returns:
- `total`: Combined weighted score
- `pair_score`: Sum of all pair co-occurrence frequencies
- `frequency_score`: Sum of individual number frequencies
- `avg_pair_freq`: Average frequency of pairs in this combination

#### `print_all_cooccurrence_stats(main_rows, min_freq=2, top_n=10)` **[NEW]**
Prints detailed statistics about co-occurring groups of all sizes (2-6). Shows the top N most frequent groups for each size.

### Combination Generation Algorithms

#### `generate_combinations_from_cooccurrence(...)` **[MUCH IMPROVED ALGORITHM]**
**Major upgrade:** Now analyzes co-occurring groups of ALL sizes (2-6 numbers), not just triplets!

Algorithm strategy:
1. First, looks for complete 6-number combinations that appeared together multiple times - these are the best suggestions!
2. Then uses 5-number groups and intelligently adds the number that co-occurs most with that group
3. Then uses 4-number groups and adds the 2 numbers that co-occur most
4. Finally uses 3-number groups as fallback

This ensures combinations where numbers have the strongest historical co-occurrence patterns.

Parameters:
- `num_suggestions`: Number of combinations to generate (default: 10)
- `top_n_per_size`: Top N combinations to consider per size (default: 20)
- `strong_top_n`: Top N strong numbers to consider (default: 5)
- `min_cooccurrence_freq`: Minimum times a group must appear together (default: 2)

#### `generate_suggested_combinations(...)`
Original algorithm that randomly mixes top singles, pairs, and triplets with scoring.

Parameters:
- `num_suggestions`: Number of combinations to generate (default: 10)
- `main_top_n`: Top N most frequent main numbers to consider (default: 15)
- `pair_top_n`: Top N most frequent pairs to consider (default: 30)
- `trip_top_n`: Top N most frequent triplets to consider (default: 30)
- `strong_top_n`: Top N most frequent strong numbers to consider (default: 5)

## CSV Format

Expected CSV format (without header):
```
1,5,12,23,34,45,7
3,8,15,22,31,42,9
...
```

Or with header:
```
num1,num2,num3,num4,num5,num6,strong
1,5,12,23,34,45,7
3,8,15,22,31,42,9
...
```

## Understanding the Scores

Each suggested combination is scored based on historical patterns:

- **Total Score**: Combined weighted score (pair_score × 2 + frequency_score)
- **Pair Score**: Sum of how often each pair in the combination appeared together
- **Average Pair Frequency**: The pair score divided by number of pairs (15 pairs in a 6-number combination)

**Higher scores indicate combinations where the numbers have appeared together more frequently in historical data.**

Example output:
```
1) 5, 12, 19, 23, 34, 41  |  Strong: 7  |  Score: 1234 (pairs: 456, avg: 30.4)
```
This means:
- The 15 pairs within these 6 numbers appeared together a total of 456 times
- On average, each pair appeared together 30.4 times
- The total weighted score is 1234

## Customization

### For the Improved Co-occurrence Algorithm (analyzes ALL sizes):
```python
generate_combinations_from_cooccurrence(
    main_rows,
    strong_numbers,
    num_suggestions=10,           # How many combinations to generate
    top_n_per_size=20,            # Top N groups to consider for each size (2-6)
    strong_top_n=5,               # Top strong numbers to consider
    min_cooccurrence_freq=2       # Minimum times a group must appear together
)
```

### For the Detailed Co-occurrence Analysis:
```python
print_all_cooccurrence_stats(
    main_rows,
    min_freq=2,   # Minimum frequency to display
    top_n=10      # Show top N for each size
)
```

### For the Random Mix Algorithm:
```python
generate_suggested_combinations(
    main_rows,
    strong_numbers,
    num_suggestions=10,  # Number of combinations to generate
    main_top_n=15,       # Top N most frequent main numbers
    pair_top_n=30,       # Top N most frequent pairs
    trip_top_n=30,       # Top N most frequent triplets
    strong_top_n=5       # Top N most frequent strong numbers
)
```

## Disclaimer

This tool is for educational and entertainment purposes only. Lottery draws are random events, and past results do not guarantee future outcomes. Use responsibly.
