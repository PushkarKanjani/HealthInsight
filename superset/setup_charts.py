import json
from superset.app import create_app

app = create_app()
with app.app_context():
    from superset.extensions import db
    from superset.connectors.sqla.models import SqlaTable
    from superset.models.dashboard import Dashboard
    from superset.models.slice import Slice

    # 1. Fetch datasets
    t_enc = db.session.query(SqlaTable).filter_by(table_name="encounter_analytics").first()
    t_cond = db.session.query(SqlaTable).filter_by(table_name="condition_analytics").first()

    if not t_enc or not t_cond:
        print("Error: Datasets not found!")
        exit(1)

    dashboard = db.session.query(Dashboard).filter_by(id=1).first()
    if not dashboard:
        print("Error: Dashboard id=1 not found!")
        exit(1)

    # Helper to add or update slice
    def get_or_create_slice(name, viz_type, datasource, params):
        s = db.session.query(Slice).filter_by(slice_name=name).first()
        if not s:
            s = Slice(
                slice_name=name,
                viz_type=viz_type,
                datasource_type="table",
                datasource_id=datasource.id,
                params=json.dumps(params)
            )
            db.session.add(s)
            db.session.commit()
            print(f"Created chart: {name}")
        else:
            s.params = json.dumps(params)
            db.session.commit()
            print(f"Updated chart: {name}")
        return s

    # Chart 1: Total Encounters (Big Number)
    c1 = get_or_create_slice(
        name="Total Encounters",
        viz_type="big_number_total",
        datasource=t_enc,
        params={
            "metric": "count",
            "subheader": "Recorded Synthetic Healthcare Encounters"
        }
    )

    # Chart 2: Total Patients (Big Number)
    c2 = get_or_create_slice(
        name="Total Patients",
        viz_type="big_number_total",
        datasource=t_enc,
        params={
            "metric": {
                "expressionType": "SQL",
                "sqlExpression": "COUNT(DISTINCT patient_id)",
                "label": "Distinct Patients"
            },
            "subheader": "Unique Synthea Synthetic Patients"
        }
    )

    # Chart 3: Average Claim Cost (Big Number)
    c3 = get_or_create_slice(
        name="Average Claim Cost ($)",
        viz_type="big_number_total",
        datasource=t_enc,
        params={
            "metric": {
                "expressionType": "SQL",
                "sqlExpression": "ROUND(AVG(total_claim_cost), 2)",
                "label": "Avg Claim Cost"
            },
            "subheader": "Mean Recorded Claim Cost (USD)"
        }
    )

    # Chart 4: Encounters by Class (Distribution Bar Chart)
    c4 = get_or_create_slice(
        name="Encounters by Class",
        viz_type="dist_bar",
        datasource=t_enc,
        params={
            "metrics": ["count"],
            "groupby": ["encounter_class"],
            "row_limit": 10,
            "order_desc": True,
            "show_legend": True,
            "show_bar_value": True
        }
    )

    # Chart 5: Top 10 Recorded Conditions (Distribution Bar Chart)
    c5 = get_or_create_slice(
        name="Top 10 Diagnosed Conditions",
        viz_type="dist_bar",
        datasource=t_cond,
        params={
            "metrics": ["count"],
            "groupby": ["condition_description"],
            "row_limit": 10,
            "order_desc": True,
            "show_legend": True,
            "show_bar_value": True
        }
    )

    # Chart 6: Encounters by Age Group
    c6 = get_or_create_slice(
        name="Encounters by Age Group",
        viz_type="pie",
        datasource=t_enc,
        params={
            "metric": "count",
            "groupby": ["age_group"],
            "row_limit": 10
        }
    )

    # Chart 7: Gender Distribution
    c7 = get_or_create_slice(
        name="Patient Gender Distribution",
        viz_type="pie",
        datasource=t_enc,
        params={
            "metric": {
                "expressionType": "SQL",
                "sqlExpression": "COUNT(DISTINCT patient_id)",
                "label": "Patients"
            },
            "groupby": ["patient_gender"],
            "row_limit": 5
        }
    )

    # Add all slices to the dashboard
    slices = [c1, c2, c3, c4, c5, c6, c7]
    dashboard.slices = slices
    
    # Construct standard responsive grid layout
    position_data = {
        "DASHBOARD_VERSION_KEY": "v2",
        "ROOT_ID": {"children": ["GRID_ID"], "id": "ROOT_ID", "type": "ROOT", "meta": {"background": "BACKGROUND_TRANSPARENT"}},
        "GRID_ID": {"children": ["ROW_HEADER", "ROW_KPIS", "ROW_CHARTS1", "ROW_CHARTS2"], "id": "GRID_ID", "parents": ["ROOT_ID"], "type": "GRID", "meta": {"background": "BACKGROUND_TRANSPARENT"}},
        
        "ROW_HEADER": {"children": ["HEADER_TEXT"], "id": "ROW_HEADER", "parents": ["ROOT_ID", "GRID_ID"], "type": "ROW", "meta": {"background": "BACKGROUND_TRANSPARENT"}},
        "HEADER_TEXT": {
            "id": "HEADER_TEXT",
            "parents": ["ROOT_ID", "GRID_ID", "ROW_HEADER"],
            "type": "MARKDOWN",
            "meta": {
                "width": 12,
                "code": "### HealthInsight Healthcare Analytics Platform\n> **Notice:** *HealthInsight is a local educational prototype for descriptive analytics over synthetic healthcare records (Synthea). No real patient data or clinical diagnosis.*",
                "background": "BACKGROUND_TRANSPARENT"
            }
        },

        "ROW_KPIS": {"children": [f"CHART_{c1.id}", f"CHART_{c2.id}", f"CHART_{c3.id}"], "id": "ROW_KPIS", "parents": ["ROOT_ID", "GRID_ID"], "type": "ROW", "meta": {"background": "BACKGROUND_TRANSPARENT"}},
        f"CHART_{c1.id}": {"children": [], "id": f"CHART_{c1.id}", "meta": {"chartId": c1.id, "width": 4, "height": 30, "background": "BACKGROUND_TRANSPARENT"}, "parents": ["ROOT_ID", "GRID_ID", "ROW_KPIS"], "type": "CHART"},
        f"CHART_{c2.id}": {"children": [], "id": f"CHART_{c2.id}", "meta": {"chartId": c2.id, "width": 4, "height": 30, "background": "BACKGROUND_TRANSPARENT"}, "parents": ["ROOT_ID", "GRID_ID", "ROW_KPIS"], "type": "CHART"},
        f"CHART_{c3.id}": {"children": [], "id": f"CHART_{c3.id}", "meta": {"chartId": c3.id, "width": 4, "height": 30, "background": "BACKGROUND_TRANSPARENT"}, "parents": ["ROOT_ID", "GRID_ID", "ROW_KPIS"], "type": "CHART"},

        "ROW_CHARTS1": {"children": [f"CHART_{c4.id}", f"CHART_{c5.id}"], "id": "ROW_CHARTS1", "parents": ["ROOT_ID", "GRID_ID"], "type": "ROW", "meta": {"background": "BACKGROUND_TRANSPARENT"}},
        f"CHART_{c4.id}": {"children": [], "id": f"CHART_{c4.id}", "meta": {"chartId": c4.id, "width": 6, "height": 50, "background": "BACKGROUND_TRANSPARENT"}, "parents": ["ROOT_ID", "GRID_ID", "ROW_CHARTS1"], "type": "CHART"},
        f"CHART_{c5.id}": {"children": [], "id": f"CHART_{c5.id}", "meta": {"chartId": c5.id, "width": 6, "height": 50, "background": "BACKGROUND_TRANSPARENT"}, "parents": ["ROOT_ID", "GRID_ID", "ROW_CHARTS1"], "type": "CHART"},

        "ROW_CHARTS2": {"children": [f"CHART_{c6.id}", f"CHART_{c7.id}"], "id": "ROW_CHARTS2", "parents": ["ROOT_ID", "GRID_ID"], "type": "ROW", "meta": {"background": "BACKGROUND_TRANSPARENT"}},
        f"CHART_{c6.id}": {"children": [], "id": f"CHART_{c6.id}", "meta": {"chartId": c6.id, "width": 6, "height": 50, "background": "BACKGROUND_TRANSPARENT"}, "parents": ["ROOT_ID", "GRID_ID", "ROW_CHARTS2"], "type": "CHART"},
        f"CHART_{c7.id}": {"children": [], "id": f"CHART_{c7.id}", "meta": {"chartId": c7.id, "width": 6, "height": 50, "background": "BACKGROUND_TRANSPARENT"}, "parents": ["ROOT_ID", "GRID_ID", "ROW_CHARTS2"], "type": "CHART"}
    }
    
    dashboard.position_json = json.dumps(position_data)
    dashboard.json_metadata = json.dumps({
        "color_scheme": "supersetColors",
        "color_namespace": "default",
        "expanded_slices": {},
        "refresh_frequency": 0,
        "timed_refresh_immune_slices": []
    })
    db.session.commit()
    print("Dashboard layout and charts successfully populated!")
