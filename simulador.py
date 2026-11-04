import streamlit as st
import pandas as pd
import numpy as np

# Configuración de la página
st.set_page_config(page_title="Simulador Resguarda - HCC", layout="wide")

st.title("📦 Tablero Simulador de Operaciones: Caso Resguarda (HCC)")
st.markdown("Simulación de capacidad, cuello de botella, flujo semanal y evaluación financiera a 52 semanas.")

# ==========================================
# 1. DATOS DE ENTRADA FIJOS (ANEXOS)
# ==========================================
DEMANDA_SEMANAL = {
    "Semana": list(range(1, 53)),
    "Fecha": [
        "05/10", "12/10", "19/10", "26/10", "02/11", "09/11", "16/11", "23/11", "30/11", "07/12",
        "14/12", "21/12", "28/12", "04/01", "11/01", "18/01", "25/01", "01/02", "08/02", "15/02",
        "22/02", "01/03", "08/03", "15/03", "22/03", "29/03", "05/04", "12/04", "19/04", "26/04",
        "03/05", "10/05", "17/05", "24/05", "31/05", "07/06", "14/06", "21/06", "28/06", "05/07",
        "12/07", "19/07", "26/07", "02/08", "09/08", "15/08", "23/08", "30/08", "06/09", "13/09",
        "20/09", "27/09"
    ],
    "Base": [
        700, 800, 950, 1050, 1150, 1300, 1550, 1900, 1750, 1700, 1650, 1300, 900, 960, 970, 970,
        980, 990, 1000, 1000, 1010, 1020, 1030, 1040, 1050, 1050, 1060, 1070, 1080, 1090, 1100, 1110,
        1280, 1290, 1130, 1140, 1150, 1160, 1170, 1180, 1190, 1200, 1210, 1220, 1230, 1240, 1250, 1260,
        1270, 1280, 1290, 1300
    ],
    "Optimista": [
        700, 800, 950, 1050, 1380, 1560, 1860, 2280, 2100, 2040, 1980, 1560, 1080, 1150, 1160, 1160,
        1180, 1190, 1200, 1200, 1210, 1220, 1240, 1250, 1260, 1260, 1270, 1280, 1300, 1310, 1320, 1330,
        1540, 1550, 1360, 1370, 1380, 1390, 1400, 1420, 1430, 1440, 1450, 1460, 1480, 1490, 1500, 1510,
        1520, 1540, 1550, 1560
    ],
    "Canal": [
        700, 800, 950, 1050, 1150, 1300, 1550, 1900, 1750, 1700, 1300, 1000, 650, 650, 650, 660,
        660, 660, 660, 660, 670, 670, 670, 670, 670, 680, 680, 680, 680, 680, 690, 690,
        760, 760, 690, 700, 700, 700, 700, 700, 710, 710, 710, 710, 720, 720, 720, 720,
        720, 730, 730, 730
    ]
}
df_demanda = pd.DataFrame(DEMANDA_SEMANAL)

# ==========================================
# 2. BARRA LATERAL: PALANCAS INTERACTIVAS
# ==========================================
st.sidebar.header("⚙️ Palancas de Decisión")

st.sidebar.subheader("1. Demanda y Mezcla")
escenario_sel = st.sidebar.selectbox("Escenario de Demanda", ["Base", "Optimista", "Canal"], index=0)
usar_mezcla_anexo = st.sidebar.checkbox("Usar mezcla del caso (30% S1-26 / 35% S27-52)", value=True)
mezcla_pro_fija = st.sidebar.slider("Mezcla Pro Fija (%)", 20, 50, 30, 1) / 100.0

col_p1, col_p2, col_p3 = st.sidebar.columns(3)
prob_base = col_p1.number_input("P. Base", 0.0, 1.0, 0.50, 0.05)
prob_opt = col_p2.number_input("P. Opt", 0.0, 1.0, 0.25, 0.05)
prob_can = col_p3.number_input("P. Canal", 0.0, 1.0, 0.25, 0.05)

st.sidebar.subheader("2. Configuración de Líneas")
op_8_operadores = st.sidebar.checkbox("O1. Reequilibrar a 8 operadores ($9k/línea, 3 sem)", value=False)
sem_orden_8op = st.sidebar.number_input("Semana orden 8 op.", 1, 52, 1) if op_8_operadores else 99

op_tercera_linea = st.sidebar.checkbox("O2. Instalar 3ra línea ($48k, 8 sem)", value=False)
sem_orden_3linea = st.sidebar.number_input("Semana orden 3ra línea", 1, 52, 1) if op_tercera_linea else 99

