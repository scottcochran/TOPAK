#!/bin/bash
# Install TLA+ tools locally to this repository

set -e

TLA_VERSION="v1.7.4"
TLA_JAR="tla2tools.jar"
TOOLS_DIR="tools"

echo "Installing TLA+ tools version $TLA_VERSION..."

# Create tools directory
mkdir -p "$TOOLS_DIR"

# Download tla2tools.jar
echo "Downloading tla2tools.jar..."
curl -L "https://github.com/tlaplus/tlaplus/releases/download/$TLA_VERSION/$TLA_JAR" \
  -o "$TOOLS_DIR/$TLA_JAR"

# Verify download
if [ -f "$TOOLS_DIR/$TLA_JAR" ]; then
  echo "✓ Successfully downloaded $TLA_JAR"
  echo "✓ Installed to: $TOOLS_DIR/$TLA_JAR"
else
  echo "✗ Failed to download $TLA_JAR"
  exit 1
fi

# Create convenience wrapper scripts
cat > tlc << 'EOF'
#!/bin/bash
# TLC wrapper script
java -XX:+UseParallelGC -jar "$(dirname "$0")/tools/tla2tools.jar" "$@"
EOF

cat > tlc-workers << 'EOF'
#!/bin/bash
# TLC wrapper with auto workers (uses all CPU cores)
java -XX:+UseParallelGC -jar "$(dirname "$0")/tools/tla2tools.jar" -workers auto "$@"
EOF

chmod +x tlc tlc-workers

echo ""
echo "✓ Installation complete!"
echo ""
echo "Created convenience scripts:"
echo "  ./tlc          - Run TLC model checker"
echo "  ./tlc-workers  - Run TLC with auto workers (parallel)"
echo ""
echo "Usage examples:"
echo "  ./tlc -parse Paxos.tla"
echo "  ./tlc Paxos.tla -config PaxosSingleNode.cfg"
echo "  ./tlc-workers Paxos.tla -config Paxos.cfg"
echo ""
