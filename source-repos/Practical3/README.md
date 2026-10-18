# Practical 3 — Code debugging (VS Code + GDB)

Ця тека — розв'язок Practical 3 з дисципліни «Introduction to Programming».

## Вміст

| Файл | Призначення |
|---|---|
| `practical.c` | Practical task #2 — програма, що виводить позицію літери в алфавіті |
| `.vscode/launch.json` | конфігурація налагодження у VS Code (C/C++ extension + GDB) |
| `.vscode/tasks.json` | збірка `gcc -g` перед запуском дебагера |
| `screenshots/` | скріншоти налагодження (Practical task #1) |

## Як зібрати

У терміналі VS Code (або звичайній консолі):

```bash
gcc -g practical.c -o practical.exe
```

## Як налагоджувати у VS Code (Practical task #1)

1. Встановити розширення **C/C++** (ms-vscode.cpptools).
2. Відкрити цю теку у VS Code.
3. У `.vscode/launch.json` за потреби виправити `miDebuggerPath` — шлях до
   `gdb.exe` (на цьому комп'ютері `C:\msys64\ucrt64\bin\gdb.exe`).
4. Поставити breakpoint у `practical.c` (рядок 58, перед `printf`) і натиснути **F5**.
5. Ввести літеру в інтегрованому терміналі — виконання зупиниться на breakpoint,
   у панелі **VARIABLES** буде видно `letter` та `position`.

Скріншоти цього процесу: `screenshots/01_vscode_breakpoint_b.png`,
`screenshots/02_vscode_breakpoint_z.png`, `screenshots/03_vscode_session_finished.png`.

## Як налагоджувати у консолі (GDB)

```bash
gcc -g practical.c -o practical.exe
gdb -q practical.exe
(gdb) break practical.c:58
(gdb) run
(gdb) info locals
(gdb) print letter
(gdb) continue
```

Скріншоти консольного GDB: `screenshots/04_gdb_breakpoint_b.png`,
`screenshots/05_gdb_breakpoint_z.png`.

## Приклад роботи програми

```
Enter a letter: b
The letter b is at position 2 in the alphabet.
Enter a letter: z
The letter z is at position 26 in the alphabet.
Enter a letter: 2
Invalid input. Stopping...
```
