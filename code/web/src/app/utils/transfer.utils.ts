type GeographicCoordinate = [number, number];

export class TransferUtils {
  private static EARTH_RADIUS = 6371000; // Earth's radius in meters

  static degreesToRadians(degrees: number): number {
    return degrees * (Math.PI / 180);
  }

  static distanceInMeters(point1: GeographicCoordinate, point2: GeographicCoordinate): number {
    const [lon1, lat1] = point1;
    const [lon2, lat2] = point2;

    const dLat = this.degreesToRadians(lat2 - lat1);
    const dLon = this.degreesToRadians(lon2 - lon1);

    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(this.degreesToRadians(lat1)) * Math.cos(this.degreesToRadians(lat2)) *
      Math.sin(dLon / 2) * Math.sin(dLon / 2);

    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

    return this.EARTH_RADIUS * c; // Distance in meters
  }

  static calculateRelativeAngle(point1: GeographicCoordinate, point2: GeographicCoordinate, point3: GeographicCoordinate): number {
    const vector1 = [point2[0] - point1[0], point2[1] - point1[1]];
    const vector2 = [point3[0] - point2[0], point3[1] - point2[1]];

    const dotProduct = vector1[0] * vector2[0] + vector1[1] * vector2[1];
    const magnitude1 = Math.sqrt(vector1[0] ** 2 + vector1[1] ** 2);
    const magnitude2 = Math.sqrt(vector2[0] ** 2 + vector2[1] ** 2);

    if (magnitude1 === 0 || magnitude2 === 0) {
      return 0;
    }

    let cosAngle = dotProduct / (magnitude1 * magnitude2);
    cosAngle = Math.max(Math.min(cosAngle, 1), -1);
    const angle = Math.acos(cosAngle);
    return angle * (180 / Math.PI);
  }

  static getTurnInstruction(angle: number): string {
    if (angle < 20) {
      return "Continue straight";
    } else if (angle < 60) {
      return angle > 0 ? "Turn slightly right" : "Turn slightly left";
    } else if (angle < 120) {
      return angle > 0 ? "Turn right" : "Turn left";
    } else {
      return angle > 0 ? "Turn sharp right" : "Turn sharp left";
    }
  }

  static pointLineDistance(point: GeographicCoordinate, start: GeographicCoordinate, end: GeographicCoordinate): number {
    if (start[0] === end[0] && start[1] === end[1]) {
      return this.distanceInMeters(point, start);
    }
    const n = Math.abs((end[0] - start[0]) * (start[1] - point[1]) - (start[0] - point[0]) * (end[1] - start[1]));
    const d = Math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2);
    return (n / d) * this.distanceInMeters(start, end);
  }

  static douglasPeucker(points: GeographicCoordinate[], epsilon: number): GeographicCoordinate[] {
    if (points.length <= 2) {
      return points;
    }

    let dmax = 0;
    let index = 0;
    const end = points.length - 1;

    for (let i = 1; i < end; i++) {
      const d = this.pointLineDistance(points[i], points[0], points[end]);
      if (d > dmax) {
        index = i;
        dmax = d;
      }
    }

    if (dmax > epsilon) {
      const recResults1 = this.douglasPeucker(points.slice(0, index + 1), epsilon);
      const recResults2 = this.douglasPeucker(points.slice(index), epsilon);
      return [...recResults1.slice(0, -1), ...recResults2];
    } else {
      return [points[0], points[end]];
    }
  }

  static generateInstructions(features: any[]): string[] {
    const instructions: string[] = [];
    let totalDistance = 0;
    const allCoords: GeographicCoordinate[] = [];
    const floorInfo: { [key: string]: number } = {};
    const verticalTransport: { [key: string]: any } = {};

    let startPoint: GeographicCoordinate | null = null;
    let startFloor = 0;
    let startLabel = '';
    let endPoint: GeographicCoordinate | null = null;
    let endFloor = 0;
    let endLabel = '';

    for (const feature of features) {
      const props = feature.properties;
      const geometry = feature.geometry;

      if (geometry.type === 'LineString') {
        const coords = geometry.coordinates as GeographicCoordinate[];
        allCoords.push(...coords);
        const floor = props.floor;
        if (floor !== undefined) {
          for (const coord of coords) {
            floorInfo[coord.toString()] = floor;
          }
        }
      }

      if (['LIFT', 'STAIRS', 'ESCALATOR', 'RAMP'].includes(props.travelType)) {
        const coord = geometry.coordinates as GeographicCoordinate;
        verticalTransport[coord.toString()] = {
          type: props.travelType,
          direction: props.direction,
          sourceFloor: props.sourceFloor,
          destinationFloor: props.destinationFloor
        };
      }

      if (props.endpointType === 'from') {
        startPoint = geometry.coordinates as GeographicCoordinate;
        startFloor = props.floor || 0;
        startLabel = props.label;
      } else if (props.endpointType === 'to') {
        endPoint = geometry.coordinates as GeographicCoordinate;
        endFloor = props.floor || 0;
        endLabel = props.label;
      }
    }

    const simplifiedPath = this.douglasPeucker(allCoords, 0.00005);

    let currentFloor = startFloor;
    instructions.push(`You are at ${startLabel} on floor ${currentFloor}.`);

    for (let i = 0; i < simplifiedPath.length - 1; i++) {
      const start = simplifiedPath[i];
      const end = simplifiedPath[i + 1];
      const segmentDistance = this.distanceInMeters(start, end);
      totalDistance += segmentDistance;

      if (i > 0) {
        const prev = simplifiedPath[i - 1];
        const angle = this.calculateRelativeAngle(prev, start, end);
        const turnInstruction = this.getTurnInstruction(angle);
        instructions.push(`${turnInstruction} and continue for about ${Math.round(segmentDistance)} meters.`);
      } else {
        instructions.push(`Walk straight for about ${Math.round(segmentDistance)} meters.`);
      }

      // Check for vertical transport
      for (const [coord, transport] of Object.entries(verticalTransport)) {
        // @ts-ignore
        const coordPoint = coord.toString() as GeographicCoordinate;
        if (this.distanceInMeters(coordPoint, end) < 5) { // within 5 meters
          const transportType = transport.type.toLowerCase();
          instructions.push(`You are in front of a ${transportType}.`);
          instructions.push(`Take the ${transportType} ${transport.direction} from floor ${transport.sourceFloor} to floor ${transport.destinationFloor}.`);
          currentFloor = transport.destinationFloor;
          break;
        }
      }

      // Check for floor changes without explicit vertical transport
      const endFloorInfo = floorInfo[end.toString()];
      if (endFloorInfo !== undefined && endFloorInfo !== currentFloor) {
        instructions.push(`You are now on floor ${endFloorInfo}.`);
        currentFloor = endFloorInfo;
      }
    }

    instructions.push(`You have arrived at ${endLabel} on floor ${endFloor}.`);
    instructions.push(`Total distance: approximately ${Math.round(totalDistance)} meters.`);

    return instructions;
  }
}
