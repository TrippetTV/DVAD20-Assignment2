#!/bin/bash
echo "Killing all Ryu manager processes..."

# Kill Ryu processes
pkill -f ryu-manager

# Kill any remaining Python processes with Ryu
pkill -f "python.*ryu"

echo "Cleanup complete!"

#chmod +x kill_ryu.sh
#./kill_ryu.sh
