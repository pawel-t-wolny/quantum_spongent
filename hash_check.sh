#!/bin/bash

TEST_WORDS_FILE="test_words.txt"
REFERENCE_SPONGENT="./spongent_reference/bin/spongent"
TEST_SPONGENT="reversible_spongent.py"
PYTHON="python3"

# Recompile the reference implementation
(
    cd spongent_reference && make clean && make
)

# Ensure test_words.txt exists
if [[ ! -f "$TEST_WORDS_FILE" ]]; then
  echo "Error: test_words.txt not found."
  exit 1
fi

run_test_case() {
  local word="$1"

  # Run the reference implementation
  ref_output=$("$REFERENCE_SPONGENT" -q "$word")
  ref_status=$?

  # Run the Python implementation
  py_output=$("$PYTHON" "$TEST_SPONGENT" -q "$word")
  py_status=$?

  # Check if both commands executed successfully
  if [[ $ref_status -ne 0 ]]; then
    echo "Error: ./spongent failed for input '$word'"
    return
  fi

  if [[ $py_status -ne 0 ]]; then
    echo "Error: reversible_spongent.py failed for input '$word'"
    return
  fi

  # Compare outputs
  if [[ "$ref_output" == "$py_output" ]]; then
    echo "✅ Match for '$word'"
  else
    echo "❌ Mismatch for '$word'"
    echo "  spongent: $ref_output"
    echo "  python:   $py_output"
  fi
}

# Test the special case: empty string
run_test_case ""

# Now loop through each word in test_words.txt
while IFS= read -r word; do
  [[ -z "$word" ]] && continue
  run_test_case "$word"
done < "$TEST_WORDS_FILE"
