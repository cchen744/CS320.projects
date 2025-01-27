import os, sys, json, csv, re, math, copy
import matplotlib.pyplot as plt
import graphviz
from collections import namedtuple
import subprocess
from pathlib import Path
import module_tester

try:
    sys.path.append(os.path.abspath(".utils"))
    import hardcoding
finally:
    sys.path.pop()

BOLD = "\033[1m"
RESET = "\033[0m"
RED = "\033[31m"

Answer = namedtuple("Answer", ["question", "type", "value", "stream", "notes"])

code = {}

def read_code_cells(ipynb, default_notes={}):
    answers = []
    with open(ipynb) as f:
        nb = json.load(f)
        cells = nb["cells"]
        expected_exec_count = 1
        source_code = []
        for cell in cells:
            if "execution_count" in cell and cell["execution_count"]:
                exec_count = cell["execution_count"]
                if exec_count != expected_exec_count:
                    raise Exception(f"Expected execution count {expected_exec_count} but found {exec_count}. Please do Restart & Run all then save before running the tester.")
                expected_exec_count = exec_count + 1
            if cell["cell_type"] != "code":
                continue
            if not cell["source"]:
                continue
            m = re.match(r"#[qQ](\d+)(.*)", cell["source"][0].strip())
            if not m:
                source_code.extend(cell["source"])
                continue
            qnum = int(m.group(1))
            source_code.extend(cell["source"])
            code[qnum] = copy.deepcopy(source_code) # add all previous code to dict entry for this question
            notes = m.group(2).strip()
            config = parse_question_config(notes)
            if "run" in config:
                exec(config["run"])
            print(f"Reading Question {qnum}")
            if qnum in [a.question for a in answers]:
                raise Exception(f"Answer {qnum} repeated!")
            expected = max([0] + [a.question for a in answers]) + 1
            if qnum != expected:
                print(f"Warning: Expected question {expected} next but found {qnum}!")

            # plots are display_data, so try to find those before looking for regular cell outputs
            outputs = [o for o in cell["outputs"]
                       if o.get("output_type") == "display_data"]
            stdout = ""
            if len(outputs) == 0:
                outputs = [o for o in cell["outputs"]
                           if o.get("output_type") == "execute_result"]
            assert len(outputs) < 2
            if len(outputs) > 0:
                output_str = "".join(outputs[0]["data"]["text/plain"]).strip()
                if output_str.startswith("<Figure"):
                    output_str = "plt.Figure()"
                if output_str.startswith("<") and "Digraph" in output_str:
                    output_str = "graphviz.graphs.Digraph()"
                if output_str == "nan":
                    output_str = 'float("nan")'
            else:
                stream = [o for o in cell["outputs"]
                          if o.get("output_type") == "stream"]
                try:
                    stdout = stream[0]["text"][0].strip()
                except:
                    pass
                output_str = "None"
            try:
                output = eval(output_str)
                if isinstance(output, tuple):
                    type_name = "tuple"
                else:
                    type_name = type(output).__name__
            except NameError as e:
                type_name = "*"
            answers.append(Answer(qnum, type_name, output_str, stdout, notes))
    return answers

def dump_results(ipynb, csv_path, default_notes={}):
    with open(csv_path, "w") as f:
        wr = csv.writer(f)
        wr.writerow(Answer._fields)
        for answer in read_code_cells(ipynb, default_notes):
            wr.writerow(answer)
    print(f"Wrote results to {csv_path}.")

def compare_bool(expected, actual, config={}):
    return (expected == actual, None)

def compare_int(expected, actual, config={}):
    return (expected == actual, None)

def compare_type(expected, actual, config={}):
    return (expected == actual, None)

def compare_float(expected, actual, config={}):
    if math.isnan(expected) and math.isnan(actual):
        return (True, None)
    tolerance = float(config.get("tolerance", 0))
    return (math.isclose(expected, actual, rel_tol=tolerance), None)

def compare_str(expected, actual, config={}):
    if config.get("case") == "any":
        return (expected.upper() == actual.upper(), None)
    return (expected == actual, None)

