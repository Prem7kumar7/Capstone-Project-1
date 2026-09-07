param(
    [string]$Message = "Update project: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
)

Write-Host "Staging changes..." -ForegroundColor Cyan
git add -A

$status = git status --porcelain
if ([string]::IsNullOrWhiteSpace($status)) {
    Write-Host "No changes detected to commit." -ForegroundColor Yellow
    exit 0
}

Write-Host "Committing with message: '$Message'..." -ForegroundColor Cyan
git commit -m "$Message"

Write-Host "Pushing to origin main..." -ForegroundColor Cyan
git push origin main

Write-Host "Done! Successfully pushed changes to GitHub." -ForegroundColor Green
