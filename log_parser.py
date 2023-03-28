import re

def parse_log(log_file):
    # Regular expression to match log lines
    log_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),(\d+),(\w+),(.*)'

    # Dictionary to store parsed log data
    log_data = {
        'timestamps': [],
        'ids': [],
        'levels': [],
        'messages': []
    }

    # Open log file and read each line
    with open(log_file, 'r') as f:
        for line in f:
            # Use regular expression to match log line
            match = re.match(log_pattern, line.strip())
            if match:
                # Extract data from log line and add to dictionary
                timestamp = match.group(1)
                log_data['timestamps'].append(timestamp)

                id = int(match.group(2))
                log_data['ids'].append(id)

                level = match.group(3)
                log_data['levels'].append(level)

                message = match.group(4)
                log_data['messages'].append(message)

    return log_data

log_file = 'example.log'
log_data = parse_log("test.log")
print(log_data)
