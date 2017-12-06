#! /bin/bash

coverage -e
coverage -x test.py
coverage -b -d ./coverage