op_disp_puerta = st.sidebar.checkbox("O5. Dispositivo puerta ($22k/línea, 10 sem)", value=False)
sem_orden_disp = st.sidebar.number_input("Semana orden dispositivo", 1, 52, 1) if op_disp_puerta else 99

op_subcontratar = st.sidebar.checkbox("O6. Subcontratar puerta (+$4.80/u, 4 sem)", value=False)
sem_orden_sub = st.sidebar.number_input("Semana orden subcontratación", 1, 52, 1) if op_subcontratar else 99

st.sidebar.subheader("3. Turnos y Horas Extra")
num_turnos = st.sidebar.selectbox("O3. Número de turnos", [1, 2, 3], index=0)
sem_inicio_t2 = st.sidebar.slider("Semana inicio Turno 2 (2 sem prep.)", 1, 52, 3) if num_turnos >= 2 else 99
sem_inicio_t3 = st.sidebar.slider("Semana inicio Turno 3 (2 sem prep.)", 1, 52, 3) if num_turnos == 3 else 99
sabados_mes = st.sidebar.slider("O7. Sábados con horas extra al mes", 0, 3, 0)

st.sidebar.subheader("4. Células de Trabajo")
num_celulas = st.sidebar.slider("O4. Número de células ($15k/célula, 5 sem)", 0, 10, 0)
sem_orden_cel = st.sidebar.number_input("Semana orden células", 1, 52, 1) if num_celulas > 0 else 99
penalizacion_cel = st.sidebar.slider("Penalización polivalencia (%)", 0, 20, 8) / 100.0

st.sidebar.subheader("5. Lotes y Parámetros Técnicos")
lote_q = st.sidebar.slider("Tamaño de lote (Q)", 25, 400, 100, 25)
tiempo_cambio_s = st.sidebar.slider("Tiempo cambio variante (min)", 5, 40, 20, 5)
incluir_curva = st.sidebar.checkbox("Aplicar curva de aprendizaje al personal nuevo", value=True)

# ==========================================
# 3. MOTOR DE CÁLCULO DE ESTACIONES Y LÍNEA
# ==========================================
def obtener_tiempos_estaciones(ocho_op, disp_puerta, subcontratar):
    if not ocho_op:
        # Línea de 6 estaciones (Anexo 3)
        estaciones = ["E1: Gabinete", "E2: Sub. Puerta", "E3: Inst. Puerta", "E4: Cableado", "E5: Pruebas", "E6: Empaque"]
        t_est = [6.50, 6.20, 8.00, 7.00, 6.50, 5.67]
        t_pro = [6.50, 6.20, 8.00, 8.60, 7.50, 5.67]
        if disp_puerta:
            t_est[1], t_pro[1] = 5.60, 5.60
            t_est[2], t_pro[2] = 6.00, 6.00
        if subcontratar:
            # Desaparece E2, E3 baja a 7.20
            estaciones.pop(1)
            t_est.pop(1)
            t_pro.pop(1)
            t_est[1], t_pro[1] = 7.20, 7.20
    else:
        # Línea de 8 estaciones (Anexo 4)
        estaciones = ["L1: Ens. Gab", "L2: Sold. Gab", "L3: Ens. Puerta", "L4: Cableado", "L5: Inst. Puerta", "L6: Mont. Eléc", "L7: Pruebas", "L8: Embalaje"]
        t_est = [5.00, 5.20, 5.80, 4.10, 4.30, 4.80, 5.00, 5.67]
        t_pro = [5.00, 5.20, 5.80, 4.10, 4.30, 6.40, 6.00, 5.67]
        if disp_puerta:
            t_est[2], t_pro[2] = 5.20, 5.20
            t_est[4], t_pro[4] = 3.30, 3.30
        if subcontratar:
            # Si subcontrata en línea de 8, desaparece L3 (Ens. puerta)
            estaciones.pop(2)
            t_est.pop(2)
            t_pro.pop(2)
    return estaciones, t_est, t_pro