def compare_list(expected, actual, config={}):
    if config.get("order") == "strict":
        return (expected == actual, None)
    else:
        return (sorted(expected) == sorted(actual), None)

def compare_tuple(expected, actual, config={}):
    return (expected == actual, None)

def compare_set(expected, actual, config={}):
    if config.get("require") == "superset":
        return (len(expected - actual) == 0, None)
    else:
        return (expected == actual, None)

def compare_dict(expected, actual, config={}):
    tolerance = config.get("tolerance", None)

    if tolerance:
        if expected.keys() != actual.keys():
            return (False, None)

        for key in expected.keys():
            if not compare_float(expected[key], actual[key], {"tolerance": tolerance}):
                return (False, None)
                
        return (True, None)

    return (expected == actual, None)

def compare_figure(expected, actual, config={}):
    if type(expected) != type(actual):
        return (False, None)
    
    name = config.get("name", None)
    tolerance = config.get("tolerance", None)
    fig_type = config.get("type", None)
    title = config.get("title", False)
    axis = config.get("axis", False)
    legend = config.get("legend", False)
    text = config.get("text", False)

    assert os.path.isfile(f".pkl/{name}.pkl")
    assert os.path.isfile(f"{name}.pkl")
    
    result = subprocess.run(
        ['python3', 
         '.utils/image_tester.py', 
         f".pkl/{name}.pkl", 
         f"{name}.pkl", 
         fig_type, 
         tolerance, 
         "-t" if title else "", 
         "-ax" if axis else "",
         "-l" if legend else "", 
         "-tx" if text else ""], 
        capture_output=True, 
        text=True)
    
    errors = [error for error in result.stderr.split("\n") if error]
    
    return (result.returncode == 1, errors)

def compare_nonetype(expected, actual, config={}):
    return (type(expected) == type(actual), None)

compare_fns = {
    "bool": compare_bool,
    "int": compare_int,
    "float": compare_float,
    "str": compare_str,
    "list": compare_list,
    "tuple": compare_tuple,
    "set": compare_set,
    "dict": compare_dict,
    "type": compare_type,
    "Figure": compare_figure,
    "Digraph": compare_figure,
    "NoneType": compare_nonetype,
}

def parse_question_config(c):
    if c.startswith("run="):
        return {"run": c[4:]}
    config = {}
    opts = c.split(" ")
    for opt in opts:
        parts = opt.split("=")
        if len(parts) != 2:
            continue
        config[parts[0]] = parts[1].strip()
    return config

def compare_question_stream(expected_stream, actual_stream):
    return expected_stream == actual_stream

def compare(expected_csv, actual_csv):
    result = {"score": 0, "errors": [], "hardcoding": []}
    passing = 0

    with open(expected_csv) as f:
        expected_rows = {int(row["question"]): dict(row) for row in csv.DictReader(f)}
    with open(actual_csv) as f:
        actual_rows = {int(row["question"]): dict(row) for row in csv.DictReader(f)}

    for qnum in sorted(expected_rows.keys()):
        if not qnum in actual_rows:
            continue
        expected = expected_rows[qnum]
        actual = actual_rows[qnum]
        if actual["type"] not in (expected["type"], "*"):
            err = f'Question {qnum}:\n{"-"*15}\nExpected type to be {expected["type"]}, but found {actual["type"]}'
            result["errors"].append(err)
            continue
        if not expected["type"] in compare_fns:
            raise Exception(f'Tester cannot handle type {expected["type"]} on question {qnum}')
        compare_fn = compare_fns[expected["type"]]
        config = parse_question_config(expected["notes"])
        if "run" in config:
            exec(config["run"])
        if expected.get("stream") != "":
            expected_stream = expected["stream"]
            actual_stream = actual["stream"]
            if not compare_question_stream(expected_stream, actual_stream):
                err = f'Question {qnum}: expected output to be "{expected_stream}", but found "{actual_stream}".'
                result["errors"].append(err)
                continue

        # ========================= Check for Hardcoding =========================
        hc = hardcoding.check_hardcoding(code[qnum], expected["value"], expected["type"], qnum)
        if hc:
            err = [
                f"{BOLD}Question {qnum}:{RESET}",
            ]
            err.extend(hc)
            result["hardcoding"].append("\n".join(err))
            continue
        # ========================= Check for Hardcoding =========================

        compare_result = compare_fn(eval(expected["value"]), eval(actual["value"]), config)
        if compare_result[0]:
            passing += 1
        else:
            err = [
                f"{BOLD}Question {qnum}:{RESET}",
            ]
            if not compare_result[1]:
                err.extend([
                    f"EXPECTED: {expected['value']}",
                    f"ACTUAL: {actual['value']}",
                ])
            elif compare_result[1]:
                formatted_errors = "\n".join(compare_result[1])
                err.append(f"ERRORS: {formatted_errors}")
            result["errors"].append("\n".join(err))

    result["missing"] = sorted(set(expected_rows.keys()) - set(actual_rows.keys()))
    score = round(100 * passing / len(expected_rows))
    result["score"] = score
    result["summary"] = f"Result: {passing} of {len(expected_rows)} passed, for a score of {score}%."
    return result

