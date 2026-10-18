# HealthInsight — Apache Superset & Trino Connection Guide
**UI Role:** Interactive BI Analytics Dashboard  
**Data Engine:** Trino 435+ querying Apache Iceberg Tables  

---

## 1. Environment Isolation (Mandatory)

> [!WARNING]
> **Do not install Superset in your main PySpark environment.**
> Superset requires specific versions of Flask, SQLAlchemy, and Celery that will conflict with PySpark and Pandas dependencies. Always use an isolated virtual environment.

### Create and Activate Dedicated Superset Environment

#### On Windows (PowerShell):
```powershell
python -m venv venv-superset
.\venv-superset\Scripts\Activate.ps1
pip install -r superset/requirements-superset.txt
```

#### On macOS / Linux:
```bash
python3 -m venv venv-superset
source venv-superset/bin/activate
pip install -r superset/requirements-superset.txt
```

---

## 2. Initialize and Launch Superset

```bash
# 1. Set Superset home directory
export SUPERSET_CONFIG_PATH=$(pwd)/superset/superset_config.py

# 2. Initialize Superset metadata database
superset db upgrade

# 3. Create initial admin user
superset fab create-admin \
  --username admin \
  --firstname Health \
  --lastname Insight \
  --email admin@healthinsight.local \
  --password admin

# 4. Initialize default roles and permissions
superset init

# 5. Start Superset development server on port 8088
superset run -p 8088 --with-threads --reload --debugger
```

Open your browser at: `http://localhost:8088` (Login with `admin` / `admin`).

---

## 3. Connect Superset to Trino

1. In Superset, navigate to:  
   **Settings (top-right cog) → Database Connections → + Database**
2. In the dropdown, select: **Trino**
3. Configure the connection parameters:
   - **Display Name:** `HealthInsight Trino Lakehouse`
   - **SQLAlchemy URI:**
     ```
     trino://localhost:8080/iceberg
     ```
     *(If running Trino with custom auth, use `trino://admin@localhost:8080/iceberg`)*
4. Click **Test Connection**.  
   - Expected Output: `Connection looks good!`
5. Under **Advanced → Security**, ensure:
   - `Allow CREATE TABLE AS / CREATE VIEW AS` (optional)
   - `Expose database in SQL Lab` (checked)
6. Click **Connect / Save**.

---

## 4. Register Virtual Datasets

Navigate to **Datasets → + Dataset**:
- **Database:** `HealthInsight Trino Lakehouse`
- **Schema:** `healthcare`
- **Tables to Register:**
  1. `encounter_analytics` (Primary dataset for visit volumes, costs, durations, trends)
  2. `condition_analytics` (Secondary dataset for condition frequencies and demographic prevalence)

---

## 5. Troubleshooting Trino Connection

| Error Message | Root Cause | Solution |
|---|---|---|
| `No module named 'trino'` | Trino Python client not installed in `venv-superset`. | Run `pip install trino` inside `venv-superset`. |
| `Connection refused on localhost:8080` | Trino server daemon is not running. | Run `docker compose up -d` or start Trino CLI/server. |
| `Schema 'healthcare' not found` | Pipeline has not ingested data to Iceberg yet. | Run `python spark/02_ingest_raw_to_iceberg.py` and `spark/03_build_analytics_tables.py`. |
