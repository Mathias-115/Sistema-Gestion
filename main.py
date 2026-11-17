main.py
# -*- coding: utf-8 -*-
"""
Sistema Integral de Gestión de Clientes, Servicios y Reservas
Curso: Programación 213023 — UNAD
Empresa: Software FJ
"""

from abc import ABC, abstractmethod
from datetime import datetime
import os

# ---------------------- CONFIGURACIÓN DE LOGS ----------------------
ARCHIVO_LOG = "sistema_logs.txt"

def registrar_log(mensaje: str, tipo: str = "INFO") -> None:
    """Registra eventos y errores en archivo con marca de tiempo"""
    marca = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"[{marca}] [{tipo}] {mensaje}\n"
    try:
        with open(ARCHIVO_LOG, "a", encoding="utf-8") as f:
            f.write(linea)
    except Exception as e:
        print(f"⚠️ No se pudo escribir en el log: {e}")

# ---------------------- EXCEPCIONES PERSONALIZADAS ----------------------
class ErrorSistema(Exception):
    """Excepción base personalizada del sistema"""
    pass

class DatoInvalidoError(ErrorSistema):
    """Datos con formato o valor incorrecto"""
    pass

class ServicioNoDisponibleError(ErrorSistema):
    """Servicio no disponible para reserva"""
    pass

class ReservaInvalidaError(ErrorSistema):
    """Operación de reserva no permitida"""
    pass

class ClienteSinDatosError(ErrorSistema):
    """Faltan datos obligatorios del cliente"""
    pass

# ---------------------- CLASE ABSTRACTA BASE ----------------------
class EntidadBase(ABC):
    """Clase abstracta que representa cualquier entidad del sistema"""
    contador_global = 0

    def __init__(self):
        EntidadBase.contador_global += 1
        self._id = EntidadBase.contador_global

    @property
    def id(self) -> int:
        return self._id

    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def validar_datos(self) -> bool:
        pass

# ---------------------- CLASE CLIENTE ----------------------
class Cliente(EntidadBase):
    """Clase que representa un cliente con encapsulación y validaciones"""
    def __init__(self, nombre: str, correo: str, telefono: str):
        super().__init__()
        self.__nombre = nombre
        self.__correo = correo
        self.__telefono = telefono
        self.validar_datos()

    # Getters (encapsulación)
    @property
    def nombre(self) -> str:
        return self.__nombre

    @property
    def correo(self) -> str:
        return self.__correo

    @property
    def telefono(self) -> str:
        return self.__telefono

    def validar_datos(self) -> bool:
        """Valida que los datos del cliente sean correctos"""
        try:
            if not self.__nombre or len(self.__nombre.strip()) < 2:
                raise DatoInvalidoError(f"Nombre '{self.__nombre}' es muy corto o vacío")
            if "@" not in self.__correo or "." not in self.__correo:
                raise DatoInvalidoError(f"Correo '{self.__correo}' tiene formato inválido")
            if len(self.__telefono) < 7:
                raise DatoInvalidoError(f"Teléfono '{self.__telefono}' es demasiado corto")
            return True
        except Exception as e:
            registrar_log(f"Error validando cliente: {e}", "ERROR")
            raise  # Encadenamiento de excepción

    def __str__(self) -> str:
        return f"Cliente #{self._id}: {self.__nombre} | {self.__correo} | {self.__telefono}"

# ---------------------- CLASE ABSTRACTA SERVICIO ----------------------
class Servicio(EntidadBase):
    """Clase abstracta base para todos los servicios"""
    def __init__(self, nombre: str, precio_base: float):
        super().__init__()
        self._nombre = nombre
        self._precio_base = precio_base
        self._disponible = True

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def disponible(self) -> bool:
        return self._disponible

    def marcar_disponible(self, estado: bool) -> None:
        self._disponible = estado

    @abstractmethod
    def calcular_costo(self, duracion: float, impuesto: float = 0.0, descuento: float = 0.0) -> float:
        """Calcula costo — SOBRECARGA: con o sin impuesto/descuento"""
        pass

    @abstractmethod
    def descripcion(self) -> str:
        pass

    def validar_datos(self) -> bool:
        if self._precio_base < 0:
            raise DatoInvalidoError("El precio base no puede ser negativo")
        return True

    def __str__(self) -> str:
        return f"{self.descripcion()} | Base: ${self._precio_base:.2f}"

