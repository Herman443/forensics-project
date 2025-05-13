from fs_analyzer import analyze_filesystem
import argparse


def main():
    parser = argparse.ArgumentParser(description="LittleFS Forensics Tool")
    parser.add_argument("image", help="Path to LittleFS image file")
    parser.add_argument(
        "--dump-raw", action="store_true", help="Dump raw flash contents"
    )
    parser.add_argument(
        "--dump-mode",
        choices=["file", "terminal"],
        default="file",
        help="Where to send dump: 'file' (default) or 'terminal'",
    )
    parser.add_argument(
        "--search", help="Search for a string in raw image data (e.g., 'secret')"
    )
    args = parser.parse_args()

    analyze_filesystem(args.image, args.dump_raw, args.search, args.dump_mode)


if __name__ == "__main__":
    main()
