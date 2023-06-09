from ag import *
from qiskit.circuit import QuantumCircuit
from vf2q import VF2Q

import os
import time

if __name__ == "__main__":

    """
    Noticeable findings:
    o------CIRCUIT------o-------VF2Q-------o------RX-VF2------o
    | 54QBT_05CYC_QSE_0 | pass (< 5s)      | pass (< 1s)      |
    | 54QBT_05CYC_QSE_2 | pass (< 1s)      | pass (< 1s)      |
    | 54QBT_05CYC_QSE_3 | pass (< 1s)      | timeout^         |
    | 54QBT_05CYC_QSE_5 | pass (< 1s)      | pass (< 100s)    |
    | 54QBT_05CYC_QSE_7 | pass (< 5s)      | pass (< 1s)      |
    | 54QBT_05CYC_QSE_9 | pass (< 1s)      | pass (< 300s)    |
    | 54QBT_10CYC_QSE_0 | pass (< 10s)     | pass (< 1s)      |
    o-------------------o------------------o------------------o
    ^did not halt within 600 seconds.
    """

    path = "./benchmark/BNTF/"

    max_vf2_runtime = [-1., None]
    max_vf2pp_runtime = [-1., None]
    total_vf2_runtime = 0.
    total_vf2pp_runtime = 0.
    num_files = 0

    INCLUDE_VF2PP = True # Toggle this to include VF2++
    INCLUDE_RXVF2 = False # Toggle this to include rustworkx's VF2
    VERIFY_MAPPING = True # Toggle this to enable/disable VF2PP mapping verification
    PRINT_MAPPING = False # Toggle this to print mappings
    
    for filename in os.listdir(path):
        
        # if filename != "54QBT_05CYC_QSE_0.qasm": continue
        # if filename != "54QBT_05CYC_QSE_2.qasm": continue
        # if filename != "54QBT_05CYC_QSE_3.qasm": continue
        # if filename != "54QBT_05CYC_QSE_5.qasm": continue
        # if filename != "54QBT_05CYC_QSE_7.qasm": continue
        # if filename != "54QBT_05CYC_QSE_9.qasm": continue
        # if filename != "54QBT_10CYC_QSE_0.qasm": continue

        print(filename)
        
        circuit = QuantumCircuit.from_qasm_file(path + filename)
        vf2pp = VF2Q(circuit, sycamore54())

        if INCLUDE_RXVF2:
            
            start = time.time()
            is_embeddable = rx.is_subgraph_isomorphic(vf2pp.archgraph, vf2pp.circgraph, induced=False)
            end = time.time()
            if (end - start) > max_vf2_runtime[0]:
                max_vf2_runtime[0] = (end - start)
                max_vf2_runtime[1] = filename
            total_vf2_runtime += (end - start)
            print(f"rx-vf2_runtime: {end - start}")

            if is_embeddable:
                vf2_map = rx.vf2_mapping(vf2pp.archgraph, vf2pp.circgraph, subgraph=True, induced=False)
                print("rx-vf2_embeddable: True")
                if PRINT_MAPPING:
                    print(f"rx-vf2_mapping: {next(vf2_map)}")
            else:
                print("rx-vf2_embeddable: False")

        if INCLUDE_VF2PP:

            start = time.time()
            vf2pp.match_all(nmap_limit=1)
            end = time.time()
            if (end - start) > max_vf2pp_runtime[0]:
                max_vf2pp_runtime[0] = (end - start)
                max_vf2pp_runtime[1] = filename
            total_vf2pp_runtime += (end - start)
            print(f"vf2-pp_runtime: {end - start}")

            if vf2pp.is_embeddable():
                vf2pp_map = next(vf2pp.mappings())
                print("vf2-pp_embeddable: True")
                if PRINT_MAPPING:
                    print(f"vf2pp_mapping: {vf2pp_map}")
                if VERIFY_MAPPING and not vf2pp.verify(vf2pp_map):
                    raise ValueError("vf2-pp: mapping is invalid")
            else:
                print("vf2-pp_embeddable: False")

            if INCLUDE_RXVF2:
                assert vf2pp.is_embeddable() == is_embeddable, "Conflicting results"
        
        num_files += 1
        print()
    
    if INCLUDE_RXVF2:
        print(f"rx-vf2_max_runtime: {max_vf2_runtime[0]} ({max_vf2_runtime[1]})")
        print(f"rx-vf2_ttl_runtime: {total_vf2_runtime}")
        print(f"rx-vf2_avg_runtime: {total_vf2_runtime / num_files}")
        print()
    
    print(f"vf2-pp_max_runtime: {max_vf2pp_runtime[0]} ({max_vf2pp_runtime[1]})")
    print(f"vf2-pp_ttl_runtime: {total_vf2pp_runtime}")
    print(f"vf2-pp_avg_runtime: {total_vf2pp_runtime / num_files}")
