# HealthInsight — Team Setup & "Works on My Machine" Prevention Guide
**Team Members:** Hemang (23BIT140), Sachi (23BIT142), Yug (23BIT149), Pushkar (23BIT153)  
**Target Environments:** Windows 10/11, macOS (Apple Silicon/Intel), Ubuntu/Debian Linux  

---

## 1. Golden Rules to Prevent "Works on My Machine" Errors

1. **NEVER Hardcode Absolute Local Paths in Code:**
   - ❌ `C:\Users\Asus\Desktop\HealthInsight\...` (Breaks immediately on a teammate's computer).
   - ✅ Always use project-relative paths or `.env` configuration:
     ```python
     import os
     from pathlib import Path
     PROJECT_ROOT = Path(__file__).resolve().parent.parent
     WAREHOUSE_DIR = os.getenv("ICEBERG_WAREHOUSE", str(PROJECT_ROOT / "iceberg" / "warehouse"))
     ```
2. **Always Use Forward Slashes for File URIs in Iceberg & Trino:**
   - Windows backslashes (`\`) break Spark URI parsers.
   - Always convert: `warehouse_path.replace("\\", "/")`.
3. **NEVER Commit `.env` or Big Data Binaries to Git:**
   - `.env` stays on your local machine.
   - Commit `.env.example` with clean placeholders.
4. **Lock All Core Engine Versions Together:**
   - Spark 3.5.x + Scala 2.12 + Iceberg 1.8.x + Mongo Connector 10.4.x + Java 17 LTS.

---

## 2. Step-by-Step Environment Setup by OS

### A. Windows Setup (Pushkar, etc.)

#### 1. Java 17 LTS Installation
Spark 3.5 requires **Java 17 LTS**.
- Download **Eclipse Temurin OpenJDK 17 (x64 Windows MSI installer)** from:  
  [https://adoptium.net/temurin/releases/?version=17](https://adoptium.net/temurin/releases/?version=17)
- During installation, **enable "Set JAVA_HOME variable"** and **"Add to PATH"**.
- Verify in PowerShell:
  ```powershell
  java -version
  # Must output: openjdk version "17.0.x"
  ```

#### 2. The Classic Windows Hadoop "winutils.exe" Fix
On Windows, Apache Spark requires `winutils.exe` and `hadoop.dll` to manage local file permissions. If missing, Spark throws:  
`java.io.IOException: Could not locate executable null\bin\winutils.exe`

**To fix permanently in 1 minute:**
1. Create folder: `C:\hadoop\bin`
2. Download `winutils.exe` and `hadoop.dll` for Hadoop 3.3.6 from the official GitHub repo:  
   `https://github.com/steveloughran/winutils/tree/master/hadoop-3.3.6/bin`
3. Set environment variable:
   ```powershell
   [System.Environment]::SetEnvironmentVariable("HADOOP_HOME", "C:\hadoop", "User")
   [System.Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\hadoop\bin", "User")
   ```

---

### B. macOS Setup (Apple Silicon M1/M2/M3 or Intel)

Using Homebrew:
```bash
# 1. Install Java 17
brew install openjdk@17
sudo ln -sfn /opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk /Library/Java/JavaVirtualMachines/openjdk-17.jdk
export JAVA_HOME="/opt/homebrew/opt/openjdk@17"

# 2. Python Environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

### C. Linux Setup (Ubuntu / Debian)

```bash
# 1. Install Java 17
sudo apt update
sudo apt install -y openjdk-17-jdk

# 2. Python Environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 3. The 1-Command Database & Trino Setup (Docker Compose)

To prevent teammates from having to manually install, configure, and troubleshoot Trino and MongoDB services, the repository provides `docker-compose.yml`.

Any teammate on any OS can start the exact same Trino and MongoDB instances with:
```bash
docker compose up -d
```

- **Trino Web UI:** `http://localhost:8080`
- **MongoDB Server:** `localhost:27017`

To shut down:
```bash
docker compose down
```

---

## 4. Git Collaboration Workflow

When working on features:
1. **Pull before starting:** `git pull origin main`
2. **Work in branches or atomic commits:**
   - Hemang: `git commit -m "feat(spark): ..."`
   - Sachi: `git commit -m "feat(iceberg): ..."`
   - Pushkar: `git commit -m "feat(trino): ..."`
   - Yug: `git commit -m "feat(superset): ..."`
3. **Verify services before pushing:**
   - On Windows: `powershell scripts/check_versions.ps1`
   - On Mac/Linux: `bash scripts/check_versions.sh`
