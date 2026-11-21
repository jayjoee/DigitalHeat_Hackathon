# Blister inspection on two screens

Two laptops inspect 30 synthetic images of eight-pocket blister packs. The image processing compares each pocket's centre with the surrounding foil and marks empty pockets. Both laptops have the same deterministic image set.

The heat timeline starts at 06:00 on 25 May 2025. At 10:00 model time the simulated 35 kWh house tank is full. The house pauses after pack 8 and sends a TLS checkpoint with the position, reject count and model time. The pool starts at pack 9. The house draws 0.5 kWh per model hour from storage. At 16:00 the tank reaches 32 kWh and the house takes back the checkpoint at pack 21.

The screens show outdoor temperature, the case's 20 °C indoor setpoint, storage and local recovered heat for one modelled server. Full allocation delivers 0.8 kW to water. The illustrated water supply temperature is 55 °C. These are simulated figures. The image processing and transfer run on the laptops.

## On one laptop

From the repository root, with Python 3.10 or later and OpenSSL:

```sh
python3 prototyp/blister_demo.py demo --open
```

Select **Start batch** in the house tab. The complete batch has 24 passed packs and six rejected packs.

## On two laptops

Use the same repository version and Wi-Fi network:

1. On the pool laptop, run `python3 prototyp/schwimmbad.py --job blister` and note the six-digit code.
2. On the house laptop, run `python3 prototyp/haus.py --job blister`, then enter the code.
3. In the house browser, select **Start batch**. The job transfers automatically.

The house screen runs on port 8082, and the sports pool screen uses 8092. If discovery fails, pass `--bad 192.168.1.42` to the house command with the address shown on the pool laptop. Guest networks may block communication between devices. An unconfirmed transfer leaves the house paused. **Retry handoff** resends the same checkpoint. Restart both processes for a fresh run.

Pairing creates temporary credentials. The course demo assumes a trusted local network and uses synthetic data.
