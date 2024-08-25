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

        if props.get('travelType') in ['LIFT', 'STAIRS', 'ESCALATOR', 'RAMP']:
            coord = tuple(geometry['coordinates'])
            vertical_transport[coord] = {
                'type': props['travelType'],
                'direction': props.get('direction'),
                'sourceFloor': props.get('sourceFloor'),
                'destinationFloor': props.get('destinationFloor')
            }

        if props.get('endpointType') == 'from':
            start_point = tuple(geometry['coordinates'])
            start_floor = props.get('floor', 0)
            start_label = props.get('label')
        elif props.get('endpointType') == 'to':
            end_point = tuple(geometry['coordinates'])
            end_floor = props.get('floor', 0)
            end_label = props.get('label')

    simplified_path = douglas_peucker(all_coords, epsilon=0.00005)

    current_floor = start_floor
    instructions.append(f"You are at {start_label} on floor {current_floor}.")

    for i in range(len(simplified_path) - 1):
        start = tuple(simplified_path[i])
        end = tuple(simplified_path[i + 1])
        segment_distance = distance.distance(start[::-1], end[::-1]).meters
        total_distance += segment_distance

        if i > 0:
            prev = tuple(simplified_path[i - 1])
            angle = calculate_relative_angle(prev, start, end)
            turn_instruction = get_turn_instruction(angle)
            instructions.append(f"{turn_instruction} and continue for about {round(segment_distance)} meters.")
        else:
            instructions.append(f"Walk straight for about {round(segment_distance)} meters.")

        # Check for vertical transport
        for coord, transport in vertical_transport.items():
            if distance.distance(coord[::-1], end[::-1]).meters < 5:  # within 5 meters
                transport_type = transport['type'].lower()
                direction = transport['direction']
                source_floor = transport['sourceFloor']
                dest_floor = transport['destinationFloor']
                instructions.append(f"You are in front of a {transport_type}.")
                instructions.append(f"Take the {transport_type} {direction} from floor {source_floor} to floor {dest_floor}.")
                current_floor = dest_floor
                break

        # Check for floor changes without explicit vertical transport
        if end in floor_info and floor_info[end] != current_floor:
            new_floor = floor_info[end]
            if new_floor != current_floor:
                instructions.append(f"You are now on floor {new_floor}.")
            current_floor = new_floor

    instructions.append(f"You have arrived at {end_label} on floor {end_floor}.")
    instructions.append(f"Total distance: approximately {round(total_distance)} meters.")

    return instructions