# ---------------------- SERVICIOS CONCRETOS (HERENCIA/POLIMORFISMO) ----------------------
class ServicioSala(Servicio):
    """Reserva de salas de reunión"""
    def __init__(self, precio_base: float, capacidad: int):
        super().__init__("Reserva de Sala", precio_base)
        self._capacidad = capacidad

    def calcular_costo(self, duracion: float, impuesto: float = 0.0, descuento: float = 0.0) -> float:
        """Cálculo con impuesto y descuento — sobrecarga simulada por parámetros opcionales"""
        if duracion <= 0:
            raise DatoInvalidoError("La duración debe ser mayor a cero")
        costo = self._precio_base * duracion
        costo += costo * impuesto
        costo -= costo * descuento
        return round(costo, 2)

    def descripcion(self) -> str:
        return f"Servicio: {self._nombre} — Capacidad: {self._capacidad} personas"

class AlquilerEquipos(Servicio):
    """Alquiler de equipos tecnológicos"""
    def __init__(self, precio_base: float, tipo_equipo: str):
        super().__init__("Alquiler de Equipos", precio_base)
        self._tipo_equipo = tipo_equipo

    def calcular_costo(self, duracion: float, impuesto: float = 0.0, descuento: float = 0.0) -> float:
        """Costo con recargo por equipos especiales"""
        if duracion <= 0:
            raise DatoInvalidoError("La duración debe ser mayor a cero")
        recargo = 1.05 if "profesional" in self._tipo_equipo.lower() else 1.0
        costo = self._precio_base * duracion * recargo
        costo += costo * impuesto
        costo -= costo * descuento
        return round(costo, 2)

    def descripcion(self) -> str:
        return f"Servicio: {self._nombre} — Tipo: {self._tipo_equipo}"

class Asesoria(Servicio):
    """Asesoría especializada"""
    def __init__(self, precio_base: float, especialista: str):
        super().__init__("Asesoría Especializada", precio_base)
        self._especialista = especialista

    def calcular_costo(self, duracion: float, impuesto: float = 0.0, descuento: float = 0.0) -> float:
        """Costo mínimo garantizado para asesorías"""
        if duracion <= 0:
            raise DatoInvalidoError("La duración debe ser mayor a cero")
        costo = self._precio_base * duracion
        costo += costo * impuesto
        costo -= costo * descuento
        return round(max(costo, 50.0), 2)  # Mínimo $50

    def descripcion(self) -> str:
        return f"Servicio: {self._nombre} — Especialista: {self._especialista}"

# ---------------------- CLASE RESERVA ----------------------
class Reserva(EntidadBase):
    """Clase que vincula cliente, servicio y duración con estado"""
    ESTADOS = {"PENDIENTE", "CONFIRMADA", "CANCELADA", "COMPLETADA"}

    def __init__(self, cliente: Cliente, servicio: Servicio, duracion: float):
        super().__init__()
        self._cliente = cliente
        self._servicio = servicio
        self._duracion = duracion
        self._estado = "PENDIENTE"
        self.validar_datos()
        registrar_log(f"Reserva creada: ID {self._id} | {cliente.nombre} → {servicio.nombre}")

    def validar_datos(self) -> bool:
        if not isinstance(self._cliente, Cliente):
            raise ReservaInvalidaError("El cliente proporcionado no es válido")
        if not isinstance(self._servicio, Servicio):
            raise ReservaInvalidaError("El servicio proporcionado no es válido")
        if self._duracion <= 0:
            raise DatoInvalidoError("La duración debe ser positiva")
        if not self._servicio.disponible:
            raise ServicioNoDisponibleError(f"El servicio {self._servicio.nombre} no está disponible")
        return True

    def confirmar(self) -> str:
        if self._estado != "PENDIENTE":
            raise ReservaInvalidaError(f"No se puede confirmar en estado {self._estado}")
        self._estado = "CONFIRMADA"
        self._servicio.marcar_disponible(False)
        registrar_log(f"Reserva {self._id} CONFIRMADA")
        return f"✅ Reserva {self._id} confirmada exitosamente"

    def cancelar(self) -> str:
        if self._estado == "COMPLETADA":
            raise ReservaInvalidaError("No se puede cancelar una reserva completada")
        self._estado = "CANCELADA"
        self._servicio.marcar_disponible(True)
        registrar_log(f"Reserva {self._id} CANCELADA")
        return f"❌ Reserva {self._id} cancelada"

    def procesar(self, impuesto: float = 0.0, descuento: float = 0.0) -> float:
        """Procesa reserva y retorna costo final con manejo de excepciones completo"""
        try:
            if self._estado != "CONFIRMADA":
                raise ReservaInvalidaError("Debe confirmar la reserva antes de procesarla")
            costo = self._servicio.calcular_costo(self._duracion, impuesto, descuento)
        except ReservaInvalidaError as e:
            registrar_log(f"Error procesando reserva {self._id}: {e}", "ERROR")
            raise
        else:
            self._estado = "COMPLETADA"
            registrar_log(f"Reserva {self._id} procesada. Costo: ${costo}")
            return costo
        finally:
            # Se ejecuta siempre
            pass

    @property
    def estado(self) -> str:
        return self._estado

    def __str__(self) -> str:
        return (f"Reserva #{self._id} | Estado: {self._estado}\n"
                f"   Cliente: {self._cliente.nombre}\n"
                f"   Servicio: {self._servicio.nombre}\n"
                f"   Duración: {self._duracion} horas")

