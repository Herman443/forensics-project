def dump_raw_to_file(data):
    with open("raw_dump.hex", "w") as f:
        f.write(data.hex())
    print("Raw image data dumped to raw_dump.hex")


def dump_raw_to_terminal(data):
    bytes_per_line = 16
    for i in range(0, len(data), bytes_per_line):
        chunk = data[i : i + bytes_per_line]
        hex_str = " ".join(f"{b:02x}" for b in chunk)
        ascii_str = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
        print(f"{i:08x}  {hex_str:<48}  {ascii_str}")


def search_raw(data, keyword):
    try:
        decoded = data.decode("utf-8", errors="ignore")
        if keyword in decoded:
            print(f"Found keyword '{keyword}' in raw image data!")
        else:
            print(f"Keyword '{keyword}' not found.")
    except Exception as e:
        print(f"Error while searching: {e}")
