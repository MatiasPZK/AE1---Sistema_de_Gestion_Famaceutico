#LIBRERIASS
import customtkinter as ctk
from tkinter import ttk, messagebox
from datos import cargar_inventario, guardar_inventario
from logica import actualizar_stock, registrar_venta, iniciar_tabla_ventas


class Manager(ctk.CTk):

    #CLASE PARA AÑADIR AL STOCK, TOMA LOS VALORES QUE DIO EL USUARIO EN EL MARCO DE AÑADIR STOCK
    def reponer_stock(self):
        str_id = self.txt_id.get().strip()
        str_cant = self.txt_cant.get().strip()

        if not str_id or not str_cant:
            messagebox.showwarning("Atención", "Por favor complete los campos.")
            return
        try:
            id_med = int(str_id)
            cantidad = int(str_cant)
        except ValueError:
            messagebox.showerror("Error", "El ID y la CANTIDAD deben de ser números enteros.")
            return
        exito, mensaje = actualizar_stock(self.df_inventario, id_med, cantidad)
        if exito:
            guardar_inventario(self.df_inventario)
            self.mostrar_datos_inventario()
            self.txt_id.delete(0, "end")
            self.txt_cant.delete(0, "end")
            messagebox.showinfo("Éxito", mensaje)
        else:
            messagebox.showerror("Error", mensaje)

    #FUNCION PARA LIMPIAR LA TABLA ANTES DE ACTUALIZAR CON LOS DATOS NUEVOS
    def mostrar_datos_inventario(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        for _, fila in self.df_inventario.iterrows():
            valores = (
                fila["id_med"],
                fila["nombre"],
                fila["sucursal"],
                int(fila["stock"]),
                f"${float(fila['precio']):,.2f}"
            )
            self.tabla.insert("", "end", values=valores)

    #COMO DICE EL NOMBRE, FUNCION PARA EJECUTAR LA VENTA. GUARDA TODO LO QUE PUSO EL USUARIO EN UNAS VARIABLES.
    def ejecutar_venta(self):
        str_vendedor = self.txt_vendedor.get().strip()
        str_id = self.txt_v_id.get().strip()
        str_cant = self.txt_v_cant.get().strip()

        if not str_vendedor or not str_id or not str_cant:
            messagebox.showwarning("Atencion", "Por favor complete los campos.")
            return
        try:
            id_med = int(str_id)
            cantidad = int(str_cant)                
        except ValueError:
            messagebox.showerror("Error", "El ID y la cantidad deben ser numéricos.")
            return
        
        exito, mensaje = registrar_venta(
            self.df_inventario,
            self.df_ventas,
            id_med,
            cantidad,
            str_vendedor
        )

        if exito:
            guardar_inventario(self.df_inventario)
            self.txt_v_id.delete(0, "end")
            self.txt_v_cant.delete(0, "end")
            messagebox.showinfo("Venta Exitosa", mensaje)
        else:
            messagebox.showerror("Error en Venta", mensaje)


    #FUNCION PARA CAMBIAR DE PESTAÑAS. OCULTA LOS FRAMES INDICADOS PARA DAR LA SENSACION DE "CAMBIO DE PESTAÑA", PERO EN VERDAD
    #TODO SIGUE AHI PERO SOLO ESTA OCULTO JEJE
    def optionmenu_callback(self, choice):
        if choice == "Inventario":
            self.frame_ventas.pack_forget()
            self.frame_exportar.pack_forget()
            self.frame_inventario.pack(fill="both", expand=True)
            self.mostrar_datos_inventario()
        elif choice == "Vender":
            self.frame_inventario.pack_forget()
            self.frame_exportar.pack_forget()
            self.frame_ventas.pack(fill="both", expand=True)
        elif choice == "Exportar":
            self.frame_inventario.pack_forget()
            self.frame_ventas.pack_forget()
            self.frame_exportar.pack(fill="both", expand=True)
            self.mostrar_datos_ventas()

    #FUNCION
    def mostrar_datos_ventas(self):
        #BORRAR DATOS DE LA TABLA ANTERIOR
        for item in self.tabla_ventas.get_children():
            self.tabla_ventas.delete(item)
        if self.df_ventas.empty:
            self.lbl_total_ingresos.configure(text="TOTAL INGRESOS: 0.00$")
            self.lbl_total_comisiones.configure(text="TOTAL DE COMISIONES (10%): 0.00$")
            self.lbl_total_unidades.configure(text="TOTAL DE UNIDADES VENDIDAS: 0")
            return

        total_ingresos = 0.0
        total_comisiones = 0.0
        total_unidades = 0

        #cargar las filas y acomular los totales
        for _, fila in self.df_ventas.iterrows():
            #carga los datos a 3 variables
            subtotal=float(fila["total"])
            comision=float(fila.get("comision", subtotal*0.10))
            cant=int(fila["cantidad"])
            #operaciones con las 3 variables anteriores
            total_ingresos += subtotal
            total_comisiones += comision
            total_unidades += cant

            valores=(
                fila.get("id_venta","-"),
                fila.get("vendedor", "-"),
                fila.get("id_med", "-"),
                fila.get("nombre", "-"),
                cant,
                f"${float(fila['precio_unitario']):,.2f}",
                f"${subtotal:,.2f}",
                f"${comision:,.2f}"
            )
            self.tabla_ventas.insert("", "end", values=valores)
        #cambia los valores de la etiquetas
        self.lbl_total_ingresos.configure(text=f"Total Recaudado: ${total_ingresos:,.2f}")
        self.lbl_total_comisiones.configure(text=f"Comisiones: ${total_comisiones:,.2f}")
        self.lbl_total_unidades.configure(text=f"Unidades Vendidas: {total_unidades}")

    def exportar_excel(self):
        if self.df_ventas.empty:
            messagebox.showwarning("Atencion!", "No hay ventas registradas como para exportar")
            return
        try:
            nombre_archivo="reporte_ventas.xlsx"
            self.df_ventas.to_excel(nombre_archivo, index=False)
            messagebox.showinfo("Exito", f"reporte exportado exitosamente como '{nombre_archivo}'.")
        except Exception as e:
            try:
                self.df_ventas.to_csv("reporte_ventas.csv", index=False)
                messagebox.showinfo("Exito", "Reporte exportado exitosamente como reporte_ventas.csv")
            except Exception as err:
                messagebox.showerror("Error", f"No se pudo guardar el reporte: {err}")
        

    #ACA ARRANCA TODO
    def __init__(self):
        super().__init__()
        self.df_ventas = iniciar_tabla_ventas()

        #PERSONALIZACION DE LA VENTANA
        self.title("App Farmaura V0.1")
        self.resizable(False, False)
        self.geometry("1280x1024")
        self.configure(fg_color="#E5FBFF")
        self.df_inventario = cargar_inventario()

        #MARCOS / FRAMES. PARA ORGANIZAR LA PAGINA
        self.container = ctk.CTkFrame(self, fg_color="#E5FBFF")
        self.container.pack(fill="both", expand=True, padx=20, pady=20)

        self.frame_nav = ctk.CTkFrame(self.container, fg_color="#D5F3F8")
        self.frame_nav.pack(fill="x", pady=(0, 10))

        self.frame_inventario = ctk.CTkFrame(self.container, fg_color="transparent")
        self.frame_inventario.pack(fill="both", expand=True)

        self.frame_acciones = ctk.CTkFrame(self.frame_inventario, fg_color="#B3B3B3")
        self.frame_acciones.pack(fill="x", pady=10)

        self.frame_ventas = ctk.CTkFrame(self.container, fg_color="#E5FBFF")

        self.frame_exportar = ctk.CTkFrame(self.container, fg_color="#2A3840")


        #PARTE DE LA BARRA DE NAVEGACION, SOLO PONE EL TEXTO "OPCION" EN EL FRAME "FRAME_NAV"
        lbl_menu = ctk.CTkLabel(self.frame_nav, text="Opción:", text_color="#202327", font=ctk.CTkFont(weight="bold"))
        lbl_menu.pack(side="left", padx=(15, 5), pady=10)

        #ESTO ES PARTE DEL FRAME "frame_acciones" QUE ES EL APARTADO PARA ACTUALIZAR EL STOCK. PONE LA CAJA DE TEXTO.
        lbl_id = ctk.CTkLabel(self.frame_acciones, text="ID Med: ", text_color="#202327")
        lbl_id.pack(side="left", padx=(20, 2), pady=10)
        self.txt_id = ctk.CTkEntry(self.frame_acciones, placeholder_text="Ej: 1", width=100)
        self.txt_id.pack(side="left", padx=(0, 10), pady=10)
        lbl_cant = ctk.CTkLabel(self.frame_acciones, text="Cantidad:", text_color="#202327")
        lbl_cant.pack(side="left", padx=(20, 2), pady=10)
        self.txt_cant = ctk.CTkEntry(self.frame_acciones, placeholder_text="Cantidad", width=100)
        self.txt_cant.pack(side="left", padx=(0, 10), pady=10)
        #BOTON. BOTON, DEL APARTADO PARA ACTUALIZAR EL STOCK
        btn_reponer = ctk.CTkButton(
            self.frame_acciones,
            text="Actualizar",
            command=self.reponer_stock
        )
        btn_reponer.pack(side="left", padx=10, pady=20)

        #PARTE IMPORTANTE! ACA EMPIEZA EL APARTADO DE LA MATRIZ DEL STOCK DISPONIBLE
        columnas = ("id_med", "nombre", "sucursal", "stock", "precio")
        self.tabla = ttk.Treeview(self.frame_inventario, column=columnas, show='headings')

        self.tabla.heading("id_med", text="ID")
        self.tabla.heading("nombre", text="Medicamento")
        self.tabla.heading("sucursal", text="Sucursal")
        self.tabla.heading("stock", text="Unidades")
        self.tabla.heading("precio", text="Precio ($)")

        self.tabla.column("id_med", width=60, anchor="center")
        self.tabla.column("nombre", width=250, anchor="w")
        self.tabla.column("sucursal", width=120, anchor="center")
        self.tabla.column("stock", width=80, anchor="center")
        self.tabla.column("precio", width=100, anchor="e")

        self.tabla.pack(fill="both", expand=True)
        self.mostrar_datos_inventario()

        #MENU DE OPCIONES
        self.optionmenu_var = ctk.StringVar(value="Inventario")
        self.optionmenu = ctk.CTkOptionMenu(
            self.frame_nav,
            values=["Inventario", "Vender", "Exportar"],
            command=self.optionmenu_callback,
            variable=self.optionmenu_var
        )
        self.optionmenu.pack(side="right", padx=10, pady=20)

        
        #VENTANA DE VENTAS. ESTO PONE EL TITULO DE LA VENTANA
        lbl_v_titulo = ctk.CTkLabel(
            self.frame_ventas,
            text="NUEVO REGISTRO DE VENTA",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#030F12"
        )
        lbl_v_titulo.pack(anchor="w", pady=(10, 15), padx=20)

        form_v = ctk.CTkFrame(self.frame_ventas, fg_color="#414242")
        form_v.pack(fill="x", padx=20, pady=10)

        #--FORMULARIO DE LA VENTA--
        # Vendedor
        lbl_vendedor = ctk.CTkLabel(form_v, text="Vendedor", text_color="#C0F6FF")
        lbl_vendedor.grid(row=0, column=0, padx=15, pady=10, sticky="w")
        self.txt_vendedor = ctk.CTkEntry(form_v, placeholder_text="EJ: Caio", width=180)
        self.txt_vendedor.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Medicamento
        lbl_v_id = ctk.CTkLabel(form_v, text="Medicamento", text_color="#C0F6FF")
        lbl_v_id.grid(row=1, column=0, padx=15, pady=10, sticky="w")
        self.txt_v_id = ctk.CTkEntry(form_v, placeholder_text="EJ: 1", width=180)
        self.txt_v_id.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # Cantidad
        lbl_v_cantidad = ctk.CTkLabel(form_v, text="Cantidad", text_color="#C0F6FF")
        lbl_v_cantidad.grid(row=2, column=0, padx=15, pady=10, sticky="w")
        self.txt_v_cant = ctk.CTkEntry(form_v, placeholder_text="EJ: 2", width=180)
        self.txt_v_cant.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        btn_venta = ctk.CTkButton(
            form_v,
            text="CONFIRMAR",
            command=self.ejecutar_venta
        )
        btn_venta.grid(row=3, column=0, columnspan=2, padx=15, pady=15, sticky="ew")


        #--PARTE DE EXPORTACION-- (IMPORTANTE)
        lbl_e_titulo = ctk.CTkLabel(
                    self.frame_exportar,
                    text="EXPORTAR VENTAS A EXCEL",
                    font=ctk.CTkFont(size=18, weight="bold"),
                    text_color="#030F12"
                )
        lbl_e_titulo.pack(anchor="w", pady=(10, 15), padx=20)

        self.frame_metricas = ctk.CTkFrame(self.frame_exportar, fg_color="#D5F3F8")
        self.frame_metricas.pack(fill="x",padx=20,pady=(0,10))
        #texto de total de ingresos adentro del frame de las metricas
        self.lbl_total_ingresos = ctk.CTkLabel(self.frame_metricas, text="TOTAL INGRESOS: 0.00$", text_color="#1F2937", font=ctk.CTkFont(weight="bold"))
        self.lbl_total_ingresos.pack(side="left", padx=20,pady=20)
        #texo del total de las comisiones dentro del frame de las metricas
        self.lbl_total_comisiones = ctk.CTkLabel(self.frame_metricas,text="TOTAL DE COMISIONES (10%): 0.00$", text_color="#1F2937", font=ctk.CTkFont(weight="bold"))
        self.lbl_total_comisiones.pack(side="left", padx=20,pady=20)
        #texto del total de unidades vendidas
        self.lbl_total_unidades = ctk.CTkLabel(self.frame_metricas, text="TOTAL DE UNIDADES VENDIDAS: 0", text_color="#1F2937", font=ctk.CTkFont(weight="bold"))
        self.lbl_total_unidades.pack(side="left",padx=20,pady=20)

        #tabla/matriz del historial de ventas
        cols_ventas=("id_venta","vendedor","id_med","medicamento","cantidad","precio_unitario","subtotal","comision")
        self.tabla_ventas=ttk.Treeview(self.frame_exportar,columns=cols_ventas,show='headings')

        self.tabla_ventas.heading("id_venta", text="ID VENTA")
        self.tabla_ventas.heading("vendedor", text="VENDEDOR")
        self.tabla_ventas.heading("id_med", text="ID MEDICAMENTO")
        self.tabla_ventas.heading("medicamento", text="MEDICAMENTO")
        self.tabla_ventas.heading("cantidad", text="CANTIDAD")
        self.tabla_ventas.heading("precio_unitario", text="PRECIO UNITARIO")
        self.tabla_ventas.heading("subtotal", text="SUBTOTAL")
        self.tabla_ventas.heading("comision", text="COMISION")

        self.tabla_ventas.column("id_venta", width=70, anchor="center")
        self.tabla_ventas.column("vendedor", width=120, anchor="w")
        self.tabla_ventas.column("id_med", width=70, anchor="center")
        self.tabla_ventas.column("medicamento", width=180, anchor="w")
        self.tabla_ventas.column("cantidad", width=70, anchor="e")
        self.tabla_ventas.column("precio_unitario", width=90, anchor="e")
        self.tabla_ventas.column("subtotal", width=100, anchor="e")
        self.tabla_ventas.column("comision", width=90, anchor="e")
        self.tabla_ventas.pack(fill="both",expand=True,padx=20,pady=5)
        #boton exportar
        btn_exportar = ctk.CTkButton(
                    self.frame_exportar,
                    text="EXPORTAR EN EXCEL",
                    command=self.exportar_excel,
                    fg_color="#1E7145",
                    hover_color="#145231"
                )
        btn_exportar.pack(pady=15)

if __name__ == "__main__":
    app = Manager()
    app.mainloop()