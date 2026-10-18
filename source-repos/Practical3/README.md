# Practical 3 — Code debugging (VS Code)

Ця тека — розв'язок Practical 3 з дисципліни «Introduction to Programming».

## Вміст

| Файл | Призначення |
|---|---|
| `practical.c` | Practical task #2 — програма, що виводить позицію літери в алфавіті |
| `.vscode/launch.json` | конфігурація налагодження у VS Code (GDB) |
| `.vscode/tasks.json` | збірка `gcc -g` перед запуском дебагера |
| `screenshots/` | скріншоти налагодження (Practical task #1) |

## Як зібрати

```bash
gcc -g practical.c -o practical.exe
```

## Як налагоджувати у VS Code

1. Встановити розширення **C/C++** (ms-vscode.cpptools).
2. Відкрити цю теку у VS Code.
3. У `launch.json` за потреби виправити `miDebuggerPath` (шлях до `gdb.exe`;
   на цьому комп'ютері — `C:\msys64\ucrt64\bin\gdb.exe`).
4. Поставити breakpoint у `practical.c` і натиснути **F5**.

## Як налагоджувати у консолі (GDB)

```bash
gcc -g practical.c -o practical.exe
gdb ./practical.exe
(gdb) break practical.c:56
(gdb) run
(gdb) next
(gdb) print letter
(gdb) print position
(gdb) continue
```

## Приклад роботи програми

```
Enter a letter: b
The letter b is at position 2 in the alphabet.
Enter a letter: z
The letter z is at position 26 in the alphabet.
Enter a letter: 2
Invalid input. Stopping...
```
