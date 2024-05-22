import re
import json
import sys
import os

TIMESTAMP_REGEX = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}\+\d{4}")
GC_NAME_REGEX = re.compile(r" \(young\).*\n")
EDEN_BEFORE_REGEX = re.compile(r"Eden: (\d+\.\d+)M")
SURVIVORS_BEFORE_REGEX = re.compile(r"Survivors: (\d+\.\d+)K")
HEAP_BEFORE_REGEX = re.compile(r"Heap: (\d+\.\d+)M")

EDEN_AFTER_REGEX = re.compile(r"Eden: \d+\.\d+M\(\d+\.\d+M\)->(\d+\.\d+)B")
SURVIVORS_AFTER_REGEX = re.compile(r"Survivors: \d+\.\d+K->(\d+\.\d+)K")
HEAP_AFTER_REGEX = re.compile(r"Heap: \d+\.\d+M\(\d+\.\d+M\)->(\d+\.\d+)M")


def main(input_file_path, output_file_path):
    if not os.path.exists(input_file_path):
        print("Input file does not exist!")
        return
    with open(input_file_path, "r") as file:
        lines = file.readlines()

    with open(output_file_path, "w") as output_file:
        output_file.write("[\n")
        is_file_not_empty = False
        for line in lines:
            timestamp_match = TIMESTAMP_REGEX.match(line)
            if timestamp_match:
                timestamp = timestamp_match.group(0)
                gc_name = re.sub(GC_NAME_REGEX, "", line.split("[")[1])
            if EDEN_BEFORE_REGEX.search(line):
                eden_before = EDEN_BEFORE_REGEX.search(line).group(1)
                survivors_before = (
                    float(SURVIVORS_BEFORE_REGEX.search(line).group(1)) / 1024
                )
                heap_before = HEAP_BEFORE_REGEX.search(line).group(1)

                eden_after = EDEN_AFTER_REGEX.search(line).group(1)
                survivors_after = (
                    float(SURVIVORS_AFTER_REGEX.search(line).group(1)) / 1024
                )
                heap_after = HEAP_AFTER_REGEX.search(line).group(1)

                before_data = {
                    "timestamp": timestamp,
                    "eden_size": eden_before,
                    "survivors_size": str(survivors_before),
                    "heap_size": heap_before,
                    "GC_name": gc_name,
                    "phase": "before",
                }

                after_data = {
                    "timestamp": timestamp,
                    "eden_size": eden_after,
                    "survivors_size": str(survivors_after),
                    "heap_size": heap_after,
                    "GC_name": gc_name,
                    "phase": "after",
                }
                if is_file_not_empty:
                    output_file.write(",\n")
                output_file.write(
                    ",\n".join(json.dumps(data) for data in [before_data, after_data])
                )

                is_file_not_empty = True
        output_file.write("\n]")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Wrong number of arguments!")
        print("Usage:")
        print("python extract_data_from_gc_logs.py input.log output.json")
    else:
        main(input_file_path=sys.argv[1], output_file_path=sys.argv[2])
