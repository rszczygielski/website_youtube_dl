#!/bin/bash
# Stop the script if any command fails
set -e

echo "1. Generating the main graph (classes.dot)..."
pyreverse -o dot website_youtube_dl/flask_api/

echo "2. Splitting the graph using the Python script..."
# Assuming split_graph.py is in the same folder (tools/)
python tools/split_graph.py classes.dot

echo "3. Converting and formatting files to SVG..."
for dot_file in classes_*.dot; do
  base_name=$(basename "$dot_file" .dot)
  unflatten -l 3 -c 3 "$dot_file" | dot -Tsvg -o "docs/${base_name}.svg"
done

echo "4. Generating the Markdown file (docs/architecture.md)..."
echo "# 🏗️ Modular System Architecture" > docs/architecture.md
echo "This documentation provides a modular, vertically stacked view of the system architecture. Dashed boxes indicate external dependencies." >> docs/architecture.md
echo "" >> docs/architecture.md

for svg_file in docs/classes_*.svg; do
  filename=$(basename "$svg_file")
  module_name=$(echo "$filename" | sed -E 's/classes_(.*)\.svg/\1/' | awk '{print toupper(substr($0,1,1)) substr($0,2)}')

  echo "## Module: ${module_name}" >> docs/architecture.md
  echo "[![${module_name} Architecture](${filename})](${filename})" >> docs/architecture.md
  echo "" >> docs/architecture.md
done

echo "Done! Architecture generated successfully."