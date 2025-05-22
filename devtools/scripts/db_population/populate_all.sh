#/bin/bash

python3 populate_coordinators.py --input_csv $1
python3 populate_teachers.py --input_csv $2
python3 populate_students.py --input_csv $3
python3 populate_groups.py --input_csv $4
