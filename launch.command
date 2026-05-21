#!/bin/bash
# BiRAGAS · The Three Rights — local launcher
# Double-click this file in Finder to open the presentation.

cd "$(dirname "$0")"
PORT=8765
URL="http://localhost:${PORT}/"

# kill any prior server on this port
lsof -ti tcp:${PORT} 2>/dev/null | xargs kill 2>/dev/null

# open browser, then start server in foreground so closing the terminal stops it
open "$URL"
echo ""
echo "  ╔═══════════════════════════════════════════════════════════════╗"
echo "  ║                                                               ║"
echo "  ║      BiRAGAS · THE THREE RIGHTS                               ║"
echo "  ║      Ayass BioScience · MMXXVI                                ║"
echo "  ║                                                               ║"
echo "  ║      Serving at:  ${URL}                       ║"
echo "  ║                                                               ║"
echo "  ║      Close this Terminal window to stop the server.           ║"
echo "  ║                                                               ║"
echo "  ╚═══════════════════════════════════════════════════════════════╝"
echo ""
python3 -m http.server ${PORT} --bind 127.0.0.1
