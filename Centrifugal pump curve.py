'''Programm for ploting curves of centrifugal pump experimental vs original from manufacturer'''

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d


class CentrifugalPump:
    '''Class containing the basic pump parametars'''
    pi = 3.14

    def __init__(self, diam1=1, diam2=1, enterarea=1, exitarea=1, headlist=[], flowlist=[], rpm=2850):
        # diameter at the entrance of the pump, in milimeters
        self.diam1 = diam1
        # diameter at the exit of the pump, in milimeters
        self.diam2 = diam2
        # surface area of the entrance pipe
        self.enterarea = (CentrifugalPump.pi * (diam1**2) / (1000000)) / 4
        # surface area of the exit pipe
        self.exitarea = (CentrifugalPump.pi * (diam2**2) / (1000000)) / 4
        self.headlist = headlist
        self.flowlist = flowlist
        self.rpm = rpm

    def __str__(self):
        return f"{self.headlist}\n{self.flowlist}"

    def pump_head(self, head):
        # function for creating a list of values for head
        self.headlist.append(head)
        return self.headlist

    def pump_flow(self, flow):
        # function for creating a list of for flow
        self.flowlist.append(flow)
        return self.flowlist

    def ask_for_diametar(self):
        while True:
            try:
                self.diam1 = float(
                    input('Enter the diameter of the pipe at the entrance of the pump [mm]: '))
                self.diam2 = float(
                    input('Enter the diameter of the pipe at the exit of the pump [mm]: '))
            except:
                print("Error. Please enter a number")
                continue
            else:
                return self.diam1, self.diam2
                break

    def ask_for_rpm(self):
        while True:
            try:
                self.rpm = float(
                    input('Enter the RPM for the characteristic curve of the pump [o/min]: '))
            except:
                print("Error. Please enter an whole number!")
                continue
            else:
                return self.rpm
                break


class ExperimentSetup:
    """Class containing the height of preasure measuring devices"""

    def __init__(self, height1=0, height2=0, geo1=0, geo2=0):
        # dimensions for real preasure compesnations
        # entrance of pump (vacuummeter)
        self.height1 = height1
        # exit of pump (manometer)
        self.height2 = height2
        # entrance of pump

    def ask_for_height(self):
        while True:
            try:
                self.height1 = float(
                    input('\nEnter the height of the vacuummeter, above the point of entrance [m]: '))
                self.height2 = float(
                    input('Enter the height of the manometer, above the point of exit [m]: '))
            except:
                print("Error. Please enter a number")
                continue
            else:
                return self.height1, self.height2
                break

    def ask_for_geo(self):
        while True:
            try:
                self.geo1 = float(
                    input('\nEnter the height of the entrance of the pump above a reference plane [m] '))
                self.geo2 = float(
                    input('Enter the height of the exit of the pump above a reference plane [m] '))
            except Exception as e:
                print("Error. Please enter a number")
            else:
                return self.geo1, self.geo2
                break


pump1 = CentrifugalPump()
pump1.ask_for_diametar()
pump1.ask_for_rpm()


while True:
    try:
        print("\n\tMinimum of 3, at least 5 are recommended")
        x = int(input(
            "\nHow many points do you want to enter from the characteristic curve given by the manufacturer: "))
    except:
        print("Please enter an integer")
    else:
        break

print('\tValues shoud be evenly spaced out, and include min and max flow')

while x > 0:
    try:
        flow = float(input('\nValue for flow [m^3/h]: '))
        head = float(input("Value for head [m]: "))
    except:
        print("Please enter a number")
    else:
        x -= 1
        pump1.pump_head(head)
        pump1.pump_flow(flow)

# Default atmospheric presssure = 1 bar
p_atm = 10**5

# Starting condition for while loop
measurement_on = True

# creating lists on which we can append to later
measured_vacuum = []
measured_pressure = []
measured_flow = []
measured_rpm = []

setup1 = ExperimentSetup()
setup1.ask_for_height()
setup1.ask_for_geo()


