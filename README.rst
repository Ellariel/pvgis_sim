==========
mosaik-pv-3
==========

This component simulates PV power output based on `PVGIS <"https://re.jrc.ec.europa.eu/">`_ photovoltaic performance data.

The PV simulator does not require any input, the only need to configure the PV system, geographical location and select an available reference year.

Since PVGIS only provides hourly data, any other step_size causes the data to be aggregated or splitted accordingly. If the step_size is less than an hour, it splits the value equally.

PV output data:

* P - active power [MW]

An example scenario is located in the ´demo´ folder.

Installation
============
* To use this project, you have to install at least version 3.2.0 of `mosaik <https://mosaik.offis.de/>`_.
* It is recommended, to use the Mosaik-CSV Library to export the results.
If you don't want to install this project through PyPI, you can use pip to install the requirements.txt file::

    pip install -r requirements.txt

How to Use
==========
Specify simulators configurations within your scenario script::

    SIM_CONFIG = {
        'PVSim': {
            'python': 'mosaik_components.pv.pvgis_simulator:PVGISSimulator'
        },
        'CSV_writer': {
            'python': 'mosaik_csv_writer:CSVWriter',
        },
        ...
    }

Initialize the PV-system::
   
    # Create PV system with certain configuration
    PVSIM_PARAMS = {
        'start_date' : START,
        'cache_dir' : './', # it caches PVGIS API requests
        'verbose' : True, # print PVGIS parameters and requests
    }
    pv_sim = world.start(
                    "PVSim",
                    step_size=STEP_SIZE,
                    sim_params=PVSIM_PARAMS,
                )

Instantiate model entities::

    PVMODEL_PARAMS = {
        'scale_factor' : 1000, # multiplies power production, 1 is equal to 1 kW peak power installed
        'lat' : 52.373, 
        'lon' : 9.738,
        'slope' : 0, # default value,
        'azimuth' : 0, # default value,
        'optimal_angle' : True, # calculate and use an optimal slope
        'optimal_both' : False, # calculate and use an optimal slope and azimuth
        'pvtech' : 'CIS', # default value,
        'system_loss' : 14, # default value,
        'database' : 'PVGIS-SARAH', # default value,
        'datayear' : 2016, # default value,
    }
    pv_model = pv_sim.PVSim.create(1, **PVMODEL_PARAMS)

Connect with PV-simulator::

    world.connect(
                        pv_model[0],
                        csv_writer,
                        'P[MW]',
                    )

    world.run(until=END)

