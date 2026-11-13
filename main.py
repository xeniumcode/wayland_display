from pywayland.client import Display
from pywayland.protocol.wayland import WlOutput

display = Display()
display.connect()

def show(label, value):
    print(f"  {label:<24} {value}")

def handle_output_event(event, output, *data):
    if event == "geometry":
        x, y, physical_width, physical_height, subpixel, make, model, transform = data
        show("Position (x, y):", f"{x}, {y}")
        show("Physical Width:", f"{physical_width} mm")
        show("Physical Height:", f"{physical_height} mm")
        show("Subpixel:", subpixel)
        show("Maker:", make)
        show("Model:", model)
        show("Transform:", transform)

    elif event == "mode":
        flags, width, height, refresh = data
        show("Width:", f"{width}")
        show("Height:", f"{height}")
        show("Refresh Rate:", f"{refresh / 1000:.2f} Hz")
        show("Flags:", flags)
        show("Current Mode:", bool(flags & WlOutput.mode.current))

    elif event == "scale":
        (factor,) = data
        show("Scale:", factor)

    elif event == "name":
        (name,) = data
        show("Name:", name)

    elif event == "description":
        (description,) = data
        show("Description:", description)

    elif event == "done":
        pass

def make_handler(event):
    def handler(output, *data):
        handle_output_event(event, output, *data)
    return handler


registry = display.get_registry()
outputs = []

def on_global(registry, name, interface, version):
    if interface != "wl_output":
        return

    bound_version = min(version, 4)
    output = registry.bind(name, WlOutput, bound_version)
    outputs.append(output)

    print(f"{'Display Information':^35}")

    output.dispatcher["geometry"] = make_handler("geometry")
    output.dispatcher["mode"] = make_handler("mode")

    if bound_version >= 2:
        output.dispatcher["done"] = make_handler("done")
        output.dispatcher["scale"] = make_handler("scale")

    if bound_version >= 4:
        output.dispatcher["name"] = make_handler("name")
        output.dispatcher["description"] = make_handler("description")


registry.dispatcher["global"] = on_global

try:
    display.roundtrip()
    display.roundtrip()
finally:
    display.disconnect()