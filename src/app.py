from flask import Flask, request, jsonify, render_template
from models.sat_model import reverse_gol
from minizinc import SingleStateModel, MultiStateModel
from gol import forward
import os

def depth_first_search(board:list[list[int]], max_steps:int) -> tuple[list[list[list[int]]], bool]:
    model = SingleStateModel()
    model.make_instance(board, ".cache/current_instance.dzn")
    next_states = [state["previous"] for state in model.call_minizinc(".cache/current_instance.dzn")]
    if max_steps == 1 and len(next_states) >= 1:
        for state in next_states:
            assert forward(state) == board, "the board is not consistent"
        return next_states, True
    for state in next_states:
        assert forward(state) == board, "the board is not consistent"
        states = depth_first_search(state, max_steps - 1)
        if states[1]:
            return states

    return [], False

def multi_states_solve(board:list[list[int]], max_steps:int) -> tuple[list[list[list[int]]], bool]:
    model = MultiStateModel()
    model.make_instance(board, max_steps, ".cache/current_instance.dzn")
    solutions = model.call_minizinc(".cache/current_instance.dzn", all_solutions=False)
    solutions = [s["previous"] for s in solutions]
    for solution in solutions:
        for step in range(len(solution)):
            if step == len(solution) - 1:
                assert forward(solution[step]) == board, "the board is not consistent"
            else:
                assert forward(solution[step]) == solution[step + 1], "the board is not consistent"
    
    return solutions, len(solutions) > 0

def sat_model(board, max_step):
    solutions, sat = reverse_gol(board, max_step)
    if not sat:
        return [], False
    for step in range(len(solutions)):
        if step == len(solutions) - 1:
            assert forward(solutions[step]) == board, "the board is not consistent"
        else:
            assert forward(solutions[step]) == solutions[step + 1], "the board is not consistent"
    
    return [solutions], True

app = Flask(__name__)

# Root endpoint
@app.route('/')
def root():
    return render_template('index.html')

# Matrix endpoint
@app.route('/reverse', methods=['POST'])
def process_matrix():
    try:
        # Get JSON data from the request
        data = request.get_json()
        method = data["method"]
        state = data["state"]
        steps = data["steps"]

        solver = None
        if method == "single":
            solver = depth_first_search
        elif method == "multi":
            solver = multi_states_solve
        elif method == "SAT":
            solver = sat_model
            
        solution, success = solver(state, steps)
        
        return jsonify({"success": success, "solution": solution}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    if not os.path.exists(".cache"):
        os.makedirs(".cache")
    app.run(debug=True)
