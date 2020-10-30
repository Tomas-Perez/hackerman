import angr
import claripy

SIZE = 0x1d

proj = angr.Project("./prodkey")

chars = [claripy.BVS(f'c{i}', 8) for i in range(SIZE)]
input_str = claripy.Concat(*chars + [claripy.BVV(b'\n')]) # + \n
initial_state = proj.factory.entry_state(stdin=input_str) # use as stdin

for c in chars: # make sure all chars are printable
    initial_state.solver.add(c >= 0x20, c <= 0x7e)

simgr = proj.factory.simulation_manager(initial_state)

simgr.explore(find=0x00400e58)

if simgr.found:
    s = simgr.found[0].solver
    possible_key = []

    for c in chars:
        possible_key.append(chr(s.eval(c)))

    print(possible_key)
    print("".join(possible_key))M4@@9-8  7@-@ @9@-6@BB2-@@@88