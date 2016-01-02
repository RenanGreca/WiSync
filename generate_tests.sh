#!/bin/bash
for i in {1..1000}
do
   touch "test$i"
   truncate -s 1M "test$i"
done