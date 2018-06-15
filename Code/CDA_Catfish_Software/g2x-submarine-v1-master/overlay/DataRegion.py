class DataRegion:
    def __init__(self):
        self.data = []

    def addTimeData(self, data_time, data_value):
        self.data.append((data_time, data_value))

    def isTimeInRegion(self, secs_since_epoch):
        return self.data[0][0] <= secs_since_epoch <= self.data[-1][0]

    def dataInTimeRegion(self, start_time, end_time):
        in_region = False
        result = []

        for item in self.data:
            # print(item[0])
            if not in_region:
                if start_time <= item[0] <= end_time:
                    in_region = True
                    result.append(item)
            else:
                if end_time < item[0]:
                    in_region = False
                else:
                    result.append(item)

        return result

    def interpolatedValueAtTime(self, secs_since_epoch):
        if secs_since_epoch < self.data[0][0]:
            return None
        elif self.data[-1][0] < secs_since_epoch:
            return None
        else:
            start = None
            end = None

            for (time, value) in self.data:
                if time == secs_since_epoch:
                    return value
                else:
                    if time <= secs_since_epoch:
                        start = (time, value)
                    elif secs_since_epoch < time:
                        if end is None:
                            end = (time, value)

            time_delta = end[0] - start[0]
            percent = time_delta / (secs_since_epoch - start[0])
            value_delta = end[1] - start[1]

            return start[1] + value_delta * percent
