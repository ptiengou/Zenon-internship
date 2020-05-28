from tkinter import *
from tkinter.ttk import *
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# functions #

def model_1(station_mass, duration, surface_payload, month_supply, o_s_ratio):
	# constants
	orion_mass = 26500.0

	# calculations
	supply_mass = duration * month_supply
	total_orbit_mass = station_mass + supply_mass + orion_mass

	# outputs
	equivalent_surface_mass = total_orbit_mass / o_s_ratio + surface_payload
	mass_on_surface_ratio = equivalent_surface_mass / surface_payload

	return(equivalent_surface_mass, mass_on_surface_ratio)

def model_2(station_mass, duration, surface_payload, month_supply, o_s_ratios):
	""" 
	more detailed model that includes bringing back part of the mass to Earth (astronauts and station)
	o_s_ratios is  list of two elements : ratio for one-way and round-trip
	"""


	# const
	orion_mass = 26500.0

	# calc
	supply_mass = duration * month_supply
	round_trip_mass = orion_mass + station_mass

	equivalent_surface_mass = supply_mass / o_s_ratios[0] + round_trip_mass / o_s_ratios[1] + surface_payload
	mass_on_surface_ratio = equivalent_surface_mass / surface_payload

	return(equivalent_surface_mass, mass_on_surface_ratio)

def variable_payload_model(station_mass, duration, month_supply, o_s_ratio, min_p, max_p):

	surface_payloads = np.linspace(min_p,max_p,10000)
	ratios = []

	for surface_payload in surface_payloads:
		result = model_1(station_mass, duration, surface_payload, month_supply, o_s_ratio)
		ratios.append(result[1])

	return(surface_payloads, ratios)

def variable_payload_model_mars(station_mass, duration, month_supply, o_s_ratios, min_p, max_p):

	surface_payloads = np.linspace(min_p,max_p,10000)
	ratios = []

	for surface_payload in surface_payloads:
		result = model_2(station_mass, duration, surface_payload, month_supply, o_s_ratios)
		ratios.append(result[1])

	return(surface_payloads, ratios)

def threshold_mass(surface_payloads, ratios, threshold):
	"""
	Takes two lists and finds limit mass where a threshold ratio is reached
	"""
	ratios = np.asarray(ratios) 
	idx = (np.abs(ratios - threshold)).argmin()
	return(surface_payloads[idx])

# classes #

