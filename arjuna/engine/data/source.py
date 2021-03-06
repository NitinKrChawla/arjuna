'''
This file is a part of Arjuna
Copyright 2015-2020 Rahul Verma

Website: www.RahulVerma.net

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import abc
import threading
import types

from arjuna.core.reader.excel import *
from arjuna.core.reader.ini import *
from arjuna.core.reader.textfile import *
from arjuna.core.thread import decorators
from arjuna.core.exceptions import *
from arjuna.core.types import constants
from arjuna.engine.data.record import *
# from arjuna.core.utils import sys_utils

class DataSource(metaclass=abc.ABCMeta):
    def __init__(self):
        super().__init__()
        self.lock = threading.RLock()
        self.name = None
        self.ended = False

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    @decorators.sync_method('lock')
    def terminate(self):
        self.ended = True

    def is_terminated(self):
        return self.ended

    def validate(self):
        pass

    @decorators.sync_method('lock')
    def next(self):
        if self.is_terminated():
            raise DataSourceFinished()

        try:
            data_record = self.get_next()
            if not data_record:
                raise StopIteration()
            record = self.process(data_record)
            if self.should_exclude(record):
                return self.next()
            else:
                return record
        except StopIteration:
            raise DataSourceFinished("Records Finished.")
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise DataSourceFinished(
                "Problem happened in getting next record. No further records would be provided.")

    def process(self, data_record):
        return data_record

    @abc.abstractmethod
    def get_next(self):
        pass

    @abc.abstractmethod
    def should_exclude(self, data_record):
        return False

    @abc.abstractmethod
    def reset(self):
        pass

    @property
    def all_records(self):
        out = []
        while True:
            try:
                record = self.next() #.record
                out.append(record)
            except DataSourceFinished as e:
                # print(e)
                # import traceback
                # traceback.print_exc()
                break
        return out


class FileDataSource(DataSource, metaclass=abc.ABCMeta):
    def __init__(self, path):
        super().__init__()
        self.__path = path
        self.__reader = None

    @property
    def path(self):
        return self.__path

    @property
    def reader(self):
        return self.__reader

    @reader.setter
    def reader(self, reader):
        self.__reader = reader

    def get_next(self):
        return self.reader.next()

    def should_exclude(self, data_record):
        return False

    def reset(self):
        self._load_file()

    @abc.abstractmethod
    def _load_file(self):
        pass


class DsvFileListDataSource(FileDataSource):
    def __init__(self, path, delimiter="\t"):
        super().__init__(path)
        self.__delimiter = delimiter
        self._load_file()

    def process(self, data_record):
        return ListDataRecord(data_record)

    def _load_file(self):
        self.reader = FileLine2ArrayReader(self.path, self.__delimiter)


class DsvFileMapDataSource(FileDataSource):
    def __init__(self, path, delimiter="\t"):
        super().__init__(path)
        self.__delimiter = delimiter
        self._load_file()

    def process(self, data_record):
        return MapDataRecord(data_record)

    def _load_file(self):
        self.reader = FileLine2MapReader(self.path, self.__delimiter)


class IniFileDataSource(FileDataSource):
    def __init__(self, path):
        super().__init__(path)
        if path.lower().endswith("ini"):
            self._load_file()
        else:
            raise Exception("Unsupported file extension for Ini reading.")

    def process(self, data_record):
        return MapDataRecord(data_record)

    def _load_file(self):
        self.reader = IniFile2MapReader(self.path)


class ExcelFileListDataSource(FileDataSource):
    def __init__(self, path):
        super().__init__(path)
        if path.lower().endswith("xls"):
            self._load_file()
        else:
            raise Exception("Unsupported file extension for Excel reading.")

    def _load_file(self):
        self.reader = ExcelRow2ArrayReader(self.path)

    def should_exclude(self, data_record):
        return False

    def process(self, data_record):
        return ListDataRecord(data_record)


class ExcelFileMapDataSource(FileDataSource):
    def __init__(self, path):
        super().__init__(path)
        if path.lower().endswith("xls"):
            self._load_file()
        else:
            raise Exception("Unsupported file extension for Excel reading.")

    def _load_file(self):
        self.reader = ExcelRow2MapReader(self.path)

    def should_exclude(self, data_record):
        return data_record.should_exclude()

    def process(self, data_record):
        return MapDataRecord(data_record)



class DummyDataSource(DataSource):
    MR = DataRecord()

    def __init__(self):
        super().__init__()
        self.done = False

    def get_next(self):
        if self.done:
            raise DataSourceFinished()
        else:
            self.done = True
            return DummyDataSource.MR

    def should_exclude(self, data_record):
        return False


class SingleDataRecordSource(DataSource):
    def __init__(self, record):
        super().__init__()
        self.record = record
        self.done = False

    def get_next(self):
        if not self.is_terminated() and not self.done:
            self.done = True
            return self.record
        else:
            raise DataSourceFinished()

    def should_exclude(self, data_record):
        return False

    def reset(self):
        pass


class DataArrayDataSource(DataSource):
    def __init__(self, records):
        super().__init__()
        self.records = records
        self.__iter = iter(self.records)

    def get_next(self):
        return next(self.__iter)

    def should_exclude(self, data_record):
        return False


class DataFunctionDataSource(DataSource):
    def __init__(self, func, *vargs, **kwargs):
        super().__init__()
        self.func = func
        self.vargs = vargs
        self.kwargs = kwargs
        try:
            self.__iter = iter(self.func(*self.vargs, **self.kwargs))
        except:
            raise Exception("data_function should return an object that is an iterable.")

    def get_next(self):
        obj = next(self.__iter)
        if isinstance(obj, DataRecord):
            return obj
        elif type(obj) is tuple or type(obj) is list:
            return DataRecord(*obj)
        elif type(obj) is dict:
            return DataRecord(**obj)
        else:
            return DataRecord(obj)

    def terminate(self):
        super().terminate()
        # self.ds.terminate()

    def should_exclude(self, data_record):
        return False


class DataClassDataSource(DataSource):
    def __init__(self, dclass, *vargs, **kwargs):
        super().__init__()
        self.klass = dclass
        self.vargs = vargs
        self.kwargs = kwargs
        try:
            self.__iter = iter(self.klass(*self.vargs, **self.kwargs))
        except:
            raise Exception("data_class should implement Python iteration protocol.")

    def get_next(self):
        obj = next(self.__iter)
        if isinstance(obj, DataRecord):
            return obj
        elif type(obj) is tuple or type(obj) is list:
            return DataRecord(*obj)
        elif type(obj) is dict:
            return DataRecord(**obj)
        else:
            return DataRecord(obj)

    def terminate(self):
        super().terminate()
        # self.ds.terminate()

    def should_exclude(self, data_record):
        return False


class MultiDataSource(DataSource):
    def __init__(self, dsource_defs):
        super().__init__()
        self.dsdefs = dsource_defs
        self.current_dsource = None
        self.def_iter = iter(self.dsdefs)

    def __init_next_source(self):
        try:
            dsdef = next(self.def_iter)
            self.current_dsource = dsdef.build()
        except:
            raise StopIteration()

    def get_next(self):
        if self.current_dsource is None:
            self.__init_next_source()

        try:
            return self.current_dsource.next()
        except StopIteration as e:
            self.__init_next_source()
            return self.get_next()

    def should_exclude(self, data_record):
        return False