# ==========================================
# 4. MOTOR DE SIMULACIÓN DE 52 SEMANAS
# ==========================================
def simular_52_semanas(params, escenario_dem):
    demanda_serie = df_demanda[escenario_dem].values
    fechas = df_demanda["Fecha"].values
    
    # Parámetros de configuración
    ocho_op = params["op_8_operadores"]
    sem_8op_activa = params["sem_orden_8op"] + 3 if ocho_op else 999
    
    tercera_linea = params["op_tercera_linea"]
    sem_3l_activa = params["sem_orden_3linea"] + 8 if tercera_linea else 999
    
    disp_puerta = params["op_disp_puerta"]
    sem_disp_activa = params["sem_orden_disp"] + 10 if disp_puerta else 999
    
    subcontratar = params["op_subcontratar"]
    sem_sub_activa = params["sem_orden_sub"] + 4 if subcontratar else 999
    
    n_celulas = params["num_celulas"]
    sem_cel_activa = params["sem_orden_cel"] + 5 if n_celulas > 0 else 999
    
    n_turnos = params["num_turnos"]
    sem_t2_activo = max(params["sem_inicio_t2"], 3) if n_turnos >= 2 else 999
    sem_t3_activo = max(params["sem_inicio_t3"], 3) if n_turnos == 3 else 999
    
    lote = params["lote_q"]
    t_cambio = params["tiempo_cambio_s"]
    sabados_mes = params["sabados_mes"]
    
    # Estado inicial (Anexo 8)
    inventario = 300.0
    pendientes_1sem = 0.0 # Esperan su 1ra semana
    pendientes_2sem = 0.0 # Esperan su 2da semana (si no se atienden, se pierden)
    
    registros = []
    inversion_acum = 0.0
    flujo_descontado_acum = 0.0
    tasa_semanal = (1.12 ** (1/52)) - 1
    
    # Contenido base para células (siempre 39.87 y 42.47)
    cont_base_est, cont_base_pro = 39.87, 42.47

    for sem in range(1, 53):
        mezcla_pro = (0.30 if sem <= 26 else 0.35) if params["usar_mezcla_anexo"] else params["mezcla_pro_fija"]
        mezcla_est = 1.0 - mezcla_pro
        
        # Activar opciones según semana
        act_8op = (sem >= sem_8op_activa)
        act_3l = (sem >= sem_3l_activa)
        act_disp = (sem >= sem_disp_activa)
        act_sub = (sem >= sem_sub_activa)
        act_cel = (sem >= sem_cel_activa)
        act_t2 = (sem >= sem_t2_activo)
        act_t3 = (sem >= sem_t3_activo)
        
        lineas_activas = 3 if act_3l else 2
        celulas_activas = n_celulas if act_cel else 0
        turnos_activos = 1 + (1 if act_t2 else 0) + (1 if act_t3 else 0)
        
        # Tiempos de estación vigentes esta semana
        _, t_est, t_pro = obtener_tiempos_estaciones(act_8op, act_disp, act_sub)
        ciclo_est, ciclo_pro = max(t_est), max(t_pro)
        ciclo_medio = (mezcla_est * ciclo_est) + (mezcla_pro * ciclo_pro)
        
        # Horas por turno según esquema (Anexo 5)
        h_prod = 7.0 if turnos_activos == 3 else 7.5
        h_pag = 7.5 if turnos_activos == 3 else 8.0
        
        # Curva de aprendizaje (Anexo 10: 70%, 80%, 90%, 95%, 100%)
        def factor_aprendizaje(sem_actual, sem_inicio):
            if not params["incluir_curva"] or sem_actual < sem_inicio:
                return 1.0
            edad = sem_actual - sem_inicio
            curva = [0.70, 0.80, 0.90, 0.95]
            return curva[edad] if edad < 4 else 1.0

        # Minutos productivos por línea sumando turnos
        min_t1 = h_prod * 5 * 60 * 1.0
        min_t2 = (h_prod * 5 * 60 * 0.92 * factor_aprendizaje(sem, sem_t2_activo)) if act_t2 else 0.0
        min_t3 = (h_prod * 5 * 60 * 0.88 * factor_aprendizaje(sem, sem_t3_activo)) if act_t3 else 0.0
        
        # Sábados (máx 3 al mes -> asignamos a las primeras N semanas de cada bloque de 4 semanas)
        pos_mes = (sem - 1) % 4
        hay_sabado = 1 if pos_mes < sabados_mes else 0
        min_sab = (6.5 * 60) if hay_sabado else 0.0
        
        # Capacidad de líneas
        t_unidad_lote = ciclo_medio + (t_cambio / lote)
        cap_linea_base = (min_t1 + min_t2 + min_t3 + min_sab) / t_unidad_lote
        
        # Si la 3ra línea acaba de entrar, su personal nuevo en T1 tiene curva
        cap_todas_lineas = cap_linea_base * 2
        if act_3l:
            f_3l = factor_aprendizaje(sem, sem_3l_activa)
            cap_3ra = ((min_t1 * f_3l) + min_t2 + min_t3 + (min_sab * f_3l)) / t_unidad_lote
            cap_todas_lineas += cap_3ra
            
        # Límite de subcontratación (1,200 u/semana)
        if act_sub and cap_todas_lineas > 1200:
            cap_todas_lineas = 1200.0
            
        # Capacidad de células (Anexo 6 y 9)
        cap_celulas_bruta = 0.0
        if celulas_activas > 0:
            cont_medio_cel = (mezcla_est * cont_base_est + mezcla_pro * cont_base_pro) * (1 + params["penalizacion_cel"])
            t_unidad_cel = cont_medio_cel + (5.0 / lote) # cambio 5 min en célula
            f_cel = factor_aprendizaje(sem, sem_cel_activa)
            min_tot_cel = (min_t1 * f_cel) + min_t2 + min_t3 + (min_sab * f_cel)
            # 3 trabajadores por célula
            cap_celulas_bruta = celulas_activas * 3 * (min_tot_cel / t_unidad_cel)
            
        cap_bruta_total = cap_todas_lineas + cap_celulas_bruta
        
        # Calidad y Unidades Buenas (Anexo 7)
        falla_linea = (mezcla_est * 0.04) + (mezcla_pro * 0.06)
        falla_cel = (mezcla_est * 0.03) + (mezcla_pro * 0.05) # -1 punto en células
        
        buenas_lineas = cap_todas_lineas * (1 - falla_linea * 0.20)
        buenas_celulas = cap_celulas_bruta * (1 - falla_cel * 0.20)
        unidades_buenas = buenas_lineas + buenas_celulas
        
        desechadas = (cap_todas_lineas * falla_linea * 0.20) + (cap_celulas_bruta * falla_cel * 0.20)
        
        # Flujo de Inventario, Pedidos Pendientes y Ventas (Anexo 8)
        dem_semana = demanda_serie[sem - 1]
        disponible = inventario + unidades_buenas
        
        # 1. Atender pendientes de hace 2 semanas (prioridad máxima para que no se pierdan)
        atendido_p2 = min(disponible, pendientes_2sem)
        disponible -= atendido_p2
        perdido_por_vencimiento = pendientes_2sem - atendido_p2
        
        # 2. Atender pendientes de hace 1 semana
        atendido_p1 = min(disponible, pendientes_1sem)
        disponible -= atendido_p1
        rem_p1 = pendientes_1sem - atendido_p1 # Pasan a ser pendientes de 2 semanas
        
        # 3. Atender demanda de la semana actual
        atendido_sem = min(disponible, dem_semana)
        disponible -= atendido_sem
        faltante_sem = dem_semana - atendido_sem
        
        # El 50% de la demanda no atendida espera, el 50% se pierde de inmediato
        nuevos_pendientes = faltante_sem * 0.50
        perdido_inmediato = faltante_sem * 0.50
        
        ventas_totales = atendido_p2 + atendido_p1 + atendido_sem
        ventas_perdidas_tot = perdido_por_vencimiento + perdido_inmediato
        
        # Actualizar colas de pendientes e inventario final (tope 1,500 u)
        pendientes_2sem = rem_p1
        pendientes_1sem = nuevos_pendientes
        pendientes_totales = pendientes_1sem + pendientes_2sem
        inventario = min(1500.0, disponible)
        
        nivel_servicio = (atendido_sem / dem_semana) * 100.0 if dem_semana > 0 else 100.0
        
        # ==========================================
        # FINANZAS SEMANALES (Anexos 1, 2, 5, 6, 8, 9, 10)
        # ==========================================
        precio_medio = (mezcla_est * 129.0) + (mezcla_pro * 169.0)
        costo_mat_medio = (mezcla_est * 58.0) + (mezcla_pro * 74.0)
        margen_unit_medio = (mezcla_est * 71.0) + (mezcla_pro * 95.0)
        
        # Ingresos y materiales de unidades vendidas + material perdido en desechos
        margen_bruto_ventas = ventas_totales * margen_unit_medio
        costo_desechos = desechadas * costo_mat_medio
        costo_subcontratacion = (cap_todas_lineas * 4.80) if act_sub else 0.0
        costo_garantia = ventas_totales * 0.008 * 85.0
        
        # Mano de obra por línea
        op_por_linea = (7 if not act_sub else 6) if act_8op else (5 if not act_sub else 4)
        pruebas_por_linea = 1
        salario_linea_hora = (op_por_linea * 6.50) + (pruebas_por_linea * 7.50)
        salario_cel_hora = 3 * 7.20 # 3 trabajadores polivalentes por célula
        
        # Costo Turno 1
        horas_sem = h_pag * 5
        mo_t1 = ((lineas_activas * salario_linea_hora) + (celulas_activas * salario_cel_hora) + (2 * 7.50)) * horas_sem
        if hay_sabado:
            mo_t1 += ((lineas_activas * salario_linea_hora) + (celulas_activas * salario_cel_hora) + (2 * 7.50)) * 7.0 * 1.50
            
        # Costo Turno 2 (+8% prima, Líder $9.00 sustituye a manipulador)
        mo_t2 = 0.0
        if act_t2:
            mo_t2 = ((lineas_activas * salario_linea_hora) + (celulas_activas * salario_cel_hora) + 9.00 + 7.50) * horas_sem * 1.08
            
        # Costo Turno 3 (+15% prima)
        mo_t3 = 0.0
        if act_t3:
            mo_t3 = ((lineas_activas * salario_linea_hora) + (celulas_activas * salario_cel_hora) + 9.00 + 7.50) * horas_sem * 1.15
            
        costo_mo_total = ((mo_t1 + mo_t2 + mo_t3) * 1.30) + 1050.0 # +30% cargas + Supervisor
        
        # Costes fijos planta y espacio (Anexo 5 y 10)
        costo_fijo_planta = 3200.0 + (600.0 if act_t2 else 0.0) + (600.0 if act_t3 else 0.0)
        espacio_usado = (lineas_activas * 120) + (celulas_activas * 40)
        costo_espacio_extra = (200 * 6.0) if (espacio_usado > 420 and sem >= 11) else 0.0
        
        # Costes de inventario, pendientes y penalización de imagen (flujo de caja vs económico)
        costo_mant_inv = inventario * costo_mat_medio * (0.24 / 52.0)
        costo_penalizacion_pend = pendientes_totales * 3.0
        costo_imagen_perdida = ventas_perdidas_tot * 10.0
        
        # Inversiones (se pagan en la semana en que se ordenan)
        inv_semana = 0.0
        if ocho_op and sem == params["sem_orden_8op"]:
            inv_semana += 9000.0 * (3 if tercera_linea else 2)
        if tercera_linea and sem == params["sem_orden_3linea"]:
            inv_semana += 48000.0
        if disp_puerta and sem == params["sem_orden_disp"]:
            inv_semana += 22000.0 * (3 if tercera_linea else 2)
        if n_celulas > 0 and sem == params["sem_orden_cel"]:
            inv_semana += 15000.0 * n_celulas
            
        inversion_acum += inv_semana
        
        # Flujo operativo semanal
        flujo_operativo = (
            margen_bruto_ventas - costo_mo_total - costo_fijo_planta - costo_espacio_extra
            - costo_desechos - costo_subcontratacion - costo_garantia
            - costo_mant_inv - costo_penalizacion_pend - costo_imagen_perdida
        )
        flujo_neto = flujo_operativo - inv_semana
        if sem == 52:
            # Valor residual del 80% de la inversión al final de la semana 52
            flujo_neto += inversion_acum * 0.80
            
        flujo_descontado_acum += flujo_neto / ((1 + tasa_semanal) ** sem)
        
        registros.append({
            "Semana": sem,
            "Fecha": fechas[sem - 1],
            "Demanda": dem_semana,
            "Capacidad_Buena": round(unidades_buenas, 1),
            "Ventas": round(ventas_totales, 1),
            "Pendientes": round(pendientes_totales, 1),
            "Perdidas": round(ventas_perdidas_tot, 1),
            "Inventario": round(inventario, 1),
            "Nivel_Servicio_%": round(nivel_servicio, 1),
            "Costo_MO": round(costo_mo_total, 0),
            "Flujo_Operativo": round(flujo_operativo, 0),
            "VA_Acumulado": round(flujo_descontado_acum, 0)
        })
        
    return pd.DataFrame(registros), inversion_acum, flujo_descontado_acum

