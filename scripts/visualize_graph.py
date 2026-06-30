
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.graph import build_graph

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_OUTPUT_PATH = os.path.join(_BASE_DIR, "results", "graph.png")


def main():
    graph = build_graph()
    png_bytes = graph.get_graph().draw_mermaid_png()
    os.makedirs(os.path.dirname(_OUTPUT_PATH), exist_ok=True)
    with open(_OUTPUT_PATH, "wb") as f:
        f.write(png_bytes)
    print(f"Graph visualization saved to {_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
