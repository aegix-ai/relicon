export interface Device {
  name: string;
  devices: number;
  consumption: number;
  type: 'plug' | 'electrical';
}

export interface ConsumptionCategory {
  title: string;
  devices: Device[];
}