def main():
    if len(sys.argv) != 1:
        print("Usage: python3 tester.py")
        return

    # dump results from this notebook to a summary .csv file
    ipynb = str(Path(__file__).parent.name) + ".ipynb"
    actual_path = ipynb.replace(".ipynb", ".csv").replace(".json", ".csv")
    dump_results(ipynb, actual_path)

    # ========================= Notebook Tests =========================
    expected_path = ipynb.replace(".ipynb", "-key.csv")
    result_notebook = compare(expected_path, actual_path)

    # ========================= Module Tests =========================
    result_module = module_tester.main(False)
    assert result_module["score"] <= 100

    # ========================= Show Results ========================= 
    score = result_notebook["score"] * 0.75 + result_module["score"] * 0.25
    result = {
        "score": score,
        "errors": result_notebook["errors"],
        "module_errors": result_module["errors"],
        "missing": result_notebook["missing"],
        "hardcoding": result_notebook["hardcoding"],
        "summary": f"Result: Score of {score}% as a weighted average of {result_module['score']}% (modules) and {result_notebook['score']}% (notebook)."
    }

    # save results
    result_path = os.path.join(os.path.dirname(ipynb), "test.json")
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)

    if len(result["errors"]) or len(result["missing"]) or len(result["module_errors"]) or len(result["hardcoding"]):
        print("\n" + "="*85 + "\n")

    # show user-friendly summary of test.json
    if len(result["errors"]) or len(result["missing"]) or len(result["module_errors"]):
        print(f"{BOLD}** There were a total of {len(result['errors']) + len(result['module_errors'])} errors and {len(result['missing'])} missing answers **{RESET}\n")
        
    # print notebook errors
    if len(result["errors"]) or len(result["missing"]):
        print(f"\n{BOLD}Notebook:{RESET}") 
        print("-"*20 + "\n")
        if len(result["errors"]):
            for err in result["errors"]:
                print(err)
                print() 
        if len(result["missing"]):
            print(f'{len(result["missing"])} answers not found, for question(s):',
                  ", ".join([str(m) for m in result["missing"]]))
            print()

    if len(result["hardcoding"]):
        print(f"{RED}{BOLD}Hardcoded answers detected. Please avoid directly writing answers in your code.\nIf you believe this is a mistake, feel free to attend office hours for clarification.{RESET}\n")
        for err in result["hardcoding"]:
                print(err)
                print() 
            
    # print module errors
    if len(result["module_errors"]):
        print(f"\n{BOLD}Modules:{RESET}")
        print("-"*20 + "\n")
        for err in result["module_errors"]:
            print(err)
            print()

    print("\n" + "="*85)
    print(f"{BOLD}{result['summary']}{RESET}")
    print("="*85)

if __name__ == '__main__':
     main()