# Diccionario de parámetros actuales del usuario
params_usuario = {
    "usar_mezcla_anexo": usar_mezcla_anexo,
    "mezcla_pro_fija": mezcla_pro_fija,
    "op_8_operadores": op_8_operadores,
    "sem_orden_8op": sem_orden_8op,
    "op_tercera_linea": op_tercera_linea,
    "sem_orden_3linea": sem_orden_3linea,
    "op_disp_puerta": op_disp_puerta,
    "sem_orden_disp": sem_orden_disp,
    "op_subcontratar": op_subcontratar,
    "sem_orden_sub": sem_orden_sub,
    "num_turnos": num_turnos,
    "sem_inicio_t2": sem_inicio_t2,
    "sem_inicio_t3": sem_inicio_t3,
    "sabados_mes": sabados_mes,
    "num_celulas": num_celulas,
    "sem_orden_cel": sem_orden_cel,
    "penalizacion_cel": penalizacion_cel,
    "lote_q": lote_q,
    "tiempo_cambio_s": tiempo_cambio_s,
    "incluir_curva": incluir_curva
}

# Ejecutar simulación para la configuración activa
df_sim, inv_total, van_total = simular_52_semanas(params_usuario, escenario_sel)

# ==========================================
# 5. PESTAÑAS DE VISUALIZACIÓN (4 VISTAS)
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs([
    "🏭 1. Panel de Línea y Control",
    "📈 2. Capacidad vs Demanda (52 Sem)",
    "🎯 3. Comparación de Estrategias",
    "🌪️ 4. Sensibilidad y Decisión"
])

