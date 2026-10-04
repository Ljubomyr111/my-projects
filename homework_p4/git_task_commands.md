# Practical 4 — Task #1 (Git) — покрокові команди

Команди нижче відповідають крокам 1–17 з «P4 — Git tips.pdf».
Файли (`main.c`) можна створювати через редактор або `echo` (у Git Bash).

```bash
# 1. Створити гілку main_backup
git checkout -b main_backup

# 2. Створити main.c із базовим вмістом
echo '#include <stdio.h>' > main.c

# 3. Закомітити файл у main_backup
git add main.c
git commit -m "Add main.c with basic content"

# 4. Переглянути історію
git log --oneline

# 5. Створити гілку feature_rebase
git checkout -b feature_rebase

# 6. Повернутись у main_backup і додати рядок
git checkout main_backup
echo 'int main_var = 0;' >> main.c
git add main.c
git commit -m "changes in mainline"

# 7. Перейти у feature_rebase і додати рядок
git checkout feature_rebase
echo 'int feature_var_1 = 0;' >> main.c
git add main.c
git commit -m "Add feature_var_1 to main.c"

### >>> ЗНІМОК 1: git log після кроку 7 (2 коміти в локальній гілці) <<<
git log --oneline

# 8. Додати ще один рядок і закомітити
echo 'int feature_var_2 = 0;' >> main.c
git add main.c
git commit -m "Add feature_var_2 to main.c"

# 9. Перевірити історію feature_rebase (2 коміти, зміни main ще не включено)
git log --oneline

# 10. Rebase feature_rebase поверх main_backup (очікується конфлікт)
git rebase main_backup

# 11. Розв'язати конфлікт: залишити ВСІ рядки, окрім останнього
#     (feature_var_2 додасть наступний коміт, який ще буде застосовано)
#     Підсумковий вміст main.c на цьому кроці:
#       #include <stdio.h>
#       int main_var = 0;
#       int feature_var_1 = 0;
git add main.c
git rebase --continue

### >>> ЗНІМОК 2: git log після кроку 13 (після rebase) <<<
git log --oneline
# очікується 3 коміти поверх базового:
#   feature_var_2, feature_var_1, changes in mainline

# 12. (у вашому репозиторії) відправити зміни:
git push origin feature_rebase

# 14. Змерджити feature_rebase у main_backup
git checkout main_backup
git merge feature_rebase
# примітка: оскільки feature_rebase попереду, це буде fast-forward;
# якщо потрібен окремий merge-коміт — використайте: git merge --no-ff feature_rebase

### >>> ЗНІМОК 3: git log після кроку 15 (після merge) <<<
git log --oneline

# 16. Історія main_backup (видно останній коміт з кроку 14)
git log --oneline

# 17. Перейти на main і видалити main_backup
git checkout main          # у вас гілка може називатись master
git branch -d main_backup  # якщо не змерджена повністю — використайте -D

# Очищення гілок
git branch -d feature_rebase
git push origin --delete main_backup feature_rebase   # якщо гілки були на remote
```

## Що здати (3 скриншоти результату `git log`)
1. Після кроку 7 → **2 коміти** у локальній гілці.
2. Після кроку 13 (rebase) → **3 коміти** поверх базового.
3. Після кроку 15 (merge) → main_backup містить коміти feature_rebase.

> Хеші у вашому репозиторії будуть інші — це нормально, важлива структура історії та повідомлення комітів.
