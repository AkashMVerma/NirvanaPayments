#!/bin/bash

for i in {100..30001..5000}
do
    python3 NirvanaAuthorities.py $i  & disown
    sleep 2
    python3 Merchant.py & disown
    sleep 2
    python3 Customer_preprocessed.py &disown
    sleep 30
done