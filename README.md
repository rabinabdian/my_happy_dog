# Lotto Data Analysis

A Python tool for analyzing lottery draw data to identify patterns, frequencies, and generate suggested combinations based on historical data.

## Features

- Load and parse lottery data from CSV files
- Analyze frequency of individual numbers
- Analyze frequency of number combinations (pairs, triplets, etc.)
- Identify most common strong numbers
- Generate suggested combinations based on historical patterns

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
5. Suggested combinations based on historical patterns

## Functions

### `load_lotto_data(filename, main_cols=6, has_header=True)`
Loads lottery data from a CSV file.

### `most_repeated_main_numbers(main_rows)`
Returns frequency count of all main numbers.

### `strong_number_frequencies(strong_numbers)`
Returns frequency count of strong numbers.

### `combo_frequencies(main_rows, size=2, min_freq=2)`
Returns frequency of number combinations (pairs, triplets, etc.).

### `generate_suggested_combinations(...)`
Generates suggested lottery combinations based on historical patterns.

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

## Customization

You can adjust the analysis parameters in the `generate_suggested_combinations()` call:
- `num_suggestions`: Number of combinations to generate (default: 10)
- `main_top_n`: Top N most frequent main numbers to consider (default: 15)
- `pair_top_n`: Top N most frequent pairs to consider (default: 30)
- `trip_top_n`: Top N most frequent triplets to consider (default: 30)
- `strong_top_n`: Top N most frequent strong numbers to consider (default: 5)

## Disclaimer

This tool is for educational and entertainment purposes only. Lottery draws are random events, and past results do not guarantee future outcomes. Use responsibly.
