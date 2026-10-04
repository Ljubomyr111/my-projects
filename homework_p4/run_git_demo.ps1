$dir = "C:\Users\Lenovo\Documents\deepseek-harness\default-workspace\homework_p4\git_demo"
$out = "C:\Users\Lenovo\Documents\deepseek-harness\default-workspace\homework_p4"

if (Test-Path $dir) { Remove-Item -Recurse -Force $dir }
New-Item -ItemType Directory -Path $dir | Out-Null

function gitc { param([string[]]$a) & git -C $dir @a }

gitc @("init", "-b", "main") | Out-Null
gitc @("config", "user.email", "student@ukma.edu.ua")
gitc @("config", "user.name", "Student")

# step 1
gitc @("checkout", "-b", "main_backup") | Out-Null
# step 2
Set-Content -Path (Join-Path $dir "main.c") -Value "#include <stdio.h>"
# step 3
gitc @("add", "main.c")
gitc @("commit", "-m", "Add main.c with basic content") | Out-Null
# step 4
Write-Output "=== step 4: log after first commit ==="
gitc @("log", "--oneline")

# step 5
gitc @("checkout", "-b", "feature_rebase") | Out-Null
# step 6
gitc @("checkout", "main_backup") | Out-Null
Add-Content -Path (Join-Path $dir "main.c") -Value "int main_var = 0;"
gitc @("add", "main.c")
gitc @("commit", "-m", "changes in mainline") | Out-Null

# step 7
gitc @("checkout", "feature_rebase") | Out-Null
Add-Content -Path (Join-Path $dir "main.c") -Value "int feature_var_1 = 0;"
gitc @("add", "main.c")
gitc @("commit", "-m", "Add feature_var_1 to main.c") | Out-Null

# SNAPSHOT 1
gitc @("log", "--oneline") | Set-Content (Join-Path $out "snapshot1_after_step7.txt")

# step 8
Add-Content -Path (Join-Path $dir "main.c") -Value "int feature_var_2 = 0;"
gitc @("add", "main.c")
gitc @("commit", "-m", "Add feature_var_2 to main.c") | Out-Null

# step 9
Write-Output "=== step 9: feature_rebase history (expect 2 commits on top of main.c) ==="
gitc @("log", "--oneline")

# step 10: rebase (conflict expected)
Write-Output "=== step 10-11: rebase + resolve conflict ==="
git -c core.editor=true -C $dir rebase main_backup
# step 11: resolve conflict (keep main_var + feature_var_1; feature_var_2
# comes from the second commit that will be replayed next)
Set-Content -Path (Join-Path $dir "main.c") -Value @(
    "#include <stdio.h>"
    "int main_var = 0;"
    "int feature_var_1 = 0;"
)
gitc @("add", "main.c")
git -c core.editor=true -C $dir rebase --continue

# SNAPSHOT 2
gitc @("log", "--oneline") | Set-Content (Join-Path $out "snapshot2_after_rebase.txt")

# step 14: merge feature_rebase into main_backup
gitc @("checkout", "main_backup") | Out-Null
gitc @("merge", "feature_rebase")

# step 15/16
Write-Output "=== step 16: main_backup history after merge ==="
gitc @("log", "--oneline")

# SNAPSHOT 3
gitc @("log", "--oneline") | Set-Content (Join-Path $out "snapshot3_after_merge.txt")

Write-Output "=== final main.c ==="
Get-Content (Join-Path $dir "main.c")

Write-Output "=== graph (all branches) ==="
gitc @("log", "--oneline", "--graph", "--all")
