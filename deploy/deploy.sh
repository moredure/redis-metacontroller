#!/usr/bin/env bash

set -e

if [[ -z "$1" ]]; then
    echo "No argument supplied"
    exit 1
fi

docker build -t mikefaraponov/microredis:operator-v$1 .

docker push mikefaraponov/microredis:operator-v$1

echo $1 > VERSION