class Interface:

	def __init__(self, root):

		# create tabs
		self.tab_control = Notebook(root)
		self.tab1 = Frame(self.tab_control)
		self.tab_control.add(self.tab1, text = "Moon")
		self.tab2 = Frame(self.tab_control)
		self.tab_control.add(self.tab2, text = "Mars")
		self.tab_control.grid(column = 0, row = 0)

		# create inputs
		self._create_inputs_moon(self.tab1)
		self._create_inputs_mars(self.tab2)

		# create buttons
		self.compute_btn = Button(root, text="Compute", command=self._compute)
		self.compute_btn.grid(column=0, row=1)
		
		self.reset_btn = Button(root, text="Reset", command=self._reset)
		self.reset_btn.grid(column=0, row=2)

		# plotting tools
		fig = Figure()
		fig.suptitle('Mass-on-surface ratio variations with surface payload mass', fontsize=15)
		self.ax = fig.add_subplot(111)
		self.ax.set_xlabel('Mass of payload on the surface for LLT mission (kg)')
		self.ax.set_ylabel('Mass-on-surface ratio')
		self.ax.grid()
		#self.ax.plot(range(10))

		self.canvas = FigureCanvasTkAgg(fig, master = root)
		self.canvas.get_tk_widget().grid(column = 0, row = 3)

	def _create_inputs_moon(self, root):
		self.station_lbl = Label(root, text="Station mass")
		self.station_lbl.grid(column=0, row=0)
		self.station_txt = Entry(root,width=10)
		self.station_txt.insert(END, '40000')
		self.station_txt.grid(column=1, row=0)

		self.supply_lbl = Label(root, text="Monthly supply mass")
		self.supply_lbl.grid(column=0, row=1)
		self.supply_txt = Entry(root,width=10)
		self.supply_txt.insert(END, '1000')
		self.supply_txt.grid(column=1, row=1)

		self.duration_lbl = Label(root, text="Mission duration")
		self.duration_lbl.grid(column=0, row=2)
		self.duration_txt = Entry(root,width=10)
		self.duration_txt.insert(END, '24')
		self.duration_txt.grid(column=1, row=2)

		self.orbit_lbl = Label(root, text = "Choice of orbit")
		self.orbit_lbl.grid(column=0, row=3)

		self.moon_selected = DoubleVar()

		self.orbit_0 = Radiobutton(root,text='LLO', value = 2.092, variable = self.moon_selected, command = self._orbit_click)
		self.orbit_0.grid(column=1, row=3)
		self.orbit_1 = Radiobutton(root,text='E-M L2', value = 2.631, variable = self.moon_selected, command = self._orbit_click)
		self.orbit_1.grid(column=2, row=3)
		self.orbit_2 = Radiobutton(root,text='Limit case', value = 3.0, variable = self.moon_selected, command = self._orbit_click)
		self.orbit_2.grid(column=3, row=3)

		self.moon_selected.set(2.631)

		self.ratio_lbl = Label(root, text="Orbit/surface ratio")
		self.ratio_lbl.grid(column=0, row=4)

		self.moon_ratio_string = StringVar()
		self.moon_ratio_string.set("{}".format(self.moon_selected.get()))
		self.ratio_value_lbl = Label(root, textvariable = self.moon_ratio_string)
		self.ratio_value_lbl.grid(column=1, row = 4)

		#surface payload variations
		self.payload_lbl = Label(root, text="Surface payload mass")
		self.payload_lbl.grid(column=0, row=6)
		self.payload_min_lbl = Label(root, text="Min value")
		self.payload_min_lbl.grid(column=1, row=5)
		self.payload_max_lbl = Label(root, text="Max value")
		self.payload_max_lbl.grid(column=2, row=5)

		self.payload_min_txt = Entry(root,width=10)
		self.payload_min_txt.insert(END, '3000')
		self.payload_min_txt.grid(column=1, row=6)
		self.payload_max_txt = Entry(root,width=10)
		self.payload_max_txt.insert(END, '50000')
		self.payload_max_txt.grid(column=2, row=6)

	def _create_inputs_mars(self, root):
		self.station_lbl2 = Label(root, text="Station mass")
		self.station_lbl2.grid(column=0, row=0)
		self.station_txt2 = Entry(root,width=10)
		self.station_txt2.insert(END, '40000')
		self.station_txt2.grid(column=1, row=0)

		self.supply_lbl2 = Label(root, text="Monthly supply mass")
		self.supply_lbl2.grid(column=0, row=1)
		self.supply_txt2 = Entry(root,width=10)
		self.supply_txt2.insert(END, '1000')
		self.supply_txt2.grid(column=1, row=1)

		self.duration_lbl2 = Label(root, text="Mission duration")
		self.duration_lbl2.grid(column=0, row=2)
		self.duration_txt2 = Entry(root,width=10)
		self.duration_txt2.insert(END, '36')
		self.duration_txt2.grid(column=1, row=2)

		self.aerobraking_lbl = Label(root, text="Surface landing scenario")
		self.aerobraking_lbl.grid(column=0, row=3)

		self.selected = IntVar()
		self.delta_vs_one_way = [2.904, 3.341, 12.673]
		self.delta_vs_round_trip = [1.611, 1.854, 7.032]

		self.aerobraking_0 = Radiobutton(root,text='Heat shields', value = 0, variable = self.selected, command = self._aero_click)
		self.aerobraking_0.grid(column=1, row=3)
		self.aerobraking_1 = Radiobutton(root,text='Aerobraking', value = 1, variable = self.selected, command = self._aero_click)
		self.aerobraking_1.grid(column=2, row=3)
		self.aerobraking_2 = Radiobutton(root,text='No aerobraking', value = 2, variable = self.selected, command = self._aero_click)
		self.aerobraking_2.grid(column=3, row=3)
		self.selected.set(0)

		self.ratio_lbl2 = Label(root, text = "Orbit/surface ratio")
		self.ratio_lbl2.grid(column=0, row = 4)

		self.ratio_string = StringVar()
		index = self.selected.get()
		self.ratio_string.set("{} (one-way)\n {} (round trip)".format(self.delta_vs_one_way[index], self.delta_vs_round_trip[index]))
		self.ratio_value2_lbl = Label(root, textvariable = self.ratio_string)
		self.ratio_value2_lbl.grid(column=1, row = 4)

		self.payload_lbl2 = Label(root, text="Surface payload mass")
		self.payload_lbl2.grid(column=0, row=6)
		self.payload_min_lbl2 = Label(root, text="Min value")
		self.payload_min_lbl2.grid(column=1, row=5)
		self.payload_max_lbl2 = Label(root, text="Max value")
		self.payload_max_lbl2.grid(column=2, row=5)

		self.payload_min_txt2 = Entry(root,width=10)
		self.payload_min_txt2.insert(END, '1000')
		self.payload_min_txt2.grid(column=1, row=6)
		self.payload_max_txt2 = Entry(root,width=10)
		self.payload_max_txt2.insert(END, '10000')
		self.payload_max_txt2.grid(column=2, row=6)

	def _get_inputs(self):
		tab = self.tab_control.tab(self.tab_control.select(), "text")

		if (tab == 'Moon'):
			station_mass = float(self.station_txt.get())
			month_supply = float(self.supply_txt.get())
			duration = float(self.duration_txt.get())
			surface_payload_min = float(self.payload_min_txt.get())
			surface_payload_max = float(self.payload_max_txt.get())
			orbit_to_surface_ratio = self.moon_selected.get()

			return(station_mass, duration, month_supply, orbit_to_surface_ratio, surface_payload_min, surface_payload_max)

		elif (tab == 'Mars'):
			station_mass = float(self.station_txt2.get())
			month_supply = float(self.supply_txt2.get())
			duration = float(self.duration_txt2.get())
			surface_payload_min = float(self.payload_min_txt2.get())
			surface_payload_max = float(self.payload_max_txt2.get())
			index = self.selected.get()
			orbit_to_surface_ratio_one_way = self.delta_vs_one_way[index]
			orbit_to_surface_ratio_round_trip = self.delta_vs_round_trip[index]

			return(station_mass, duration, month_supply, (orbit_to_surface_ratio_one_way, orbit_to_surface_ratio_round_trip), surface_payload_min, surface_payload_max)

	def _compute(self):

		# collect_inputs
		(station_mass, duration, month_supply, orbit_to_surface_ratio, surface_payload_min, surface_payload_max) = self._get_inputs()
		
		#plot graph
		tab = self.tab_control.tab(self.tab_control.select(), "text")
		if (tab == 'Moon'):
			result = variable_payload_model(station_mass, duration, month_supply, orbit_to_surface_ratio, surface_payload_min, surface_payload_max)		
			self.ax.plot(result[0], result[1], label = "station : {:.0f}t ; supply : {:.1f}t/mo ; d : {:.0f}mo ; r : {}".format(station_mass/1000, month_supply/1000, duration, orbit_to_surface_ratio))
			self.ax.legend()
			self.canvas.draw()

			#print("Ratio of 2 : {} kg".format(threshold_mass(result[0], result[1], 2)))
			# print("Ratio of 3.4 : {} kg".format(threshold_mass(result[0], result[1], 3.4)))
			# print("Ratio of 5 : {} kg".format(threshold_mass(result[0], result[1], 5)))
			# print("Ratio of 10 : {} kg\n".format(threshold_mass(result[0], result[1], 10)))

		elif (tab == 'Mars'):
			result = variable_payload_model_mars(station_mass, duration, month_supply, orbit_to_surface_ratio, surface_payload_min, surface_payload_max)		
			self.ax.plot(result[0], result[1], label = "station : {:.0f}t ; supply : {:.1f}t/mo ; d : {:.0f}mo ; r : {}".format(station_mass/1000, month_supply/1000, duration, orbit_to_surface_ratio))
			self.ax.legend()
			self.canvas.draw()

			#print beak-even values
			# print("Ratio of 5 : {} kg".format(threshold_mass(result[0], result[1], 5)))
			# print("Ratio of 10 : {} kg".format(threshold_mass(result[0], result[1], 10)))
			# print("Ratio of 15.5 : {} kg".format(threshold_mass(result[0], result[1], 15.5)))
			# print("Ratio of 50 : {} kg\n".format(threshold_mass(result[0], result[1], 50)))

	def _reset(self):
		self.ax.clear()
		self.ax.set_xlabel('Mass of payload on the surface for LLT mission (kg)')
		self.ax.set_ylabel('Mass-on-surface ratio')
		self.ax.grid()
		self.canvas.draw()

	def _aero_click(self):
		index = self.selected.get()
		self.ratio_string.set("{} (one-way)   \n {} (round trip)".format(self.delta_vs_one_way[index], self.delta_vs_round_trip[index]))

	def _orbit_click(self):
 		self.moon_ratio_string.set("{}".format(self.moon_selected.get()))


##########
## MAIN ##
##########

root = Tk()
root.title("Model")
root.geometry('660x780')

interface = Interface(root)

root.mainloop()
