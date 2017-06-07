@echo off
pushd ..
zip -r9 "scene_check.zip" scene_check\*.py scene_check\validators\*.py
popd
move ..\scene_check.zip .

