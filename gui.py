#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Tkinter
#para que entienda las constantes de tkinter
from Tkconstants import *
#para que muestre la ventana de error
from tkMessageBox import *
import sys
from time import sleep
from PyMata.pymata import PyMata

#defino los pines que voy a usar
SRMTR = 8		#pin del servo salida analogica tipo PWM
IN1 = 9			#IN1 a IN4 son los pines del motor stepper salidas digitales
IN2 = 10
IN3 = 11
IN4 = 12
INP = 7			#entrada del boton entrada digital
POTE = 0		#entrada del potenciometroentrada analogica

#defino las variables para manipular las entradas/salidas
servo_pos = 90		#posición inicial (en grados) del servo
paso = 5			#paso en grados del servo
stepCW = 50			#pasos que da el stepper por cada pulsación de boton
					#o tecla en sentido horario
stepCCW = -stepCW	#idem anterior pero en sentido antihorario
manual = 0			#testigo de si el boton esta pulsado
					#si esta pulsado, el servo se mueve con el potenciometro
					#en el caso contrario, con los botones de la ventana
					#o el teclado

def cb_entrada_h(data):
	'''
	Callback del flanco ascendente del switch
	Seteo la variable manual en 1 para manejar con el potenciometro
	al servo. Le aviso a la ventana que deshabilite los botones y preparo el
	latch para que cuando vuelva a cambiar de estado, llame a la
	función cb_entrada_l
	'''
	
	global manual
	
	manual = 1
	app(btn = 1)
	ard.set_digital_latch(INP, ard.DIGITAL_LATCH_LOW, cb_entrada_l)

def cb_entrada_l(data):
	'''
	Callback del flanco descendente del switch
	Seteo la variable manual en 0 para manejar con los botones de la ventana
	o con el teclado al servo. Le aviso a la ventana que habilite los botones
	 y preparo el latch para que cuando vuelva a cambiar de estado
	llame a la función cb_entrada_h
	'''
	
	global manual, servo_pos
	
	manual = 0
	
	app(btn = 0)
	ard.set_digital_latch(INP, ard.DIGITAL_LATCH_HIGH, cb_entrada_h)

def cb_pote(data):
	'''
	Callback del cambio de estado del potenciometro,
	cambio la escala de 0 a 1024 a una escala de 0 a 180 para manejar el servo
	este resultado se lo paso a la ventana y llamo a la función pote_man
	para mover el servo
	'''
	val = (data[2]*180)/1024
	app(pot = val)
	pote_man(val)

def config_ardu():
	'''
	Configuro las I/O del sistema
	'''
	
	global ard
	#seteo el pin del servomotor y le paso la posición inicial
	ard.servo_config(SRMTR)
	ard.analog_write(SRMTR, servo_pos)
	
	#seteo los pines del stepper motor
	#en el caso del motor 28BYJ-48 se pasa el dato que son 2048 pasos por vuelta
	ard.stepper_config(2048, [9, 10, 11, 12])
	
	#configuro la entrada del switch y hago que cuando pase al estado HIGH
	#llame a la función cb_entrada_h
	ard.set_pin_mode(INP, ard.INPUT, ard.DIGITAL)
	ard.set_digital_latch(INP, ard.DIGITAL_LATCH_HIGH, cb_entrada_h)
	
	#configuro la entrada del potenciometro
	#en el cambio de valor, llama a la función cb_pote
	ard.set_pin_mode(POTE, ard.INPUT, ard.ANALOG, cb_pote)

def pote_man(pote):
	'''
	Si el switch esta en HIGH, le paso el valor escalado del potenciometro
	al servo
	'''
	
	global manual
	
	if (manual == 1):
		ard.analog_write(SRMTR, pote)

