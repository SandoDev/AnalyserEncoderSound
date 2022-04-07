"""
Digital to Digital
Manchester differential
"""
import numpy as np
import matplotlib.pyplot as plt


def enconding_man_diff(clk, data):
    man_diff = 1*clk    # manchester-differential just a copy of the clk

    level = 0
    sync = 5

    #print("data", data)
    #print("man_diff", man_diff)

    current_pos = 0

    for ii in range(len(data)):
        # print("ii:",ii)
        # print("data[ii]:",data[ii])
        # print(man_diff[current_pos],man_diff[current_pos+1])

        if data[ii] == 0:
            man_diff[current_pos] = level
            man_diff[current_pos+1] = sync

        if data[ii] == 1:
            man_diff[current_pos] = sync
            man_diff[current_pos+1] = level
            level = man_diff[current_pos]
            sync = man_diff[current_pos+1]

        # print(man_diff[current_pos],man_diff[current_pos+1])
        # print()
        current_pos += 2

    return man_diff


def analog_to_digital_converter(signal, vcc, n_bits):
    """
    Retorna un array con los voltages de comparación para cada valor en la onda
    """
    resolution = vcc/(pow(2, n_bits)-1)
    # print("resolution:",resolution)
    # print()
    final_array = []  # contain decial values
    array_cicles = []  # contain decial values
    for a_value in signal:
        # print("a_value:",a_value)
        if a_value >= 0:
            round_clocks_cicles = np.round(a_value/resolution)
            array_cicles.append(round_clocks_cicles)
            # print("round_clocks_cicles:",round_clocks_cicles)
            # TODO esta linea ya no es necesaria, porque el hacer la division de a_value/resolution ya se obtiene el valor digital necesario
            voltage = round_clocks_cicles*resolution
            # print("voltage:",voltage)
            if a_value >= voltage:
                #print("yes, equal or major")
                final_array.append(voltage)
            else:
                #print("No, minor")
                final_array.append(voltage+resolution)
        else:
            # print("nagetive:",0)
            final_array.append(0)
        # print()
    return final_array, array_cicles
