import math
import multiprocessing
import os
import random
from concurrent.futures import ProcessPoolExecutor
from itertools import permutations
from time import perf_counter


# False: up to 12 pizzerias. True: up to 50 pizzerias.
USE_LARGE_DATA = True

# Original data for up to 12 pizzerias.
LOCAL_TIMES = [
    [0, 7, 10, 9, 10, 10, 14, 13, 14, 18, 18, 15, 22],
    [7, 0, 7, 13, 17, 15, 15, 9, 7, 24, 20, 22, 21],
    [10, 7, 0, 10, 17, 19, 22, 15, 10, 27, 14, 21, 27],
    [9, 13, 10, 0, 10, 16, 22, 21, 18, 22, 10, 11, 30],
    [10, 17, 17, 10, 0, 9, 18, 21, 23, 12, 18, 7, 27],
    [10, 15, 19, 16, 9, 0, 10, 17, 22, 9, 25, 15, 19],
    [14, 15, 22, 22, 18, 10, 0, 11, 19, 16, 31, 25, 10],
    [13, 9, 15, 21, 21, 17, 11, 0, 9, 25, 28, 28, 13],
    [14, 7, 10, 18, 23, 22, 19, 9, 0, 30, 23, 28, 22],
    [18, 24, 27, 22, 12, 9, 16, 25, 30, 0, 30, 17, 24],
    [18, 20, 14, 10, 18, 25, 31, 28, 23, 30, 0, 17, 39],
    [15, 22, 21, 11, 7, 15, 25, 28, 28, 17, 17, 0, 34],
    [22, 21, 27, 30, 27, 19, 10, 13, 22, 24, 39, 34, 0],
]
LOCAL_READY = [0, 0, 12, 0, 25, 8, 35, 0, 20, 30, 22, 18, 28]

if USE_LARGE_DATA:
    from pizza_data import TIMES, READY
else:
    TIMES = LOCAL_TIMES
    READY = LOCAL_READY

SIZES = [4, 6, 8, 9, 10, 11, 30, 50]
RUNS = 10
ITERATIONS = 10000
START_TEMPERATURE = 20.0
END_TEMPERATURE = 0.1
PARALLEL_WORKERS = os.cpu_count() or 1


def route_time(route, times, ready):
    time = 0
    previous = 0
    for pizzeria in route:
        arrival = time + times[previous][pizzeria]
        time = max(arrival, ready[pizzeria])
        previous = pizzeria
    return time + times[previous][0]


def cost(routes, times, ready):
    longest_time = 0
    for route in routes:
        time = route_time(route, times, ready)
        if time > longest_time:
            longest_time = time
    return longest_time


def brute_force(times, ready):
    return search_orders(permutations(range(1, len(times))), times, ready)


def search_orders(orders, times, ready):
    n = len(times) - 1
    best_routes = None
    best_cost = math.inf
    for order in orders:
        for split in range(n + 1):
            routes = [list(order[:split]), list(order[split:])]
            value = cost(routes, times, ready)
            if value < best_cost:
                best_routes, best_cost = routes, value
    return best_routes, best_cost


def search_part(task):
    prefix, times, ready = task
    remaining = [node for node in range(1, len(times)) if node not in prefix]
    orders = (prefix + tail for tail in permutations(remaining))
    return search_orders(orders, times, ready)


def brute_force_parallel(times, ready, workers=PARALLEL_WORKERS):
    if workers < 1:
        raise ValueError("workers must be positive")
    n = len(times) - 1
    if workers == 1 or n < 2:
        return brute_force(times, ready)
    tasks = [(prefix, times, ready)
             for prefix in permutations(range(1, n + 1), 2)]
    with ProcessPoolExecutor(max_workers=min(workers, len(tasks)),
                             mp_context=multiprocessing.get_context("spawn")) as pool:
        return min(pool.map(search_part, tasks), key=lambda result: result[1])


def neighbor(routes, rng):
    result = []
    for route in routes:
        result.append(route.copy())

    positions = []
    for car in range(2):
        for i in range(len(result[car])):
            positions.append((car, i))
    if not positions:
        return result
    car, i = rng.choice(positions)
    pizzeria = result[car].pop(i)
    target = rng.randrange(2)
    position = rng.randrange(len(result[target]) + 1)
    result[target].insert(position, pizzeria)
    return result


