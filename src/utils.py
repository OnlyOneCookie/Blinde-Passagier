import math
from geopy import distance


def calculate_relative_angle(point1, point2, point3):
    vector1 = (point2[0] - point1[0], point2[1] - point1[1])
    vector2 = (point3[0] - point2[0], point3[1] - point2[1])

    dot_product = vector1[0] * vector2[0] + vector1[1] * vector2[1]
    magnitude1 = math.sqrt(vector1[0] ** 2 + vector1[1] ** 2)
    magnitude2 = math.sqrt(vector2[0] ** 2 + vector2[1] ** 2)

    if magnitude1 == 0 or magnitude2 == 0:
        return 0

    cos_angle = dot_product / (magnitude1 * magnitude2)
    cos_angle = max(min(cos_angle, 1), -1)
    angle = math.acos(cos_angle)
    return math.degrees(angle)


def get_turn_instruction(angle):
    if angle < 20:
        return "Continue straight"
    elif angle < 60:
        return "Turn slightly right" if angle > 0 else "Turn slightly left"
    elif angle < 120:
        return "Turn right" if angle > 0 else "Turn left"
    else:
        return "Turn sharp right" if angle > 0 else "Turn sharp left"


def point_line_distance(point, start, end):
    if start == end:
        return distance.distance(point, start).meters
    n = abs((end[0] - start[0]) * (start[1] - point[1]) - (start[0] - point[0]) * (end[1] - start[1]))
    d = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
    return n / d


def douglas_peucker(points, epsilon):
    if len(points) <= 2:
        return points

    dmax = 0
    index = 0
    for i in range(1, len(points) - 1):
        d = point_line_distance(points[i], points[0], points[-1])
        if d > dmax:
            index = i
            dmax = d

    if dmax > epsilon:
        results = douglas_peucker(points[:index + 1], epsilon)[:-1] + douglas_peucker(points[index:], epsilon)
    else:
        results = [points[0], points[-1]]

    return results


def generate_instructions(features):
    instructions = []
    total_distance = 0
    all_coords = []
    floor_info = {}
    vertical_transport = {}

    for feature in features:
        props = feature['properties']
        geometry = feature['geometry']

        if geometry['type'] == 'LineString':
            coords = geometry['coordinates']
            all_coords.extend(coords)
            floor = props.get('floor')
            if floor is not None:
                for coord in coords:
                    floor_info[tuple(coord)] = floor

        if props.get('travelType') in ['LIFT', 'STAIRS', 'ESCALATOR']:
            coord = tuple(geometry['coordinates'])
            vertical_transport[coord] = props

        if props.get('endpointType') == 'from':
            start_point = tuple(geometry['coordinates'])
            start_floor = props.get('floor')
            start_label = props.get('label')
        elif props.get('endpointType') == 'to':
            end_point = tuple(geometry['coordinates'])
            end_floor = props.get('floor')
            end_label = props.get('label')

    simplified_path = douglas_peucker(all_coords, epsilon=0.00005)

    current_floor = start_floor if start_floor is not None else 0
    instructions.append(f"You are at {start_label} on floor {current_floor}")

    for i in range(len(simplified_path) - 1):
        start = tuple(simplified_path[i])
        end = tuple(simplified_path[i + 1])
        segment_distance = distance.distance(start[::-1], end[::-1]).meters
        total_distance += segment_distance

        if i > 0:
            prev = tuple(simplified_path[i - 1])
            angle = calculate_relative_angle(prev, start, end)
            turn_instruction = get_turn_instruction(angle)
            instructions.append(f"{turn_instruction} and walk for about {round(segment_distance)} meters")
        else:
            instructions.append(f"Walk straight for about {round(segment_distance)} meters")

        # Check for vertical transport
        for coord in [start, end]:
            if coord in vertical_transport:
                transport = vertical_transport[coord]
                transport_type = transport['travelType'].lower()
                direction = transport.get('direction', 'to')
                source_floor = transport.get('sourceFloor')
                dest_floor = transport.get('destinationFloor')
                if source_floor == current_floor:
                    instructions.append(f"Take the {transport_type} {direction} floor {dest_floor}")
                    current_floor = dest_floor
                break

        # Check for floor changes without explicit vertical transport
        if end in floor_info and floor_info[end] != current_floor:
            new_floor = floor_info[end]
            if new_floor is not None and current_floor is not None:
                if new_floor > current_floor:
                    direction = "up"
                elif new_floor < current_floor:
                    direction = "down"
                else:
                    direction = "to"
                instructions.append(f"Go {direction} to floor {new_floor}")
            current_floor = new_floor

    end_floor = end_floor if end_floor is not None else current_floor
    instructions.append(f"You have arrived at {end_label} on floor {end_floor}")
    instructions.append(f"Total walking distance: approximately {round(total_distance)} meters")

    return instructions
