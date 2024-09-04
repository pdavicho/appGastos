import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
from datetime import datetime


# Configuración de la página
st.set_page_config(page_title="Gestor de Finanzas Personales", page_icon="💰", layout="wide")

# Funciones para manejar la base de datos
def crear_tablas():
    conn = sqlite3.connect('finanzas.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS transacciones
                 (id INTEGER PRIMARY KEY, tipo TEXT, categoria TEXT, 
                  monto REAL, fecha DATE, detalle TEXT)''')
    conn.commit()
    conn.close()

def agregar_transaccion(tipo, categoria, monto, fecha, detalle):
    conn = sqlite3.connect('finanzas.db')
    c = conn.cursor()
    c.execute("INSERT INTO transacciones (tipo, categoria, monto, fecha, detalle) VALUES (?, ?, ?, ?, ?)",
              (tipo, categoria, monto, fecha, detalle))
    conn.commit()
    conn.close()

def obtener_transacciones(tipo, mes, año):
    conn = sqlite3.connect('finanzas.db')
    query = f"SELECT * FROM transacciones WHERE tipo = ? AND strftime('%m', fecha) = ? AND strftime('%Y', fecha) = ?"
    df = pd.read_sql_query(query, conn, params=(tipo, f"{mes:02d}", str(año)))
    conn.close()
    return df

# Categorías predefinidas
CATEGORIAS_GASTOS = ['Comida', 'Gasolina', 'Salud', 'Casa', 'Restaurante', 'Deportes','Tarjeta', 'Otros']
#CATEGORIAS_GASTOS = st_tags(label='Escoger las palabras que desea analizar :',
#                           text='Presionar enter o anadir mas',
#                           value=['Comida', 'Gasolina', 'Salud', 'Casa', 'Restaurante', 'Deportes'],
#                           maxtags=8,
#                           key="opciones_gastos")
CATEGORIAS_INGRESOS = ['Sueldo', 'Bonificación', 'Inversiones', 'Otros']
#CATEGORIAS_INGRESOS = st_tags(label='Escoger las palabras que desea analizar :',
#                           text='Presionar enter o anadir mas',
#                           value=['Sueldo', 'Bonificación', 'Inversiones'],
#                           maxtags=8,
#                           key="opciones_ingresos")

# Inicialización de la base de datos
crear_tablas()

# Título de la aplicación
st.title("💰 Gestor de Finanzas Personales")

# Sidebar para navegación
pagina = st.sidebar.selectbox("Selecciona una página", ["Añadir Transacción", "Ver Reporte", "Gráficos"])

if pagina == "Añadir Transacción":
    st.header("Añadir Nueva Transacción")
    
    tipo = st.selectbox("Tipo de Transacción", ["Gasto", "Ingreso"])
    
    if tipo == "Gasto":
        categoria = st.selectbox("Categoría", CATEGORIAS_GASTOS)
    else:
        categoria = st.selectbox("Categoría", CATEGORIAS_INGRESOS)
    
    monto = st.number_input("Monto", min_value=0.01, step=0.01)
    fecha = st.date_input("Fecha")
    detalle = st.text_input("Detalle (opcional)")
    
    if st.button("Añadir Transacción"):
        agregar_transaccion(tipo.lower(), categoria, monto, fecha, detalle)
        st.success(f"{tipo} de {monto:.2f} en {categoria} añadido correctamente.")

elif pagina == "Ver Reporte":
    st.header("Reporte Mensual")
    
    col1, col2 = st.columns(2)
    with col1:
        mes = st.selectbox("Mes", range(1, 13), format_func=lambda x: datetime(2023, x, 1).strftime('%B'))
    with col2:
        año = st.selectbox("Año", range(2024, 2031))
    
    gastos = obtener_transacciones('gasto', mes, año)
    ingresos = obtener_transacciones('ingreso', mes, año)
    
    total_gastos = gastos['monto'].sum()
    total_ingresos = ingresos['monto'].sum()
    
    st.subheader(f"Resumen para {datetime(año, mes, 1).strftime('%B %Y')}")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Ingresos", f"${total_ingresos:.2f}")
    col2.metric("Total Gastos", f"${total_gastos:.2f}")
    col3.metric("Balance", f"${total_ingresos - total_gastos:.2f}")
    
    st.subheader("Desglose de Gastos")
    st.dataframe(gastos)
    
    st.subheader("Desglose de Ingresos")
    st.dataframe(ingresos)

elif pagina == "Gráficos":
    st.header("Visualización de Datos")
    
    mes = st.selectbox("Mes", range(1, 13), format_func=lambda x: datetime(2023, x, 1).strftime('%B'))
    año = st.selectbox("Año", range(2024, 2031))
    
    gastos = obtener_transacciones('gasto', mes, año)
    
    if not gastos.empty:
        fig, ax = plt.subplots(figsize=(10, 6))
        gastos_por_categoria = gastos.groupby('categoria')['monto'].sum()
        ax.pie(gastos_por_categoria.values, labels=gastos_por_categoria.index, autopct='%1.1f%%')
        ax.set_title(f"Distribución de Gastos - {datetime(año, mes, 1).strftime('%B %Y')}")
        st.pyplot(fig)
    else:
        st.info("No hay datos de gastos para el período seleccionado.")
    
    # Gráfico de barras para comparar ingresos y gastos
    ingresos = obtener_transacciones('ingreso', mes, año)
    
    if not ingresos.empty or not gastos.empty:
        total_ingresos = ingresos['monto'].sum()
        total_gastos = gastos['monto'].sum()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(['Ingresos', 'Gastos'], [total_ingresos, total_gastos])
        ax.set_title(f"Comparación de Ingresos y Gastos - {datetime(año, mes, 1).strftime('%B %Y')}")
        ax.set_ylabel('Monto ($)')
        for i, v in enumerate([total_ingresos, total_gastos]):
            ax.text(i, v, f'${v:.2f}', ha='center', va='bottom')
        st.pyplot(fig)
    else:
        st.info("No hay datos suficientes para generar el gráfico comparativo.")