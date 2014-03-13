@echo off

:: Clean up any remaining .npz files.

set filetype=.npz

for /r %%i in (*) do (
   if %%~xi==%filetype% (
      del %%i
   )
)

:: Clean up .bin files as well

set filetype=.bin

for /r %%i in (*) do (
   if %%~xi==%filetype% (
      del %%i
   )
)