class simple(Tkinter.Tk):
	'''
	Clase encargada del GUI del sistema
	'''
	def __init__(self, parent):
		Tkinter.Tk.__init__(self, parent)
		self.parent = parent
		self.initialize()
		
	def initialize(self):
		
		self.grid()
		
		#inicio las variables de los labels
		#variable que indica el estado del switch
		self.lbl_switch = Tkinter.StringVar()
		self.lbl_switch.set("LOW")
		#variable que indica el valor escalado del potenciometro
		self.lbl_val_pote = Tkinter.IntVar()
		self.lbl_val_pote.set("0")
		
		#titulo e indicador del estado del switch
		self.lbl_titulo_switch = Tkinter.Label(self, text = "estado switch")
		self.lbl_titulo_switch.grid(column = 0, row = 0)
		
		self.lbl_man = Tkinter.Label(self, textvariable = self.lbl_switch)
		self.lbl_man.grid(column = 0, row = 1, sticky = 'EW')
		
		
		
		#titulo e indicador de la lectura del potenciometro
		self.lbl_titulo_pote = Tkinter.Label(self, text = "potenciometro")
		self.lbl_titulo_pote.grid(column = 0, row = 2)
		
		self.lbl_pote = Tkinter.Label(self, textvariable = self.lbl_val_pote)
		self.lbl_pote.grid(column = 0, row = 3)
		
		
		
		#botones para mover el servo
		self.lbl_titulo_servo = Tkinter.Label(self, text = "servo")
		self.lbl_titulo_servo.grid(column = 3, row = 0, columnspan = 2,
								   sticky = 'EW')
		
		#boton para incrementar el ángulo del servo
		self.btn_serv_pos = Tkinter.Button(self, text = "servo +",
										   command = self.ser_mas)
		self.btn_serv_pos.grid(column = 3, row = 1)
		self.bind('<Up>', lambda e : self.ser_mas())
		
		#boton para decrementar el ángulo del servo
		self.btn_serv_neg = Tkinter.Button(self, text = "servo -",
										   command = self.ser_men)
		self.btn_serv_neg.grid(column = 4, row = 1)
		self.bind('<Down>', lambda e : self.ser_men())
		
		
		
		#botones para mover el stepper
		self.lbl_titulo_stepper = Tkinter.Label(self, text = "stepper")
		self.lbl_titulo_stepper.grid(column = 3, row = 2, columnspan = 2,
									 sticky = 'EW')
		
		#boton para girar el motor hacia la izquierda
		self.btn_izq = Tkinter.Button(self, text = "izquierda",
									  command = self.izq)
		self.btn_izq.grid(column = 3, row = 3)
		self.bind('<Left>', lambda e : self.izq())
		
		self.btn_der = Tkinter.Button(self, text = "derecha",
									  command = self. der)
		self.btn_der.grid(column = 4, row = 3)
		self.bind('<Right>', lambda e : self.der())
		
		sleep(1)
		self.update_idletasks()
		self.update()
		self.geometry(self.geometry())
	
	def ser_mas(self):
		'''
		aumento el ángulo del servo, si se llegan a los 180 grados, se llama a
		una ventana de error alertando al usuario que se ha llegado
		al límite superior
		'''
		
		global servo_pos, paso
		
		if(servo_pos == 180):
			self.lbl_servo_err = "Llegaste al limite superior"
			self.alert()
		else:
			servo_pos = servo_pos + paso
			ard.analog_write(SRMTR, servo_pos)
	
	def ser_men(self):
		'''
		disminuyo el ángulo del servo, si se llegan a los 0 grados, se llama a
		una ventana de error alertando al usuario que se ha llegado
		al límite inferior
		'''
		
		global servo_pos, paso
		
		if(servo_pos == 0):
			self.lbl_servo_err = "Llegaste al limite inferior"
			self.alert()
		else:
			servo_pos = servo_pos - paso
			ard.analog_write(SRMTR, servo_pos)
	
	def izq(self):
		'''
		muevo a la izquierda al motor stepper y espero 1 segundo para 
		evitar problemas de comunicación con el arduino
		'''
		ard.stepper_step(3, stepCCW)
		sleep(1)
	
	def der(self):
		'''
		muevo a la derecha al motor stepper y espero 1 segundo para 
		evitar problemas de comunicación con el arduino
		'''
		ard.stepper_step(3, stepCW)
		sleep(1)
	
	def __call__(self, **kwargs):
		'''
		Recibo la información de las funciones externas para modificar los
		labels y el estado de los botones del servo.
		'''
		
		if(kwargs is not None):
			for key, value in kwargs.iteritems():
				if(key == "btn"):
					if(value == 0):
						#el switch no esta presionado, los botones se habilitan
						self.lbl_switch.set("LOW")
						self.btn_serv_pos.config(state = NORMAL)
						self.btn_serv_neg.config(state = NORMAL)
					else:
						#el switch esta presionado, los botones se deshabilitan
						self.lbl_switch.set("HIGH")
						self.btn_serv_pos.config(state = DISABLED)
						self.btn_serv_neg.config(state = DISABLED)
				elif(key == "pot"):
					#actualizo el valor escalado del potenciometro
					self.lbl_val_pote.set(value)
				else:
					break
		
	
	def alert(self):
		'''
		muestro un mensaje de error en el caso de llegar a un
		valor de 0 o de 180 en la variable servo_pos
		'''
		showerror("ERROR", self.lbl_servo_err)
		

if __name__ == "__main__":
	ard = PyMata()
	app = simple(None)
	app.title('my app')
	app.focus_set()
	config_ardu()
	app.mainloop()
	ard.close()
