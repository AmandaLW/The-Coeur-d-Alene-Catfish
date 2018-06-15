import sqlite3
from DataRegion import DataRegion

SELECT_DEPTH = """
select
    date, property, value
from
    readings
where
    device='Pressure/Temperature' and
    property in ('running','depth_feet')
"""

SELECT_TEMPERATURE = """
select
    date, property, value
from
    readings
where
    device='Pressure/Temperature' and
    property in ('running','fahrenheit')
"""


class DataManager:
    def __init__(self):
        self.depth_regions = []
        self.temperature_regions = []

    def load(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.depth_regions = self.process_query(SELECT_DEPTH)
        self.temperature_regions = self.process_query(SELECT_TEMPERATURE)
        self.connection.close()

    def process_query(self, query):
        running = False
        regions = []
        currentRegion = None

        for (date, property, value) in self.connection.execute(query):
            if property == "running":
                running = value == 1.0

                if running:
                    currentRegion = DataRegion()
                    regions.append(currentRegion)
                else:
                    if currentRegion is not None and len(currentRegion.data) == 0:
                        regions.pop()

                    currentRegion = None
            elif running:
                currentRegion.addTimeData(date, value)
            else:
                print("hmm, got value, but we're not supposedly running")

        return regions

    def select_depths(self, start_time, end_time):
        result = []

        for region in self.depth_regions:
            result.extend(region.dataInTimeRegion(start_time, end_time))

        return result

    def select_temperatures(self, start_time, end_time):
        result = []

        for region in self.temperature_regions:
            result.extend(region.dataInTimeRegion(start_time, end_time))

        return result