# --- VISTA 1: PANEL DE LA LÍNEA ---
with tab1:
    st.subheader("Análisis de Estaciones, Cuello de Botella y Valores de Control")
    est_nombres, t_e, t_p = obtener_tiempos_estaciones(op_8_operadores, op_disp_puerta, op_subcontratar)
    m_pro = 0.30 if usar_mezcla_anexo else mezcla_pro_fija
    m_est = 1.0 - m_pro
    
    t_medio_estacion = [(m_est * te + m_pro * tp) for te, tp in zip(t_e, t_p)]
    ciclo_e, ciclo_p = max(t_e), max(t_p)
    ciclo_m = (m_est * ciclo_e) + (m_pro * ciclo_p)
    utilizacion = [(tm / ciclo_m) * 100 for tm in t_medio_estacion]
    
    df_est = pd.DataFrame({
        "Estación": est_nombres,
        "Estándar (min)": t_e,
        "Pro (min)": t_p,
        "Tiempo Medio (min)": [round(x, 2) for x in t_medio_estacion],
        "Utilización (%)": [round(u, 1) for u in utilizacion]
    })
    
    col1, col2 = st.columns([1.2, 1])
    with col1:
        st.markdown("**Tiempos y Utilización por Estación (Mezcla inicial)**")
        st.dataframe(df_est, use_container_width=True)
        st.bar_chart(df_est.set_index("Estación")["Utilización (%)"])
        
    with col2:
        st.markdown("**Parámetros de la Línea Configurada**")
        t_prod_sem = 2250.0 # 1 turno base
        cap_bruta_l = t_prod_sem / (ciclo_m + (tiempo_cambio_s / lote_q))
        n_lin = 3 if op_tercera_linea else 2
        falla_m = (m_est * 0.04) + (m_pro * 0.06)
        cap_buena_planta = (cap_bruta_l * n_lin) * (1 - falla_m * 0.20)
        
        st.metric("Cuello de Botella Estándar / Pro", f"{ciclo_e:.2f} min / {ciclo_p:.2f} min")
        st.metric("Ciclo Medio Ponderado", f"{ciclo_m:.2f} min")
        st.metric("Capacidad Bruta (1 Turno, Líneas)", f"{cap_bruta_l:.1f} u/línea ({cap_bruta_l*n_lin:.1f} total)")
        st.metric("Unidades Buenas (1 Turno, Líneas)", f"{cap_buena_planta:.1f} u/sem")
        st.info("💡 **Nota crítica sobre Ingeniería (O1):** El informe de Cabrera promedia los tiempos de estación (5.0 min), pero una línea en serie está limitada por su estación más lenta (L8 = 5.67 min en Estándar y L6 = 6.40 min en Pro). No duplica la capacidad.")

