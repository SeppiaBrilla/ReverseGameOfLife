import subprocess
import json

class SingleStateModel:
    MODEL = "src/models/single_state_model.mzn"

    def make_instance(self, board: list[list[int]], instance_name:str) -> None:
        n = len(board)
        m = len(board[0])
        board_lines = [ ", ".join([str(v) for v in board[i]]) for i in range(len(board)) ]
        board_str = "[| " + " |\n\t     ".join(board_lines) + " |]"
        instance = f"""
    n = {n};
    m = {m};
    current = {board_str};
    """
        f = open(instance_name, "w")
        f.write(instance)
        f.close()

    def call_minizinc(self, instance:str = "", all_solutions:bool = True, time_limit:int|None = None) -> list[dict]:
        command = ["minizinc", "-m", self.MODEL]
        if instance != "":
            command += ["-d", instance]

        command += ["--output-mode", "json"]

        if all_solutions:
            command.append("-a")

        if time_limit is not None:
            command += ["--time-limit", str(time_limit)]

        command += ["-p", '12']
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode("utf-8")

        if "=====UNSATISFIABLE=====" in result:
            return []

        try:
            solutions = result.replace("==========", "").replace("\n","").split("----------")
            return [json.loads(sol) for sol in solutions if sol != ""]
        except json.JSONDecodeError as _:
            raise Exception(result)

class MultiStateModel:
    MODEL = "src/models/multi_states_model.mzn"

    def make_instance(self, board: list[list[int]], number_of_states:int, instance_name:str) -> None:
        n = len(board)
        m = len(board[0])
        board_lines = [ ", ".join([str(v) for v in board[i]]) for i in range(len(board)) ]
        board_str = "[| " + " |\n\t     ".join(board_lines) + " |]"
        instance = f"""
    n = {n};
    m = {m};
    steps = {number_of_states};
    current = {board_str};
    """
        f = open(instance_name, "w")
        f.write(instance)
        f.close()

    def call_minizinc(self, instance:str = "", all_solutions:bool = True, time_limit:int|None = None) -> list[dict]:
        command = ["minizinc", "-m", self.MODEL]
        if instance != "":
            command += ["-d", instance]

        command += ["--output-mode", "json"]

        if all_solutions:
            command.append("-a")

        if time_limit is not None:
            command += ["--time-limit", str(time_limit)]
        command += ["-p", '12']

        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode("utf-8")

        if "=====UNSATISFIABLE=====" in result:
            return []

        try:
            solutions = result.replace("==========", "").replace("\n","").split("----------")
            return [json.loads(sol) for sol in solutions if sol != ""]
        except json.JSONDecodeError as _:
            raise Exception(result)


if __name__ == "__main__":
    solutions = SingleStateModel().call_minizinc()
    print(f"number of solutions: {len(solutions)}")
