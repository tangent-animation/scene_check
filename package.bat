@echo off
pushd ..
zip -r9 "scene_check.zip" scene_check\*.py scene_check\validators\*.py scene_check\schemes\*.scheme
popd
move ..\scene_check.zip .

