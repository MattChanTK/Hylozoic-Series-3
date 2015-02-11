import threading
from datetime import datetime
import queue


class DataCollection(object):

    def __init__(self):

        self.__data = dict()
        self.creation_date = datetime.now()

    @property
    def data(self):
        return self.__data

class DataCollector(object):

    def __init__(self, data: DataCollection):

        self.data_q = queue.Queue()
        self.lock = threading.Lock()

        if data is None:
            data = DataCollection()
        if not isinstance(data, DataCollection):
            raise TypeError("Data must be in DataCollection class")
        self.data_collection = data

    def enqueue(self, robot_name: str, var_name: str, val, time=None):
        self.data_q.put_nowait((robot_name, var_name, val, time))


    def append(self):

        with self.lock:

            while not self.data_q.empty():

                data_package = self.data_q.get()
                robot_name = data_package[0]
                var_name = data_package[1]
                val = data_package[2]
                time = data_package[3]

                if not isinstance(robot_name, str):
                    raise TypeError("Robot name must be a String")
                if not isinstance(var_name, str):
                    raise TypeError("Variable name must be a String")

                if not isinstance(time, datetime):
                    time = datetime.now()

                if robot_name not in self.data_collection.data:
                    self.data_collection.data[robot_name] = dict()

                if var_name not in self.data_collection.data[robot_name]:
                    self.data_collection.data[robot_name][var_name] = [(val, time)]

                self.data_collection.data[robot_name][var_name].append((val, time))


    def __get_element(self, robot_name: str, var_name: str, index='all', return_type=0, ):

        if not isinstance(robot_name, str):
            raise TypeError("Robot name must be a String")
        if not isinstance(var_name, str):
            raise TypeError("Variable name must be a String")

        if robot_name not in self.data_collection.data:
            raise KeyError("%s does not exist" % robot_name)

        if var_name not in self.data_collection.data[robot_name]:
            raise KeyError("Variable %s does not exist in %s!" % (var_name, robot_name))

        if isinstance(index, int):
            if index >= len(self.data_collection.data[robot_name][var_name]):
                return None

            return self.data_collection.data[robot_name][var_name][index][return_type]

        elif isinstance(index, tuple) and len(index) == 2:
            return self.data_collection.data[robot_name][var_name][index[0]:index[1]][return_type]

        else:
            return self.data_collection.data[robot_name][var_name]


    def get_element_val(self, robot_name: str, var_name: str, index: int=-1):
        return self.__get_element(robot_name, var_name, index, 0)

    def get_element_time(self, robot_name: str, var_name: str, index: int=-1):
        return self.__get_element(robot_name, var_name, index, 1)

    def get_data(self, robot_name: str, var_name: str):
        return self.__get_element(robot_name, var_name, index='all')
