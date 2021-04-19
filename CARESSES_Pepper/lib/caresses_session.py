# -*- coding: utf-8 -*-
import qi
import sys
import caresses_app

sys.path.append("/data/home/red-hot-chili-pepper/.local/share/PackageManager/apps/caresses/lib")

def main():
    # Create NAOqi session
    robot_ip = "localhost"
    robot_port = "9559"
    try:
        # Initialize qi framework.
        session = qi.Session()
        session.connect("tcp://%s:%s" % (robot_ip, robot_port))
        print("\nConnected to Naoqi at ip '%s' on port '%s'.\n" % (robot_ip, robot_port))

    except RuntimeError:
        print ("Can't connect to Naoqi at ip '%s' on port '%s'.\nPlease check your script arguments. Run with -h option for help." % (robot_ip, robot_port))
        sys.exit(1)

    robot = caresses_app.CARESSES(session)
    robot.run()
    session.close()


if __name__ == '__main__':
    main()