# --- VISTA 2: CAPACIDAD VS DEMANDA SEMANA A SEMANA ---
with tab2:
    st.subheader(f"Simulación Semanal - Escenario: {escenario_sel}")
    
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Valor Actual (VAN 52 sem)", f"US$ {van_total:,.0f}")
    k2.metric("Inversión Requerida", f"US$ {inv_total:,.0f}", delta="Dentro de límite ($120k)" if inv_total <= 120000 else "Requiere Consejo (> $120k)", delta_color="normal" if inv_total <= 120000 else "inverse")
    k3.metric("Total Unidades Vendidas", f"{df_sim['Ventas'].sum():,.0f} u")
    k4.metric("Total Ventas Perdidas", f"{df_sim['Perdidas'].sum():,.0f} u")
    k5.metric("Nivel de Servicio Medio", f"{df_sim['Nivel_Servicio_%'].mean():.1f}%")
    
    st.markdown("#### Capacidad de Unidades Buenas vs. Demanda Semanal")
    st.line_chart(df_sim.set_index("Semana")[["Demanda", "Capacidad_Buena", "Ventas"]])
    
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown("#### Evolución de Inventario y Pedidos Pendientes")
        st.area_chart(df_sim.set_index("Semana")[["Inventario", "Pendientes"]])
    with col_g2:
        st.markdown("#### Ventas Perdidas por Semana")
        st.bar_chart(df_sim.set_index("Semana")["Perdidas"])
        
    with st.expander("Ver tabla detallada de las 52 semanas"):
        st.dataframe(df_sim, use_container_width=True)

