#!/bin/bash
npm run build && \
  rm -rf ../extension/assets && \
  cp -r ./dist/* ../extension/ \
;

