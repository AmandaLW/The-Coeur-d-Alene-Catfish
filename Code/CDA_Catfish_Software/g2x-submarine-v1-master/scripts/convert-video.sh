#!/usr/bin/env bash

for f in *.h264
do
	base=$(basename $f .h264)
	target="$base.mp4"
	echo "converting $f to $target..."
	mp4box -add $f $target
done

echo "done"
