#/bin/bash
cat domains.txt | xargs -I{} python scanner.py $1 {}