# --- VISTA 3: COMPARACIÓN DE ESTRATEGIAS ---
with tab3:
    st.subheader("Evaluación Multi-Escenario de Estrategias")
    st.markdown("Comparación de 5 estrategias (incluyendo tu configuración actual de la barra lateral) bajo los tres escenarios de demanda.")
    
    estrategias_predef = {
        "0. Planta Actual (Base)": {
            "usar_mezcla_anexo": True, "mezcla_pro_fija": 0.30, "op_8_operadores": False, "sem_orden_8op": 99,
            "op_tercera_linea": False, "sem_orden_3linea": 99, "op_disp_puerta": False, "sem_orden_disp": 99,
            "op_subcontratar": False, "sem_orden_sub": 99, "num_turnos": 1, "sem_inicio_t2": 99, "sem_inicio_t3": 99,
            "sabados_mes": 0, "num_celulas": 0, "sem_orden_cel": 99, "penalizacion_cel": 0.08,
            "lote_q": 100, "tiempo_cambio_s": 20, "incluir_curva": True
        },
        "1. Intensiva Flexible (8 Op + 2º Turno + Sábados)": {
            "usar_mezcla_anexo": True, "mezcla_pro_fija": 0.30, "op_8_operadores": True, "sem_orden_8op": 1,
            "op_tercera_linea": False, "sem_orden_3linea": 99, "op_disp_puerta": False, "sem_orden_disp": 99,
            "op_subcontratar": False, "sem_orden_sub": 99, "num_turnos": 2, "sem_inicio_t2": 3, "sem_inicio_t3": 99,
            "sabados_mes": 3, "num_celulas": 0, "sem_orden_cel": 99, "penalizacion_cel": 0.08,
            "lote_q": 200, "tiempo_cambio_s": 20, "incluir_curva": True
        },
        "2. Expansión Híbrida (8 Op + 2º Turno + 2 Células)": {
            "usar_mezcla_anexo": True, "mezcla_pro_fija": 0.30, "op_8_operadores": True, "sem_orden_8op": 1,
            "op_tercera_linea": False, "sem_orden_3linea": 99, "op_disp_puerta": False, "sem_orden_disp": 99,
            "op_subcontratar": False, "sem_orden_sub": 99, "num_turnos": 2, "sem_inicio_t2": 3, "sem_inicio_t3": 99,
            "sabados_mes": 2, "num_celulas": 2, "sem_orden_cel": 1, "penalizacion_cel": 0.08,
            "lote_q": 200, "tiempo_cambio_s": 20, "incluir_curva": True
        },
        "3. Alta Inversión Fija (3ra Línea + 8 Op + 2º Turno)": {
            "usar_mezcla_anexo": True, "mezcla_pro_fija": 0.30, "op_8_operadores": True, "sem_orden_8op": 1,
            "op_tercera_linea": True, "sem_orden_3linea": 1, "op_disp_puerta": False, "sem_orden_disp": 99,
            "op_subcontratar": False, "sem_orden_sub": 99, "num_turnos": 2, "sem_inicio_t2": 3, "sem_inicio_t3": 99,
            "sabados_mes": 0, "num_celulas": 0, "sem_orden_cel": 99, "penalizacion_cel": 0.08,
            "lote_q": 200, "tiempo_cambio_s": 20, "incluir_curva": True
        },
        "⭐ Tu Configuración Actual (Sidebar)": params_usuario
    }
    
    res_comp = []
    for nombre_est, p_est in estrategias_predef.items():
        _, inv_e, van_base = simular_52_semanas(p_est, "Base")
        _, _, van_opt = simular_52_semanas(p_est, "Optimista")
        df_can, _, van_can = simular_52_semanas(p_est, "Canal")
        
        ve = (prob_base * van_base) + (prob_opt * van_opt) + (prob_can * van_can)
        peor_caso = min(van_base, van_opt, van_can)
        
        res_comp.append({
            "Estrategia": nombre_est,
            "Inversión (US$)": inv_e,
            "VAN Base (US$)": round(van_base, 0),
            "VAN Optimista (US$)": round(van_opt, 0),
            "VAN Canal (US$)": round(van_can, 0),
            "Valor Esperado (US$)": round(ve, 0),
            "Peor Caso (US$)": round(peor_caso, 0)
        })
        
    df_comp = pd.DataFrame(res_comp)
    st.dataframe(df_comp, use_container_width=True)
    
    st.markdown("#### Comparación de Valor Esperado vs. Peor Caso por Estrategia")
    st.bar_chart(df_comp.set_index("Estrategia")[["Valor Esperado (US$)", "Peor Caso (US$)"]])

