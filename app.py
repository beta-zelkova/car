# app.py
from flask import Flask, render_template, request, jsonify
import csv
import heapq
from collections import defaultdict

app = Flask(__name__)

def load_data_from_csv(path):
    graph = defaultdict(list)
    with open(path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            graph[row['from']].append({
                'for': row['to'],
                'time': int(row['time']),
                'cost': int(row['cost'])
            })
    return graph

# 経路探索ロジック
def min_time(graph, start, goal):
    heap = [(0, start, [])]
    visited = {}
    while heap:
        current_time, station, path_so_far = heapq.heappop(heap)
        if station in visited:
            continue
        visited[station] = current_time
        current_path = path_so_far + [station]
        if station == goal:
            return current_time, current_path
        for edge in graph.get(station, []):
            heapq.heappush(heap, (current_time + edge['time'], edge['for'], current_path))
    return float('inf'), []

def min_cost(graph, start, goal):
    heap = [(0, start, [start])]
    visited = {}
    while heap:
        current_cost, station, path_so_far = heapq.heappop(heap)
        if station in visited:
            continue
        visited[station] = current_cost
        if station == goal:
            return current_cost, path_so_far
        for edge in graph.get(station, []):
            new_path = path_so_far + [edge['for']]
            heapq.heappush(heap, (current_cost + edge['cost'], edge['for'], new_path))
    return float('inf'), []

def find_all_routes(graph, selected_stations):
    results = []
    for i in range(len(selected_stations)):
        for j in range(i+1, len(selected_stations)):
            s, g = selected_stations[i], selected_stations[j]
            t, tpath = min_time(graph, s, g)
            c, cpath = min_cost(graph, s, g)
            results.append({
                'from': s,
                'to': g,
                'min_time': t,
                'time_path': tpath,
                'min_cost': c,
                'cost_path': cpath
            })
    return results

@app.route('/')
def index():
    graph = load_data_from_csv('data.csv')
    stations = sorted(graph.keys())
    return render_template('car.html', stations=stations)

@app.route('/search', methods=['POST'])
def search():
    selected_stations = request.json.get('stations', [])
    graph = load_data_from_csv('data.csv')
    results = find_all_routes(graph, selected_stations)
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
