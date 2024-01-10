import mosaik.util
SIM_CONFIG = {
    'PVSim': {
        'python': 'mosaik_components.pv.pvgis_simulator:PVGISSimulator'
    },
    'CSV_writer': {
        'python': 'mosaik_csv_writer:CSVWriter',
    },
}

START = "2020-01-01 00:00:00"
DATE_FORMAT = "YYYY-MM-DD HH:mm:ss"
END = 60 * 60 * 24 * 30
STEP_SIZE = 60 * 60 * 24

PVSIM_PARAMS = {
    'start_date' : START,
    'cache_dir' : './', # it caches PVGIS API requests
    'verbose' : True, # print PVGIS parameters and requests
}

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

world = mosaik.World(SIM_CONFIG)

# Create PV system
pv_sim = world.start(
                "PVSim",
                step_size=STEP_SIZE,
                sim_params=PVSIM_PARAMS,
            )
pv_model = pv_sim.PVSim.create(1, **PVMODEL_PARAMS)

csv_sim_writer = world.start('CSV_writer', start_date = START,
                                           output_file='results.csv')
csv_writer = csv_sim_writer.CSVWriter(buff_size = STEP_SIZE)

world.connect(
                    pv_model[0],
                    csv_writer,
                    'P[MW]',
                )

world.run(until=END)