import numpy as np
import matplotlib.pyplot as plt

"""
Functions to model the SLS rocket
Used to determine the ratio between what mass can be brought to a Moon/Mars orbit and what mass can be brought to the surface of the Moon/Mars, using the same rocket
"""

## constant ##
g0 = 9.81

## functions ##
def one_stage_calc(m_payload, m_rocket, spec_imp, delta_v):
	"""
	Calculations for 1 booster
	Classic tsiokovsky equation
	Returns wet mass at launch and fuel mass
	"""
	dry_mass = m_rocket + m_payload
	wet_mass = dry_mass * np.exp(delta_v / g0 / spec_imp)
	fuel_mass = wet_mass - dry_mass
	return(wet_mass, fuel_mass)

#def two_stages_calc(m_payload, delta_v_1, delta_v_2):
	# """
	# Calculates the energy / kg for a given payload mass
	# Uses a 2 stages rockets with specs from SLS (not including boosters...)
	# delta_v for each stage can also be used as a variable
	# """
	# ## stage two ##
	# # specs
	# m_rocket_2 = 4000.0
	# spec_imp_2 = 462.00
	# fuel_ener_intensity_2 = 9.7

	# #calculations
	# dry_mass_2 = m_rocket_2 + m_payload
	# wet_mass_2 = dry_mass_2 * np.exp(delta_v_2 / g0 / spec_imp_2)
	# fuel_mass_2 = wet_mass_2 - dry_mass_2
	# energy_2 = fuel_mass_2 * fuel_ener_intensity_2

	# ## stage 1 ##
	# # specs
	# m_rocket_1 = 85000.0
	# spec_imp_1 = 363.00
	# fuel_ener_intensity_1 = 9.7

	# #calculations
	# dry_mass_1 = m_rocket_1 + wet_mass_2
	# wet_mass_1 = dry_mass_1 * np.exp(delta_v_1 / g0 / spec_imp_1)
	# fuel_mass_1 = wet_mass_1 - dry_mass_1
	# energy_1 = fuel_mass_1 * fuel_ener_intensity_1

	# energy_tot = energy_1 + energy_2

	# return(energy_tot / m_payload)

def sls_model(m_payload, delta_v_b, delta_v_1, delta_v_2):
	"""
	3-stage model of Space Launch System
	Returns the wet mass computed, and a check value that asserts if the maximum fuel mass has been exceeded
	"""

	## specs ##
	#stage 2
	m_rocket_2 = 3490.0
	spec_imp_2 = 462.0
	max_fuel_2 = 30710
	#stage 1
	m_rocket_1 = 85000.0
	spec_imp_1 = 363.0
	max_fuel_1 = 987000.
	#solid rocket boosters
	m_rocket_b = 130000.
	#spec_imp_b = 269.0
	spec_imp_b = 275.0
	max_fuel_b = 1400000

	## calculations ## 
	# stage 2
	(wet_mass_2, fuel_mass_2) = one_stage_calc(m_payload,
	 							m_rocket_2,
								spec_imp_2,
								delta_v_2)

	# stage 1
	(wet_mass_1, fuel_mass_1) = one_stage_calc(wet_mass_2,
	 							m_rocket_1,
								spec_imp_1,
								delta_v_1)

	# solid rocket boosters
	(wet_mass_b, fuel_mass_b) = one_stage_calc(wet_mass_1,
	 							m_rocket_b,
								spec_imp_b,
								delta_v_b)

	# checking if maximum fuel masses have been exceeded
	checklist = [(fuel_mass_2 < max_fuel_2),
			(fuel_mass_1 < max_fuel_1),
			(fuel_mass_b < max_fuel_b)]
	#print(checklist)
	check = checklist[0] & checklist[1] & checklist[2]

	return(wet_mass_b, check)

def optimal_delta_repartition(m_payload, delta_v):
	"""
	for a given delta-v and a payload mass, calculates all the possible delta-v repartitions (between bosters, stage 1 and stage 2)
	returns the optimal one (smaller wet_mass)
	returns false if not possible to reach delta-v with the given payload
	"""
	n = 200 #sets the level of precision but also computing time
	wet_masses = []
	delta_vs = []
	delta_v_2s = np.linspace(0, delta_v, n)
	delta_v_1s = np.linspace(0, delta_v, n)

	for delta_v_1 in delta_v_1s:
		for delta_v_2 in delta_v_2s:#

			if delta_v_1 + delta_v_2 < delta_v:
				#only computing if delta v repartition makes sense
				delta_v_b = delta_v - delta_v_1 - delta_v_2
				result = sls_model(m_payload,
										  delta_v_b,
										  delta_v_1,
										  delta_v_2)
				if result[1]:
					# add result only if validated by sls model (check = True)
					wet_masses.append(result[0])
					delta_vs.append((delta_v_1, delta_v_2))

	if (len(wet_masses) == 0):
		# delta_v not doable with given payload
		return(False)

	else :
		optimal_mass = min(wet_masses)
		optimal_index = wet_masses.index(min(wet_masses))
		optimal_repartition = delta_vs[optimal_index]

		return(optimal_mass, optimal_repartition[0], optimal_repartition[1])

def max_payload(delta_v):
	"""
	calculates the maximum payload that the SLS can carry to a given delta-v
	"""
	n = 300 #sets the level of precision but also computing time
	m_payloads = np.linspace(0, 30000, n)
	max_payload = 0

	for m_payload in m_payloads:
		rep_result = optimal_delta_repartition(m_payload, delta_v)
		if  rep_result == False:
			return(max_payload)
		else :
			max_payload = m_payload

	return("Maximum mass reached, change parameters in max_payload function")


##########
## Main ##
##########

## Moon ##

delta_v_orbit = 9300 + 3400
delta_v_surface = 9300 + 3400 + 2500

## calculations ## 
max_payload_orbit = max_payload(delta_v_orbit)
max_payload_surface = max_payload(delta_v_surface)
ratio_moon = max_payload_orbit / max_payload_surface

print("Maximum mass in Moon orbit : {}".format(max_payload_orbit))
print("Maximum mass on Moon surface : {}".format(max_payload_surface))
print("Moon ratio : {}".format(ratio_moon))


# ## Mars ##

# delta_v_orbit_mars = 9300 + 4300 + 600
# delta_v_aerobrake_mars = 2000
# delta_v_surface_mars = 9300 + 4300 + 5500 - delta_v_aerobrake_mars

# ## calculations ## 
# max_payload_orbit_mars = max_payload(delta_v_orbit_mars)
# max_payload_surface_mars = max_payload(delta_v_surface_mars)
# ratio_mars = max_payload_orbit_mars / max_payload_surface_mars

# print("Maximum mass in Mars orbit : {}".format(max_payload_orbit_mars))
# print("Maximum mass on Mars surface : {}".format(max_payload_surface_mars))
# print("Mars ratio : {}".format(ratio_mars))

