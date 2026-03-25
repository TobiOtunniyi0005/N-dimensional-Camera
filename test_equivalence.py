import random
from Working_on_fixed import project_and_rotate as py_project
from Working_on_fixed_numpy import project_and_rotate as np_project

def random_vectors(n, d):
    return [[random.uniform(-1, 1) for _ in range(d)] for _ in range(n)]

def test_project_equivalence():
    vectors = random_vectors(10, 5)
    change_code = [1, 2, 1, 2, 0]
    angle = 37.0

    out_py = py_project(vectors, change_code, angle)
    out_np = np_project(vectors, change_code, angle)

    for a, b in zip(out_py, out_np):
        for x, y in zip(a, b):
            assert abs(x - y) < 1e-6

if __name__ == "__main__":
    test_project_equivalence()
    print("✅ NumPy and Python implementations are equivalent")
