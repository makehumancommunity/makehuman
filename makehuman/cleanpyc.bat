@echo off

:: Clean up any remaining .pyc files.
:: It is advised to do this after every svn update.

set filetype=.pyc

for /r %%i in (*) do (
   if %%~xi==%filetype% (
      del %%i
   )
)