# ---------------------- GESTIÓN DEL SISTEMA ----------------------
class SistemaGestion:
    """Contenedor principal del sistema"""
    def __init__(self):
        self.clientes: list[Cliente] = []
        self.servicios: list[Servicio] = []
        self.reservas: list[Reserva] = []
        registrar_log("=== SISTEMA INICIADO ===")

    def registrar_cliente(self, nombre: str, correo: str, telefono: str) -> Cliente | None:
        try:
            cliente = Cliente(nombre, correo, telefono)
        except ClienteSinDatosError:
            registrar_log("Intento de registro sin datos", "ERROR")
        except DatoInvalidoError as e:
            print(f"⚠️ No se pudo registrar cliente: {e}")
            return None
        else:
            self.clientes.append(cliente)
            print(f"✅ Cliente registrado: {cliente.nombre}")
            return cliente

    def crear_servicio(self, tipo: str, *args) -> Servicio | None:
        try:
            if tipo == "sala":
                servicio = ServicioSala(*args)
            elif tipo == "equipos":
                servicio = AlquilerEquipos(*args)
            elif tipo == "asesoria":
                servicio = Asesoria(*args)
            else:
                raise DatoInvalidoError(f"Tipo de servicio '{tipo}' no existe")
            servicio.validar_datos()
        except DatoInvalidoError as e:
            print(f"⚠️ No se pudo crear servicio: {e}")
            return None
        else:
            self.servicios.append(servicio)
            print(f"✅ Servicio creado: {servicio.nombre}")
            return servicio

    def hacer_reserva(self, cliente: Cliente, servicio: Servicio, duracion: float) -> Reserva | None:
        try:
            reserva = Reserva(cliente, servicio, duracion)
        except (ServicioNoDisponibleError, ReservaInvalidaError, DatoInvalidoError) as e:
            print(f"⚠️ Reserva fallida: {e}")
            return None
        else:
            self.reservas.append(reserva)
            print(f"✅ Reserva creada — ID: {reserva.id}")
            return reserva

    def listar_reservas(self) -> None:
        print("\n=== LISTA DE RESERVAS ===")
        for r in self.reservas:
            print(r)

# ---------------------- DEMOSTRACIÓN (10+ OPERACIONES) ----------------------
def main():
    print("="*55)
    print("  SISTEMA DE GESTIÓN — Software FJ | UNAD 213023")
    print("="*55)

    sg = SistemaGestion()

    # --- OPERACIÓN 1: Cliente válido ---
    sg.registrar_cliente("María López", "maria@ejemplo.com", "3124567890")

    # --- OPERACIÓN 2: Cliente con correo inválido ---
    sg.registrar_cliente("Juan Pérez", "correo_incorrecto", "3101234567")

    # --- OPERACIÓN 3: Cliente con teléfono corto ---
    sg.registrar_cliente("Ana Ruiz", "ana@ejemplo.com", "12345")

    # --- OPERACIÓN 4: Otro cliente válido ---
    sg.registrar_cliente("Carlos Méndez", "carlos@ejemplo.com", "3159876543")

    # --- OPERACIÓN 5: Servicio sala válido ---
    sala = sg.crear_servicio("sala", 80.0, 15)

    # --- OPERACIÓN 6: Servicio con precio negativo (inválido) ---
    sg.crear_servicio("equipos", -50.0, "Portátiles")

    # --- OPERACIÓN 7: Servicio equipos válido ---
    equipos = sg.crear_servicio("equipos", 45.0, "Equipos de edición profesional")

    # --- OPERACIÓN 8: Servicio asesoría válido ---
    asesoria = sg.crear_servicio("asesoria", 120.0, "Ing. Ramírez")

    # --- OPERACIÓN 9: Tipo de servicio inexistente ---
    sg.crear_servicio("transporte", 30.0, "Vehículos")

    # --- OPERACIÓN 10: Reserva exitosa ---
    if sala and sg.clientes:
        r1 = sg.hacer_reserva(sg.clientes[0], sala, 3.0)
        if r1:
            print(r1.confirmar())
            costo = r1.procesar(impuesto=0.12, descuento=0.05)
            print(f"💵 Costo final: ${costo}")

    # --- OPERACIÓN 11: Reserva a servicio no disponible ---
    if sg.clientes and equipos:
        r2 = sg.hacer_reserva(sg.clientes[0], sala,
