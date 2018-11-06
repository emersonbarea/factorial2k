#!/bin/bash

printf 'Killing MaxiNet...\n'
pgrep -f MaxiNetWorker | sudo xargs kill
pgrep -f MaxiNetFrontendServer | sudo xargs kill
printf 'MaxiNet killed\n'
