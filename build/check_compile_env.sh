#!/bin/bash

GCC_PATH=$(which gcc 2>/dev/null)
if [ -z "$GCC_PATH" ]; then
    echo "not found gcc, please install gcc-9.4.0"
    exit 1
fi

GCC_VERSION=$(gcc --version | head -n1 | awk '{print $NF}')
if [ "$GCC_VERSION" != "9.4.0" ]; then
    echo "current gcc version is $GCC_VERSION, please use gcc-9.4.0"
    exit 1
fi

LIBSTDCXX_PATH=$(gcc -print-file-name=libstdc++.so)
if [ -L "$LIBSTDCXX_PATH" ]; then
    LIBSTDCXX_PATH=$(readlink -f "$LIBSTDCXX_PATH")
fi
echo "$LIBSTDCXX_PATH"

GLIBCXX_MAX_VERSION=$(strings $LIBSTDCXX_PATH | grep "^GLIBCXX_[0-9]" | awk -F'_' '{print $2}' | sort -V | tail -1)
if [ "$GLIBCXX_MAX_VERSION" != "3.4.28" ]; then
    echo "GLIBCXX: $GLIBCXX_MAX_VERSION, please use libstdc++.so.6.0.28"
    exit 1
fi

echo "GLIBCXX: $GLIBCXX_MAX_VERSION"
