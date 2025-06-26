# 📤 File Transfer Instructions

## Method 1: SCP (Mac/Linux)

```bash
# Upload entire package
scp -i ~/.ssh/oracle_cloud_key -r instagram-automation-cloud-package ubuntu@YOUR_VM_IP:~/

# SSH into VM
ssh -i ~/.ssh/oracle_cloud_key ubuntu@YOUR_VM_IP

# Navigate and setup
cd instagram-automation-cloud-package
./quick_setup.sh
```

## Method 2: WinSCP (Windows)

1. Download and install WinSCP
2. Connect using your Oracle Cloud SSH key
3. Upload the entire `instagram-automation-cloud-package` folder
4. Use PuTTY to SSH into your VM
5. Run: `cd instagram-automation-cloud-package && ./quick_setup.sh`

## Method 3: Git Repository (Recommended)

1. Upload package to GitHub/GitLab
2. SSH into Oracle Cloud VM
3. Run: `git clone YOUR_REPOSITORY_URL`
4. Navigate and setup: `cd YOUR_REPO && ./quick_setup.sh`

## Verification

After upload, verify all files are present:
```bash
ls -la instagram-automation-cloud-package/
```

Should show:
- cloud_instagram_bot.py
- cloud_scheduler.py  
- cloud_web_dashboard.py
- cloud_deploy.sh
- quick_setup.sh
- README.md
- And more...
