@echo off
rem ---------------------------------------------------------------------
rem  Builds dino.c into dino.exe using the MSVC compiler (cl.exe).
rem  Just run this file, or press Ctrl+Shift+B in VS Code.
rem ---------------------------------------------------------------------
setlocal
set "VCVARS="

set "VSWHERE=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe"
if exist "%VSWHERE%" (
  for /f "usebackq tokens=*" %%i in (`"%VSWHERE%" -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath`) do (
    if exist "%%i\VC\Auxiliary\Build\vcvars64.bat" set "VCVARS=%%i\VC\Auxiliary\Build\vcvars64.bat"
  )
)
if not defined VCVARS (
  for /d %%d in ("%ProgramFiles%\Microsoft Visual Studio\*") do (
    if exist "%%d\VC\Auxiliary\Build\vcvars64.bat" set "VCVARS=%%d\VC\Auxiliary\Build\vcvars64.bat"
  )
)
if not defined VCVARS (
  echo [ERROR] Visual Studio C++ build tools were not found.
  echo         Install the "Desktop development with C++" workload,
  echo         or build with gcc:  gcc dino.c -O2 -o dino.exe
  exit /b 1
)

call "%VCVARS%" >nul
pushd "%~dp0"
cl /nologo /W4 /O2 /utf-8 dino.c /Fe:dino.exe
if errorlevel 1 (
  echo.
  echo [ERROR] Build failed.
  popd
  exit /b 1
)
del /q dino.obj >nul 2>&1
echo.
echo [OK] Built dino.exe   -   run it with:  dino.exe
popd
endlocal
