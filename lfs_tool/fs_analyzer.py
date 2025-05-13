from utils import dump_raw_to_file, dump_raw_to_terminal, search_raw


def analyze_filesystem(
    image_path, dump_raw_flag=False, search_term=None, dump_mode="file"
):
    print("Filesystem Info (assumed values):")
    print("Block size: 512")
    print("Block count: 128\n")

    try:
        with open(image_path, "rb") as f:
            raw = f.read()

            if dump_raw_flag:
                if dump_mode == "file":
                    dump_raw_to_file(raw)
                else:
                    dump_raw_to_terminal(raw)

            if search_term:
                search_raw(raw, search_term)

    except Exception as e:
        print(f"Failed to analyze image: {e}")
