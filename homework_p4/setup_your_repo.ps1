$repo = "C:\Users\Lenovo\Documents\ukma\intro-to-prog"
$snap = "C:\Users\Lenovo\Documents\ukma\intro-to-prog\_snapshots"

if (Test-Path $repo) { Remove-Item -Recurse -Force $repo }
New-Item -ItemType Directory -Path $snap -Force | Out-Null

function gitc { param([string[]]$a) & git -C $repo @a }

gitc @("init", "-b", "main") | Out-Null
gitc @("config", "user.email", "l.vynnyk@ukma.edu.ua")
gitc @("config", "user.name", "Liubomyr Vynnyk")

# 1-2-3
gitc @("checkout", "-b", "main_backup") | Out-Null
Set-Content -Path (Join-Path $repo "main.c") -Value "#include <stdio.h>"
gitc @("add", "main.c")
gitc @("commit", "-m", "Add main.c with basic content") | Out-Null

# 5
gitc @("checkout", "-b", "feature_rebase") | Out-Null

# 6
gitc @("checkout", "main_backup") | Out-Null
Add-Content -Path (Join-Path $repo "main.c") -Value "int main_var = 0;"
gitc @("add", "main.c")
gitc @("commit", "-m", "changes in mainline") | Out-Null

# 7
gitc @("checkout", "feature_rebase") | Out-Null
Add-Content -Path (Join-Path $repo "main.c") -Value "int feature_var_1 = 0;"
gitc @("add", "main.c")
gitc @("commit", "-m", "Add feature_var_1 to main.c") | Out-Null

# SNAPSHOT 1
gitc @("log", "--oneline") | Set-Content (Join-Path $snap "1_after_step7.txt")

# 8
Add-Content -Path (Join-Path $repo "main.c") -Value "int feature_var_2 = 0;"
gitc @("add", "main.c")
gitc @("commit", "-m", "Add feature_var_2 to main.c") | Out-Null

# 10-11 rebase + resolve conflict
git -c core.editor=true -C $repo rebase main_backup | Out-Null
Set-Content -Path (Join-Path $repo "main.c") -Value @(
    "#include <stdio.h>"
    "int main_var = 0;"
    "int feature_var_1 = 0;"
)
gitc @("add", "main.c")
git -c core.editor=true -C $repo rebase --continue | Out-Null

# SNAPSHOT 2
gitc @("log", "--oneline") | Set-Content (Join-Path $snap "2_after_rebase.txt")

# 14 merge
gitc @("checkout", "main_backup") | Out-Null
gitc @("merge", "feature_rebase") | Out-Null

# SNAPSHOT 3
gitc @("log", "--oneline") | Set-Content (Join-Path $snap "3_after_merge.txt")

Write-Output "=== DONE. main_backup history ==="
gitc @("log", "--oneline", "--graph", "--all")
Write-Output "=== main.c content ==="
Get-Content (Join-Path $repo "main.c")
Write-Output "=== snapshot files ==="
Get-ChildItem -Path $snap -Filter *.txt | Select-Object -ExpandProperty FullName
