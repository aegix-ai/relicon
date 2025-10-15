import { Tv, Lightbulb, Coffee, Printer, WashingMachine, Wifi } from 'lucide-react';

const devices = [
  { name: 'Lamps', devices: 10, consumption: 78, icon: Lightbulb },
  { name: 'Smart TV', devices: 1, consumption: 180, icon: Tv },
  { name: 'Coffee Machine', devices: 1, consumption: 110, icon: Coffee },
  { name: 'Printer', devices: 1, consumption: 40, icon: Printer },
  { name: 'Washing Machine', devices: 1, consumption: 133, icon: WashingMachine },
  { name: 'Wi-Fi Router', devices: 2, consumption: 30, icon: Wifi },
];

export function PowerConsumption() {
  return (
    <div className="bg-gray-900 rounded-2xl p-6 text-white">
      <h2 className="text-xl font-semibold mb-4">Power Consumption</h2>
      <p className="text-sm text-gray-400 mb-6">Summary of energy consumption</p>
      
      <div className="grid grid-cols-2 gap-6 mb-6">
        <div>
          <div className="text-3xl font-bold">48</div>
          <div className="text-sm text-gray-400">kWh Daily Usage</div>
        </div>
        <div>
          <div className="text-3xl font-bold">680</div>
          <div className="text-sm text-gray-400">kWh Monthly Usage</div>
        </div>
      </div>
      
      <div className="space-y-4">
        {devices.map(device => (
          <div key={device.name} className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-3">
              <device.icon className="w-5 h-5 text-yellow-400" />
              <div>
                <div>{device.name}</div>
                <div className="text-xs text-gray-500">
                  {device.devices} {device.devices === 1 ? 'DEVICE' : 'DEVICES'}
                </div>
              </div>
            </div>
            <div className="text-gray-400">{device.consumption} kWh</div>
          </div>
        ))}
      </div>
    </div>
  );
}
