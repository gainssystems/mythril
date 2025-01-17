from datetime import datetime

import mythril.laser.ethereum.svm as svm
import tests
from mythril.analysis.security import fire_lasers
from mythril.analysis.symbolic import SymExecWrapper
from mythril.disassembler.disassembly import Disassembly
from mythril.ethereum import util
from mythril.laser.ethereum.transaction import execute_contract_creation
from mythril.mythril import MythrilDisassembler
from mythril.solidity.soliditycontract import SolidityContract

solc_binary = MythrilDisassembler._init_solc_binary("v0.5.0")


def test_create():
    contract = SolidityContract(
        str(tests.TESTDATA_INPUTS_CONTRACTS / "calls.sol"), solc_binary=solc_binary
    )

    laser_evm = svm.LaserEVM({})

    laser_evm.time = datetime.now()
    execute_contract_creation(laser_evm, contract.creation_code)

    resulting_final_state = laser_evm.open_states[0]

    for address, created_account in resulting_final_state.accounts.items():
        created_account_code = created_account.code
        actual_code = Disassembly(contract.code)

        for i in range(len(created_account_code.instruction_list)):
            found_instruction = created_account_code.instruction_list[i]
            actual_instruction = actual_code.instruction_list[i]

            assert found_instruction["opcode"] == actual_instruction["opcode"]


def test_sym_exec():
    contract = SolidityContract(
        str(tests.TESTDATA_INPUTS_CONTRACTS / "calls.sol"), solc_binary=solc_binary
    )

    sym = SymExecWrapper(
        contract,
        address=(util.get_indexed_address(0)),
        strategy="dfs",
        execution_timeout=25,
    )
    issues = fire_lasers(sym)

    assert len(issues) != 0
