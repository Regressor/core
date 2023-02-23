"""The HUB-C2000PP service utils."""

import asyncio

import aioudp

SEP_STRING = "__DLM__"


async def get_devices(host, port):
    """Get devices from HUB-C2000PP service."""
    devices = {"zones": [], "relays": [], "parts": [], "error": False}

    try:
        async with aioudp.connect(host, port) as connection:
            # first is "BAD_CMD" because of "trash" from aioudp
            result = await asyncio.wait_for(connection.recv(), timeout=1)

            await connection.send(b"getZones")
            result = await asyncio.wait_for(connection.recv(), timeout=1)
            result = result.decode("utf-8")

            if result == "BAD_CMD":
                devices["error"] = "Server returned BAD_CMD"
                return devices

            if result:
                lines = result.split(SEP_STRING)
                for line in lines:
                    device_info = line.split(":")
                    if len(device_info) == 10:
                        if device_info[0] == "zone":
                            uid = f"{int(device_info[1])}.{device_info[2]}.{device_info[3]}.{device_info[4]}"
                            adc = device_info[6]
                            if adc and adc != "-":
                                adc = round(float(device_info[6]), 2)
                            device = {
                                "id": int(device_info[1]),
                                "sh": device_info[2],
                                "part": device_info[3],
                                "stype": device_info[4],
                                "state": device_info[5],
                                "adc": adc,
                                "type": device_info[7],
                                "dev": device_info[8],
                                "desc": device_info[9],
                                "uid": uid,
                            }
                            devices["zones"].append(device)
                            continue

                    devices["error"] = "Unexpected server reply"

            await connection.send(b"getParts")
            result = await asyncio.wait_for(connection.recv(), timeout=1)
            result = result.decode("utf-8")

            if result == "BAD_CMD":
                devices["error"] = "Server returned BAD_CMD"
                return devices

            if result:
                lines = result.split(SEP_STRING)
                for line in lines:
                    device_info = line.split(":")
                    if len(device_info) == 4:
                        if device_info[0] == "part":
                            device = {
                                "id": int(device_info[1]),
                                "stat": device_info[2],
                                "desc": device_info[3],
                            }
                            if device["stat"] == 0:
                                continue
                            devices["parts"].append(device)
                            continue

                    devices["error"] = "Unexpected server reply"

            await connection.send(b"getRelays")
            result = await asyncio.wait_for(connection.recv(), timeout=1)
            result = result.decode("utf-8")

            if result == "BAD_CMD":
                devices["error"] = "Server returned BAD_CMD"
                return devices

            if result:
                lines = result.split(SEP_STRING)
                for line in lines:
                    device_info = line.split(":")
                    if len(device_info) == 4:
                        if device_info[0] == "relay":
                            device = {
                                "id": int(device_info[1]),
                                "stat": device_info[2],
                                "desc": device_info[3],
                            }
                            devices["relays"].append(device)
                            continue

                    devices["error"] = "Unexpected server reply"

        return devices
    except asyncio.TimeoutError:
        devices["error"] = "Connection timeout"
        return devices
