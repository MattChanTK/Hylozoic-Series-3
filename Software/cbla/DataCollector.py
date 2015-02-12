import threading
from datetime import datetime
import queue
from copy import copy

class DataCollection(object):

    def __init__(self):

        self.__data = dict()
        self.creation_date = datetime.now()

        self.index = dict()
        self.index['val'] = 0
        self.index['time'] = 1

    @property
    def data(self):
        return self.__data

    @property
    def type_index(self):
        return self.index

    def append_data(self, robot_name: str, var_name: str, val, time=None):

        if not isinstance(robot_name, str):
            raise TypeError("Robot name must be a String")
        if not isinstance(var_name, str):
            raise TypeError("Variable name must be a String")

        if robot_name not in self.__data:
            self.__data[robot_name] = dict()

        # special cases for setting the labels
        if (var_name == 'actuator_labels' or var_name == 'sensor_labels') and isinstance(val, tuple):
            self.__data[robot_name][var_name] = val
            return

        if not isinstance(time, datetime):
            time = datetime.now()

        # append new data
        if var_name not in self.__data[robot_name]:
            self.__data[robot_name][var_name] = [[copy(val), copy(time)]]
        else:
            self.__data[robot_name][var_name].append([copy(val), copy(time)])

    def set_robot_actuator_labels(self, robot_name, actuator_labels):
        self.append_data(robot_name, 'actuator_labels', actuator_labels)

    def set_robot_sensor_labels(self, robot_name, sensor_labels):
        self.append_data(robot_name, 'sensor_labels', sensor_labels)

    def get_robot_actuator_labels(self, robot_name):
        try:
            return self.__data[robot_name]['actuator_labels']
        except KeyError:
            return None

    def get_robot_sensor_labels(self, robot_name):
        try:
            return self.__data[robot_name]['sensor_labels']
        except KeyError:
            return None

    def get_data_element(self, robot_name: str, var_name: str, index='all', return_type='val'):

        # error checking
        if not isinstance(robot_name, str):
            raise TypeError("Robot name must be a String")
        if not isinstance(var_name, str):
            raise TypeError("Variable name must be a String")

        if robot_name not in self.__data:
            raise KeyError("%s does not exist" % robot_name)

        if var_name not in self.__data[robot_name]:
            raise KeyError("Variable %s does not exist in %s!" % (var_name, robot_name))

        if return_type not in self.type_index.keys():
            raise KeyError("Return Type %s does not exist" % str(return_type))

        # return data in the right format
        if isinstance(index, int):
            if index >= len(self.__data[robot_name][var_name]):
                return None

            return self.__data[robot_name][var_name][index][self.index[return_type]]

        elif isinstance(index, tuple) and len(index) == 2:
            return list(zip(*self.__data[robot_name][var_name][index[0]:index[1]]))[self.index[return_type]]

        elif index == 'all':
            return self.__data[robot_name][var_name]

        elif index == 'all_zip':
            return list(zip(*self.__data[robot_name][var_name]))

        return None


class DataCollector(object):

    def __init__(self, data: DataCollection):

        self.data_q = queue.Queue()
        self.lock = threading.Lock()

        if data is None:
            data = DataCollection()
        if not isinstance(data, DataCollection):
            raise TypeError("Data must be in DataCollection class")
        self.data_collection = data

    @property
    def data(self) -> dict:
        return self.data_collection.data

    @property
    def creation_date(self) -> datetime:
        return self.data_collection.creation_date

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

                self.data_collection.append_data(robot_name, var_name, val, time)


    def __get_element(self, robot_name: str, var_name: str, index='all', return_type='val'):

        return self.data_collection.get_data_element(robot_name, var_name, index, return_type)

    def get_element_val(self, robot_name: str, var_name: str, index=-1):
        return self.__get_element(robot_name, var_name, index, return_type='val')

    def get_element_time(self, robot_name: str, var_name: str, index=-1):
        return self.__get_element(robot_name, var_name, index, return_type='time')

    def get_var_data(self, robot_name: str, var_name: str):
        return self.__get_element(robot_name, var_name, index='all')

    def get_named_var_data(self, robot_name: str, var_name: str):
        named_var_data = dict()
        type_index = self.data_collection.type_index
        var_all_data = self.__get_element(robot_name, var_name, index='all_zip')
        for type, index in type_index.items():
            named_var_data[type] = var_all_data[index]

        return named_var_data


    @property
    def robot_names(self):
        return list(self.data_collection.data.keys())
