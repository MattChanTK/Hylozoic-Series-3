import threading
from datetime import datetime
import queue
from copy import copy


class DataCollection(object):

    def __init__(self):

        self.__data = dict()
        self.__creation_date = datetime.now()

        self.__index = dict()
        self.__index['val'] = 0
        self.__index['time'] = 1
        self.__index['step'] = 2

    @property
    def data(self):
        return self.__data

    @property
    def type_index(self):
        return self.__index

    @property
    def creation_date(self):
        return self.__creation_date

    def append_data(self, robot_name: str, var_name: str, val, time=None, step=-1):

        if not isinstance(robot_name, str):
            raise TypeError("Robot name must be a String")
        if not isinstance(var_name, str):
            raise TypeError("Variable name must be a String")

        if robot_name not in self.data:
            self.data[robot_name] = dict()


        if not isinstance(time, datetime):
            time = datetime.now()

        # append new data
        if var_name not in self.data[robot_name]:
            self.data[robot_name][var_name] = [[copy(val), copy(time), copy(step)]]
        else:
            self.data[robot_name][var_name].append([copy(val), copy(time), copy(step)])

    def assign_data(self, robot_name: str, var_name: str, val, time=None, step=-1):

        if not isinstance(robot_name, str):
            raise TypeError("Robot name must be a String")
        if not isinstance(var_name, str):
            raise TypeError("Variable name must be a String")

        if robot_name not in self.data:
            self.data[robot_name] = dict()

        if not isinstance(time, datetime):
            time = datetime.now()

        # assign
        self.data[robot_name][var_name] = [copy(val), copy(time), copy(step)]


    def set_robot_actuator_labels(self, robot_name, actuator_labels):
        if isinstance(actuator_labels, tuple):
            self.assign_data(robot_name, 'actuator_labels', actuator_labels)
        else:
            raise TypeError("Labels have to be in a tuple!")

    def set_robot_sensor_labels(self, robot_name, sensor_labels):
        if isinstance(sensor_labels, tuple):
            self.assign_data(robot_name, 'sensor_labels', sensor_labels)
        else:
            raise TypeError("Labels have to be in a tuple!")


    def get_robot_actuator_labels(self, robot_name):
        try:
            return self.data[robot_name]['actuator_labels'][self.type_index['val']]
        except KeyError:
            return None

    def get_robot_sensor_labels(self, robot_name):
        try:
            return self.data[robot_name]['sensor_labels'][self.type_index['val']]
        except KeyError:
            return None

    def get_data_element(self, robot_name: str, var_name: str, index='all', return_type='val'):

        # error checking
        if not isinstance(robot_name, str):
            raise TypeError("Robot name must be a String")
        if not isinstance(var_name, str):
            raise TypeError("Variable name must be a String")

        if robot_name not in self.data:
            raise KeyError("%s does not exist" % robot_name)

        if var_name not in self.data[robot_name]:
            raise KeyError("Variable %s does not exist in %s!" % (var_name, robot_name))

        if return_type is not None and return_type not in self.type_index.keys():
            raise KeyError("Return Type %s does not exist" % str(return_type))

        # return data in the right format
        if isinstance(index, int):
            if index >= len(self.data[robot_name][var_name]):
                return None
            if return_type is None:
                return self.data[robot_name][var_name][index]
            else:
                return self.data[robot_name][var_name][index][self.type_index[return_type]]

        elif isinstance(index, tuple) and len(index) == 2:
            if return_type is None:
                return list(zip(*self.data[robot_name][var_name][index[0]:index[1]]))
            else:
                return list(zip(*self.data[robot_name][var_name][index[0]:index[1]]))[self.type_index[return_type]]

        elif index == 'all':
            return self.data[robot_name][var_name]

        elif index == 'all_zip':
            return list(zip(*self.data[robot_name][var_name]))

        return None


class DataCollector(object):

    def __init__(self, data: DataCollection=None):

        self.data_q = queue.Queue()
        self.data_q_assign = queue.Queue()
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

    @property
    def type_index(self) -> dict:
        return self.data_collection.type_index

    def enqueue(self, robot_name: str, var_name: str, val, time=None, step=-1):
        self.data_q.put_nowait((copy(robot_name), copy(var_name), copy(val), copy(time), copy(step)))

    def enqueue_assign(self, robot_name: str, var_name: str, val, time=None, step=-1):
        self.data_q_assign.put_nowait((copy(robot_name), copy(var_name), copy(val), copy(time), copy(step)))

    def append(self, max_save=float('inf')):

        with self.lock:

            count = 0
            while not self.data_q.empty() and count < max_save:

                data_package = self.data_q.get()
                robot_name = data_package[0]
                var_name = data_package[1]
                val = data_package[2]
                time = data_package[3]
                step = data_package[4]

                self.data_collection.append_data(robot_name, var_name, val, time, step)
                count += 1

            count = 0
            while not self.data_q_assign.empty() and count < max_save:
                data_package = self.data_q_assign.get()
                robot_name = data_package[0]
                var_name = data_package[1]
                val = data_package[2]
                time = data_package[3]
                step = data_package[4]

                self.data_collection.assign_data(robot_name, var_name, val, time, step)
                count += 1

    def __get_element(self, robot_name: str, var_name: str, index='all', return_type='val'):

        return self.data_collection.get_data_element(robot_name, var_name, index, return_type)

    def get_element_val(self, robot_name: str, var_name: str, index=-1):
        return self.__get_element(robot_name, var_name, index, return_type='val')

    def get_element_time(self, robot_name: str, var_name: str, index=-1):
        return self.__get_element(robot_name, var_name, index, return_type='time')

    def get_element_step(self, robot_name: str, var_name: str, index=-1):
        return self.__get_element(robot_name, var_name, index, return_type='step')

    def get_assigned_element(self, robot_name: str, var_name: str, return_type=None):
        if return_type is not None:
            return self.__get_element(robot_name, var_name, index='all')[self.type_index[return_type]]
        else:
            return self.__get_element(robot_name, var_name, index='all')

    def get_var_data(self, robot_name: str, var_name: str):
        return self.__get_element(robot_name, var_name, index='all')

    def get_named_var_data(self, robot_name: str, var_name: str, max_idx: int=-1):
        named_var_data = dict()
        type_index = self.data_collection.type_index
        var_all_data = self.__get_element(robot_name, var_name, index=(0, max_idx), return_type=None)
        for type, index in type_index.items():
            named_var_data[type] = var_all_data[index]

        return named_var_data


    @property
    def robot_names(self):
        return list(self.data_collection.data.keys())
