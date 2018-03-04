import os
import logging
import settings
import time


class Telemetry(object):
    """Telemetry class for pi-o-steer"""

    def __init__(self, name, ext):
        super(Telemetry, self).__init__()
        self.name = name
        self.runId = time.time()
        # log_namespace can be replaced with your namespace
        logger = logging.getLogger('piosteer.%s' % name)
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            # usually I keep the LOGGING_DIR defined in some global settings file
            fileName = str(self.runId) + self.name + "." + ext
            print('Logging telemetry at:' + fileName)
            file_name = os.path.join("./logs", fileName)
            handler = logging.FileHandler(file_name)
            formatter = logging.Formatter(
                '%(asctime)s,%(levelname)s,%(message)s')
            handler.setFormatter(formatter)
            handler.setLevel(logging.INFO)
            logger.addHandler(handler)

        self._logger = logger

    def get(self):
        return self._logger
