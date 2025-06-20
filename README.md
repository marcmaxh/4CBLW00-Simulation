To run the various simulations in this project, you pass arguments 1, 2, or 3 when running main.py

First, navigate in your terminal to the root directory of this project (the one which contains main.py)
Next, type 'python main.py x' with x being 1, 2, or 3, based on which simulation you want to run, see details below.

main.py 1 runs the GUI where the user can select details on what transportation they want to simulate and the specifications of the trip. This is the transportation mode simulation
main.py 2 runs the randomised trip generation of the transportation mode simulation which generates 10000 random trips and compares their results to show differences between fatbikes, cars, and buses.
main.py 3 runs the real-time discrete event simulation that simulates a full day of our service being provided with a probabilistic based function to generate trips at each minute of the day.