# --- VISTA 4: SENSIBILIDAD Y PUNTOS DE DECISIÓN ---
with tab4:
    st.subheader("Análisis de Sensibilidad y Hoja de Ruta Secuencial")
    
    # Calcular VE base de la configuración actual
    _, _, vb0 = simular_52_semanas(params_usuario, "Base")
    _, _, vo0 = simular_52_semanas(params_usuario, "Optimista")
    _, _, vc0 = simular_52_semanas(params_usuario, "Canal")
    ve_base_actual = (prob_base * vb0) + (prob_opt * vo0) + (prob_can * vc0)
    
    # Sensibilidad variando parámetros clave
    factores = [
        ("Mezcla Pro (20% vs 45%)", "mezcla_pro_fija", 0.20, 0.45),
        ("Tamaño de Lote Q (50 vs 300)", "lote_q", 50, 300),
        ("Penalización Células (0% vs 20%)", "penalizacion_cel", 0.00, 0.20),
        ("Tiempo de Cambio (10 vs 35 min)", "tiempo_cambio_s", 10, 35)
    ]
    
    datos_sens = []
    for etiqueta, clave, val_bajo, val_alto in factores:
        p_bajo = params_usuario.copy()
        p_alto = params_usuario.copy()
        if clave == "mezcla_pro_fija":
            p_bajo["usar_mezcla_anexo"] = False
            p_alto["usar_mezcla_anexo"] = False
        p_bajo[clave] = val_bajo
        p_alto[clave] = val_alto
        
        _, _, vb_b = simular_52_semanas(p_bajo, "Base")
        _, _, vo_b = simular_52_semanas(p_bajo, "Optimista")
        _, _, vc_b = simular_52_semanas(p_bajo, "Canal")
        ve_bajo = (prob_base * vb_b) + (prob_opt * vo_b) + (prob_can * vc_b)
        
        _, _, vb_a = simular_52_semanas(p_alto, "Base")
        _, _, vo_a = simular_52_semanas(p_alto, "Optimista")
        _, _, vc_a = simular_52_semanas(p_alto, "Canal")
        ve_alto = (prob_base * vb_a) + (prob_opt * vo_a) + (prob_can * vc_a)
        
        impacto = abs(ve_alto - ve_bajo)
        datos_sens.append({
            "Variable": etiqueta,
            "VE con Valor Bajo (US$)": round(ve_bajo, 0),
            "VE con Valor Alto (US$)": round(ve_alto, 0),
            "Amplitud de Impacto (US$)": round(impacto, 0)
        })
        
    df_sens = pd.DataFrame(datos_sens).sort_values(by="Amplitud de Impacto (US$)", ascending=False)
    
    col_s1, col_s2 = st.columns([1.2, 1])
    with col_s1:
        st.markdown("**Impacto en el Valor Esperado (Gráfico de Tornado / Amplitud)**")
        st.dataframe(df_sens, use_container_width=True)
        st.bar_chart(df_sens.set_index("Variable")["Amplitud de Impacto (US$)"])
    with col_s2:
        st.markdown("**Árbol de Decisión Secuencial Recomendado para el Consejo**")
        st.success("""
        **Fase 1 (Semana 1 - Viernes 2 de Octubre):**
        * Aprobar **Reequilibrio a 8 operadores** en las 2 líneas actuales (US$ 18,000, listo en Sem 4).
        * Iniciar contratación de **2º Turno** (US$ 0 CAPEX, listo en Sem 3) y activar **Sábados extra** + aumento de lote a **Q = 200**.
        * Ordenar **2 Células de trabajo** (US$ 30,000, listas en Sem 6 para el pico de Black Friday).
        * *Inversión total Fase 1: US$ 48,000 (muy por debajo del límite de US$ 120,000).*
        
        **Fase 2 (Punto de Decisión en Semana 5 - inicios de Noviembre):**
        * Ya se observa si los pedidos reales siguen la curva *Base/Canal* (1,150 u) o la *Optimista* (1,380 u).
        
        **Fase 3 (Punto de Decisión en Semana 13-14 - Enero):**
        * Si ocurre **Llenado de Canal** (demanda cae a 650 u/sem): se desactiva el 2º turno en líneas o se reasignan operarios, evitando quedar con una 3ra línea rígida ociosa.
        * Si se confirma tendencia **Base u Optimista**: se mantienen los 2 turnos y se evalúa ampliar 2 células adicionales para el pico del Día de las Madres (Sem 33).
        """)