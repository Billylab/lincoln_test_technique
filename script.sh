#!/bin/sh
echo Starting Python script : 0_landing_to_raw
python pipeline/0_landing_to_raw/manual_files/0_landing_to_raw.py

echo Starting Python script : 1_make_json_graph
python pipeline/1_make_json_graph/1_make_json_graph.py


