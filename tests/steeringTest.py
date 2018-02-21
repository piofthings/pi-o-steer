from app import Telemetry


class SteeringTest(object):
    """docstring for SteeringTest."""

    def __init__(self, arg):
        super(SteeringTest, self).__init__()
        self.arg = arg


def main():
    controller = SteeringTest()
    controller.run()


if __name__ == '__main__':
    main()