print("\nTime to enter measurements")
print("\n\tMinimum of 3, at least 5 are recommended")

print("***BE CAREFULL while entering the values, mistakes WILL cause errors during ploting***")
while measurement_on:
    while True:
        try:
            addmeasure = input(
                "\nWould you like to insert another measurement? ")
            addmeasure.lower().startswith('y') or addmeasure.lower().startswith('n')
        except:
            print("Error. Please enter yes or no")
        else:
            break

    if addmeasure.lower()[0] == 'y':
        value1 = float(input("Measured vacuum pressure [bar]: "))
        value2 = float(input("Measured gauge presssure [bar]: "))
        value3 = float(input("Measured flow [l/min]: "))
        value4 = int(input("Measured RPM [o/min]: "))
        # changing the measured values so thay can be used for further calculations
        measured_vacuum.append(
            p_atm - value1 * 10**5 + 1000 * 9.81 * setup1.height1)
        measured_pressure.append(
            p_atm + value2 * 10**5 + 1000 * 9.81 * setup1.height2)
        # m3/h
        measured_flow.append(value3 / 1000 * 60)
        measured_rpm.append(value4)
    else:
        measurement_on = False
        break

print("\nThe values from the measurements, changed for easier calculation:")
print(f"\nAbsolute presssure at entrance [Pa]: {measured_vacuum}")
print(f"Absolut pressure at exit [Pa]: {measured_pressure}")
print(f"Flow [m^3/h]: {measured_flow}")
print(f"RPM [o/min]: {measured_rpm}\n")


# speed at which the fluid is flowing 1 at entance, 2 at exit
speed1 = []
speed2 = []

# Different forms of energy transformed in head [m]
pressure_head = []
speed_head = []
pump1_head = []


# earth acceleration
g = 9.81
# density of water
den = 1000

for num in range(0, len(measured_pressure)):
    speed1.append(measured_flow[num] / (3600 * pump1.enterarea))
    speed2.append(measured_flow[num] / (3600 * pump1.exitarea))
    speed_head.append((speed2[num]**2 - speed1[num]**2) / (2 * g))
    pressure_head.append(
        (measured_pressure[num] - measured_vacuum[num]) / (g * den))
    pump1_head.append(
        pressure_head[num] + speed_head[num] + (setup1.height2 - setup1.height1))
    print(
        f"Pump head is {pump1_head[num]} m for flow of {measured_flow[num]} m^3/h, with {measured_rpm[num]} o/min.")


# converting the gained results to get an experimental curve with the correct rpm
    # using theory of similarity to get a curve with the corresponding rpm
rpm_measured_flow = []
rpm_measured_head = []
for i in range(0, len(pump1_head)):
    rpm_measured_flow.append(measured_flow[i] * pump1.rpm / measured_rpm[i])
    rpm_measured_head.append(
        pump1_head[i] * ((pump1.rpm / measured_rpm[i])**2))

# plot containing the manufacturer curve, experimental points, and experimental curve
list1 = np.array(pump1.flowlist)
list2 = np.array(pump1.headlist)


x_new = np.linspace(list1.min(), list1.max(), 100)
f = interp1d(list1, list2, kind='quadratic')

y_smooth = f(x_new)


list3 = np.array(rpm_measured_flow)
list4 = np.array(rpm_measured_head)

x_new1 = np.linspace(list3.min(), list3.max(), 100)
f_1 = interp1d(list3, list4, kind='quadratic')

y_smooth1 = f_1(x_new1)

plt.plot(x_new, y_smooth)
plt.scatter(list1, list2)

plt.plot(x_new1, y_smooth1)
plt.scatter(list3, list4)

plt.scatter(measured_flow, pump1_head)
plt.show()

print("The blue line and dots represent the curve given by the manufacturer")
print("The green dots represent the exact values of the measurements, plotted to the graph")
print("The orange line and dots represent the curve calculated from the experimental values")
