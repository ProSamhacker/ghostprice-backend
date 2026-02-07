# Quick Setup Instructions for Windows Task Scheduler

## 🚀 Option 1: Automatic Setup (Recommended)

**Just run this PowerShell script:**

1. Right-click `setup_scheduled_tasks.ps1`
2. Select "Run with PowerShell"
3. Done! Both tasks are created automatically

**What it creates:**
- ✅ Weekly Discovery (Sundays 1 AM)
- ✅ Daily Scraper (Every day 2 AM)

---

## 📋 Option 2: Manual Setup

If the script doesn't work, follow these steps:

### Step 1: Open Task Scheduler
- Press `Win + R`
- Type: `taskschd.msc`
- Press Enter

### Step 2: Create Weekly Discovery Task

1. Click "Create Basic Task..."
2. **Name**: `GhostPrice Weekly Discovery`
3. **Description**: `Discovers new electronics from Amazon`
4. **Trigger**: Weekly → Sunday → 1:00 AM
5. **Action**: Start a program
   - **Program**: `python`
   - **Arguments**: `discover_products.py`
   - **Start in**: `C:\Users\SAMIR\Desktop\WEBSITE\GHOST PRICE\ext\backend`
6. **Finish** → Check "Open Properties" → OK

**In Properties:**
- General tab:
  - ☑ Run whether user is logged on or not
  - ☑ Run with highest privileges
- Conditions tab:
  - ☐ Start only if on AC power (uncheck)
  - ☑ Wake computer to run
- Settings tab:
  - ☑ Run task as soon as possible after missed
  - Stop task if runs longer than: `2 hours`

### Step 3: Create Daily Scraper Task

1. Click "Create Basic Task..."
2. **Name**: `GhostPrice Daily Scraper`
3. **Description**: `Updates prices for tracked products`
4. **Trigger**: Daily → 2:00 AM
5. **Action**: Start a program
   - **Program**: `python`
   - **Arguments**: `daily_price_scraper.py`
   - **Start in**: `C:\Users\SAMIR\Desktop\WEBSITE\GHOST PRICE\ext\backend`
6. **Finish** → Configure same properties as above

---

## ✅ Verify Tasks Work

**Test immediately (don't wait for schedule):**
1. Open Task Scheduler
2. Find your task
3. Right-click → Run
4. Check database: `python view_database.py stats`

**Check task history:**
1. Select task
2. Click "History" tab
3. Look for successful runs

---

## 📊 Expected Schedule

**Week 1-4 (Build Phase):**
```
Sunday 1 AM:  Product Discovery (~30-45 min)
Daily 2 AM:   Price Scraping (~5-15 min)
```

**After Month 3 (Maintenance):**
```
First Sunday: Product Discovery (optional)
Daily 2 AM:   Price Scraping (always)
```

---

## 🔧 Troubleshooting

**Task runs but nothing happens:**
- Check Python path: `where python` in cmd
- Use full path: `C:\Python311\python.exe` instead of `python`

**Task fails with error:**
- Check logs folder for error messages
- Verify working directory is correct
- Ensure Python packages installed

**Computer doesn't wake:**
- BIOS: Enable "Wake on RTC"
- Power Options: Allow wake timers

---

## 🎯 You're All Set!

After setup:
- ✅ Products discovered automatically every Sunday
- ✅ Prices updated automatically every day
- ✅ Database grows without manual work
- ✅ Extension gets better data daily

**No more manual work needed!** 🎉
