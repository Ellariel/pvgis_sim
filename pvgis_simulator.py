from __future__ import annotations

import arrow
import copy
import pandas as pd
from os.path import abspath
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Set, Tuple
import mosaik_api_v3
from pvgis import PVGIS
from mosaik_api_v3.types import (
    CreateResult,
    CreateResultChild,
    Meta,
    ModelDescription,
    OutputData,
    OutputRequest,
)

META = {
    "api_version": "3.0",
    "type": "time-based",
    "models": {
        "PV": {
            "public": True,
            "any_inputs": True,
            "persistent": [],
            "params": [], 
            "attrs": ["P[MW]",      # estimated active PV power supply based on reference year, [MW]
            ],   
        }
    },
}

STEP_SIZE = 15*60  # minutes
CACHE_DIR = Path(abspath(__file__)).parent
DATE_FORMAT = "YYYY-MM-DD HH:mm:ss"

class PVGISSimulator(mosaik_api_v3.Simulator):
    _sid: str
    """This simulator's ID."""
    _step_size: Optional[int]
    """The step size for this simulator. If ``None``, the simulator
    is running in event-based mode, instead.
    """
    sim_params: Dict
    """Emission methodology specification:
    DEFAULT_CONFIG = {
    "ExternalGrid": {
        "input_attr": "P[MW]",
        "output_attr": "E[tCO2eq]",
        "country": "Germany",
        "co2_intensity": 0.385, # [tones CO₂eq. / MWh]
        "method": None, # callable that transforms input data to output
    }, 
    """

    def __init__(self) -> None:
        super().__init__(META)
    
    def init(self, sid: str, time_resolution: float, step_size: int = STEP_SIZE, sim_params: Dict = {}):
        self.cache_dir = sim_params.get('cache_dir', CACHE_DIR)
        self.verbose = sim_params.get('verbose', True)
        self.date = arrow.get(sim_params.get('start_date', '2016-01-01 00:00:01'), DATE_FORMAT)
        self.step_size = step_size
        self.sid = sid
        self.pvgis = PVGIS(verbose=self.verbose, 
                           local_cache_dir=self.cache_dir)
        self.entities = {}
        return self.meta

    def create(self, num: int, model: str, **model_params: Any) -> List[CreateResult]:
        entities = []
        for n in range(len(self.entities), len(self.entities) + num):
            eid = f"{model}-{n}"
            production, info = self.pvgis.get_production_timeserie(**model_params)
            production.index = production.index + pd.offsets.DateOffset(years=self.date.year - production.index[0].year) # change history year to current one
            self.entities[eid] = production
            entities.append({
                "eid": eid,
                "type": model,
            })
        return entities
    
    def _get_production(self, eid, attr):
        return self.entities[eid]

    def step(self, time, inputs, max_advance):
        self.date = self.date.shift(seconds=self.step_size)
        return time + self.step_size
     
    def get_data(self, outputs: OutputRequest) -> OutputData:
        return {eid: {attr: self._get_production(eid, attr) 
                            for attr in attrs
                                } for eid, attrs in outputs.items()}