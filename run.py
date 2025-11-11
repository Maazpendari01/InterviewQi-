#!/usr/bin/env python
"""
Run script for tech-interview-ai project
"""
import sys
from pathlib import Path

# Add the project root to Python path
root = Path(__file__).resolve().parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Run tech-interview-ai components')
    parser.add_argument('component', choices=['server', 'test-chroma', 'test-connections', 'interview-graph'],
                      help='Component to run')
    args = parser.parse_args()

    if args.component == 'server':
        import uvicorn
        uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
    elif args.component == 'test-chroma':
        from backend.tests import test_chroma
        test_chroma.main()
    elif args.component == 'test-connections':
        from backend.tests import test_connections
        test_connections.main()
    elif args.component == 'interview-graph':
        from backend.app.services.interview_graph import InterviewGraph
        graph = InterviewGraph()
        # Add test code here
        print("Interview graph initialized successfully")