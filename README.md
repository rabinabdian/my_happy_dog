# Lotto Data Analysis

A Python tool for analyzing lottery draw data to identify patterns, frequencies, and generate suggested combinations based on historical data.

## Features

- Load and parse lottery data from CSV files
- Analyze frequency of individual numbers
- Analyze frequency of number combinations (pairs, triplets, etc.)
- Identify most common strong numbers
- **IMPROVED: Generate combinations based on co-occurrence patterns** - prioritizes numbers that appear together frequently
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
5. **IMPROVED ALGORITHM**: Combinations based on co-occurrence patterns (numbers that appear together most frequently)
6. **ALTERNATIVE**: Random mix combinations with scoring

Each suggested combination includes:
- The 6 main numbers
- The strong number
- A quality score showing how often those numbers appeared together historically
- Pair co-occurrence score and average pair frequency

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

#### `score_combination(combo, main_rows, pair_counter=None, single_counter=None)`
Scores a combination based on historical co-occurrence patterns. Returns:
- `total`: Combined weighted score
- `pair_score`: Sum of all pair co-occurrence frequencies
- `frequency_score`: Sum of individual number frequencies
- `avg_pair_freq`: Average frequency of pairs in this combination

### Combination Generation Algorithms

#### `generate_combinations_from_cooccurrence(...)` **[IMPROVED ALGORITHM]**
Generates combinations by starting with the most frequently co-occurring triplets and expanding them with numbers that co-occur most often. This algorithm prioritizes numbers that historically appear together.

Parameters:
- `num_suggestions`: Number of combinations to generate (default: 10)
- `start_with_top_n_trips`: Number of top triplets to consider as seeds (default: 20)
- `strong_top_n`: Top N strong numbers to consider (default: 5)

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

### For the Improved Co-occurrence Algorithm:
```python
generate_combinations_from_cooccurrence(
    main_rows,
    strong_numbers,
    num_suggestions=10,          # How many combinations to generate
    start_with_top_n_trips=20,   # Top triplets to use as seeds
    strong_top_n=5               # Top strong numbers to consider
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
