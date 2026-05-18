"""Dashboard Streamlit — laSalle Health Center (Día 7)."""

from __future__ import annotations

import os

import httpx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from app.api_client import (
    API_URL,
    acknowledge_alert,
    get_dashboard,
    get_logs,
    get_study_image,
)

st.set_page_config(
    page_title="laSalle Health — Dashboard",
    page_icon="🫁",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("laSalle Health Center")
st.caption("Dashboard operativo · Día 7 — métricas IA, pipeline y alertas")


@st.cache_data(ttl=30)
def load_data() -> dict:
    return get_dashboard()


def render_health(health: dict) -> None:
    status = health.get("status", "unknown")
    color = "🟢" if status == "ok" else "🟠"
    st.subheader(f"{color} Estado del sistema: {status.upper()}")
    checks = health.get("checks") or {}
    cols = st.columns(len(checks) or 1)
    labels = {"database": "PostgreSQL", "minio": "MinIO", "ml": "Servicio ML"}
    for i, (key, chk) in enumerate(checks.items()):
        ok = chk.get("ok")
        with cols[i % len(cols)]:
            st.metric(labels.get(key, key), "OK" if ok else "FALLO")
            if not ok and chk.get("error"):
                st.caption(str(chk["error"])[:120])


def render_metrics(metrics: dict) -> None:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Predicciones", metrics.get("predictions_total", 0))
    c2.metric("Subidas API", metrics.get("api_uploads", 0))
    c3.metric("Pacientes", metrics.get("patients_total", 0))
    c4.metric("Modelo", metrics.get("model_version", "—"))


def render_class_charts(pct_rows: list, ml_eval: dict | None) -> None:
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Predicciones en producción (% por clase)")
        if pct_rows:
            df = pd.DataFrame(pct_rows)
            fig = px.pie(
                df,
                values="count",
                names="label",
                hole=0.35,
                color="label",
                color_discrete_map={
                    "covid": "#bf5af2",
                    "neumonia": "#ff9f0a",
                    "sana": "#30d158",
                },
            )
            fig.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=320)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Aún no hay predicciones registradas.")
    with col_b:
        st.subheader("Evaluación modelo (test)")
        if ml_eval and ml_eval.get("confusion_matrix"):
            labels = ml_eval.get("labels") or ["covid", "neumonia", "sana"]
            cm = ml_eval["confusion_matrix"]
            fig = go.Figure(
                data=go.Heatmap(
                    z=cm,
                    x=[f"Pred {l}" for l in labels],
                    y=[f"Real {l}" for l in labels],
                    colorscale="Blues",
                    text=cm,
                    texttemplate="%{text}",
                )
            )
            fig.update_layout(height=320, margin=dict(t=30, b=30))
            st.plotly_chart(fig, use_container_width=True)
            st.metric("FN neumonía → sana (test)", ml_eval.get("fn_neumonia_to_sana", "—"))
            st.metric("Errores totales (off-diagonal)", ml_eval.get("misclassified_total", "—"))
            acc = ml_eval.get("accuracy_test")
            if acc is not None:
                st.caption(f"Accuracy test: {float(acc) * 100:.1f}%")
        else:
            st.info("Informe de entrenamiento no disponible en la API.")


def render_images(studies: list) -> None:
    st.subheader("Imágenes procesadas")
    if not studies:
        st.info("No hay estudios con imagen en MinIO.")
        return
    cols = st.columns(4)
    for i, s in enumerate(studies):
        with cols[i % 4]:
            img = get_study_image(s["study_id"])
            if img:
                st.image(img, use_container_width=True)
            else:
                st.caption("Sin vista previa")
            st.markdown(f"**`{s['study_id']}`**")
            pred = s.get("predicted_label") or "—"
            conf = s.get("confidence")
            line = f"{pred}"
            if conf is not None:
                line += f" · {float(conf) * 100:.0f}%"
            st.caption(line)
            if s.get("patient_name"):
                st.caption(s["patient_name"])


def render_pipeline_summary(summary: dict) -> None:
    st.subheader("Estado del pipeline (resumen)")
    c1, c2, c3 = st.columns(3)
    c1.metric("OK", summary.get("ok", 0))
    c2.metric("En curso", summary.get("running", 0))
    c3.metric("Fallidos", summary.get("failed", 0))
    st.caption("Detalle de líneas de log en MongoDB (pestaña Logs).")


def render_logs() -> None:
    st.subheader("Logs centralizados (MongoDB)")
    col = st.selectbox(
        "Colección",
        ("application_logs", "airflow_logs", "file_logs"),
        key="log_collection",
    )
    c1, c2, c3 = st.columns(3)
    service = c1.text_input("Servicio (opcional)", placeholder="api, ml, watcher…")
    level = c2.selectbox("Nivel", ("", "DEBUG", "INFO", "WARNING", "ERROR"))
    limit = c3.number_input("Límite", min_value=10, max_value=500, value=100, step=10)
    try:
        payload = get_logs(
            col,
            service=service.strip() or None,
            level=level or None,
            limit=int(limit),
        )
    except httpx.HTTPError as exc:
        st.error(f"No se pudieron cargar logs: {exc}")
        return
    items = payload.get("items") or []
    st.caption(f"{payload.get('count', 0)} registros · colección `{col}`")
    if not items:
        st.info("Sin entradas para los filtros seleccionados.")
        return
    df = pd.DataFrame(items)
    cols = [c for c in ("timestamp", "level", "service", "logger", "message", "path") if c in df.columns]
    st.dataframe(df[cols] if cols else df, use_container_width=True, hide_index=True)


def render_alerts(alerts: list) -> None:
    st.subheader("Alertas")
    if not alerts:
        st.success("No hay alertas activas en el sistema.")
        return
    for a in alerts:
        sev = a.get("severity", "info")
        icon = {"critical": "🔴", "warning": "🟠", "info": "🔵"}.get(sev, "⚪")
        with st.expander(f"{icon} {a.get('title', 'Alerta')} — {a.get('created_at', '')}"):
            st.write(a.get("message", ""))
            if a.get("run_id"):
                st.caption(f"Run: {a['run_id']}")
            if not a.get("acknowledged"):
                if st.button("Marcar como leída", key=f"ack_{a['alert_id']}"):
                    if acknowledge_alert(int(a["alert_id"])):
                        st.cache_data.clear()
                        st.rerun()


with st.sidebar:
    st.markdown(f"**API:** `{API_URL}`")
    if st.button("Actualizar datos"):
        st.cache_data.clear()
        st.rerun()

try:
    data = load_data()
except httpx.HTTPError as exc:
    st.error(f"No se pudo conectar con la API ({API_URL}): {exc}")
    st.stop()

render_health(data.get("health") or {})
st.divider()
render_metrics(data.get("metrics") or {})

tab_ia, tab_img, tab_logs, tab_alert = st.tabs(
    ["IA y clases", "Imágenes", "Logs", "Alertas"]
)

with tab_ia:
    render_class_charts(
        data.get("predictions_by_class") or [],
        data.get("ml_evaluation"),
    )

with tab_img:
    render_images(data.get("recent_studies") or [])

with tab_logs:
    render_pipeline_summary(data.get("pipeline_summary") or {})
    st.divider()
    render_logs()

with tab_alert:
    render_alerts(data.get("alerts") or [])