def simulated_annealing(times, ready, seed=0):
    rng = random.Random(seed)
    order = list(range(1, len(times)))
    rng.shuffle(order)
    split = len(order) // 2
    current = [order[:split], order[split:]]
    current_cost = cost(current, times, ready)
    best_routes = []
    for route in current:
        best_routes.append(route.copy())
    best_cost = current_cost

    for step in range(ITERATIONS):
        progress = step / max(1, ITERATIONS - 1)
        temperature = START_TEMPERATURE * (END_TEMPERATURE / START_TEMPERATURE) ** progress
        candidate = neighbor(current, rng)
        candidate_cost = cost(candidate, times, ready)
        delta = candidate_cost - current_cost

        if delta <= 0 or rng.random() < math.exp(-delta / temperature):
            current, current_cost = candidate, candidate_cost
            if current_cost < best_cost:
                best_routes = []
                for route in current:
                    best_routes.append(route.copy())
                best_cost = current_cost

    return best_routes, best_cost


def check_routes(routes, n):
    assert len(routes) == 2
    assert sorted(routes[0] + routes[1]) == list(range(1, n + 1))


def show_routes(routes, times, ready):
    for car, route in enumerate(routes, 1):
        path = " -> ".join(map(str, [0] + route + [0]))
        print(f"  Car {car}: {path}; return time: {route_time(route, times, ready)} min")


def get_example(n):
    maximum = min(len(TIMES), len(READY)) - 1
    if not 1 <= n <= maximum:
        raise ValueError(f"Requested {n} pizzerias, but data is available for 1 to {maximum}. Update SIZES or extend TIMES and READY.")
    times = [row[:n + 1] for row in TIMES[:n + 1]]
    if any(len(row) != n + 1 for row in times):
        raise ValueError(f"The travel-time matrix is incomplete for {n} pizzerias.")
    return times, READY[:n + 1]


def run_sa_runs(times, ready, optimum=None):
    n = len(times) - 1
    values, durations = [], []
    best_routes, best_value = None, math.inf
    print("SA: seed | result (min) | gap (%) | computation time (s)")
    for seed in range(RUNS):
        started = perf_counter()
        routes, value = simulated_annealing(times, ready, seed)
        elapsed = perf_counter() - started
        check_routes(routes, n)
        assert value == cost(routes, times, ready)
        values.append(value)
        durations.append(elapsed)
        if value < best_value:
            best_routes, best_value = routes, value

        gap_text = "N/A"
        if optimum is not None:
            assert value >= optimum
            gap = 100 * (value - optimum) / optimum if optimum else 0
            gap_text = f"{gap:.2f}"
        print(f"    {seed:2} | {value:15} | {gap_text:>14} | {elapsed:.6f}")

    mean = sum(values) / RUNS
    print(f"SA: best {min(values)} min; mean {mean:.2f} min; worst {max(values)} min.")
    if optimum is not None:
        print(f"Optimum found in {values.count(optimum)}/{RUNS} runs.")
    print(f"Mean SA computation time: {sum(durations) / RUNS:.6f} s.")
    print("Best SA routes:")
    show_routes(best_routes, times, ready)


def run_sa_only():
    for n in SIZES:
        get_example(n)
    print("SA only: two cars, order readiness times included.")
    print(f"SA: {RUNS} runs, seeds 0..{RUNS - 1}, {ITERATIONS} iterations.")
    print(f"Temperature: {START_TEMPERATURE} -> {END_TEMPERATURE} min.")
    print("The exact optimum is not computed; gap is shown as N/A.")
    for n in SIZES:
        times, ready = get_example(n)
        print(f"\n--- {n} pizzerias: starting SA only ---", flush=True)
        run_sa_runs(times, ready)


def run_brute_force_and_sa():
    for n in SIZES:
        get_example(n)
    print("Brute force and SA:")
    print(f"SA: {RUNS} runs, seeds 0..{RUNS - 1}, {ITERATIONS} iterations.")
    print(f"Temperature: {START_TEMPERATURE} -> {END_TEMPERATURE} min.")
    print(f"Brute force for 8 or more pizzerias: {PARALLEL_WORKERS} processes (1 = sequential).")
    for n in SIZES:
        times, ready = get_example(n)

        print(f"\n--- {n} pizzerias: starting brute force ---", flush=True)
        started = perf_counter()
        if n >= 8 and PARALLEL_WORKERS > 1:
            exact_routes, optimum = brute_force_parallel(times, ready, PARALLEL_WORKERS)
        else:
            exact_routes, optimum = brute_force(times, ready)
        exact_seconds = perf_counter() - started
        check_routes(exact_routes, n)
        print(f"Brute force: {math.factorial(n) * (n + 1):,} candidates; "
              f"optimum {optimum} min; computation time {exact_seconds:.6f} s.")
        show_routes(exact_routes, times, ready)

        run_sa_runs(times, ready, optimum)


if __name__ == "__main__":
    run_sa_only() #SA only
    # run_brute_force_and_sa() #SA and brute force
