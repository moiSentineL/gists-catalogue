# 20240622-checkin-gist

**Gist file**: [https://gist.github.com/moiSentineL/3f34d12442c1db6f5328ef83c551402b](https://gist.github.com/moiSentineL/3f34d12442c1db6f5328ef83c551402b)

**Description**: Hourly Check-in for productivity on Linux using native notify-send. Plays sound as well using paplay. 

## checkin.sh

```Shell
#!/bin/bash

# Array of random messages
messages=(
    "Are you being productive?"
    "What are you working on?"
    "Stay focused and keep working!"
    "How's your progress?"
    "Are you working on what you planned for?"
)

while true; do
    # Select a random message from the array
    random_message=${messages[$RANDOM % ${#messages[@]}]}

    # Send notification with the random message
    notify-send "Hourly Check-in" "$random_message" -u critical

    # Play notification sound
    paplay ~/.local/notif.mp3

    # Wait for 1 hour (3600 seconds)
    sleep 3600
done

```