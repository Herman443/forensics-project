# LittleFS Forensics Tool

This project is a simple forensic analysis tool for examining raw LittleFS flash images. It can search for deleted file content, dump raw flash data, and demonstrate that **deleted files in LittleFS may remain recoverable** from unreferenced flash blocks.

Due to API limitations in the official littlefs-python library, it is not possible to mount and list files from an image that was generated externally (e.g., in C). The library only supports creating and managing LittleFS instances from within Python, not parsing arbitrary on-disk images. As a result, this tool focuses on raw image analysis — including metadata inspection, string search, and validation of undeleted file content — which still provides meaningful forensic insight.

---

## Features

- Search raw flash data for keywords (e.g. deleted file content)
- Dump flash image data in a clean hex+ASCII format
- Supports dumping to file or printing directly to the terminal (recommend dumping to file)
- Demonstrates that LittleFS **does not securely erase deleted content**

---

## Requirements

- Python 3.7+
- `littlefs-python` (used for formatting and configuration)

## Installation

```bash
git clone https://github.com/Herman443/forensics-project.git
cd littlefs-forensics
pip install -r requirements.txt
```

---

## Usage

### Basic command:

    python lfs_tool/main.py lfs.img

### Search for a string (e.g. from a deleted file):

    python lfs_tool/main.py lfs.img --search "hello"

### Dump raw flash contents to a hex file:

    python lfs_tool/main.py lfs.img --dump-raw

### Dump raw flash contents directly to terminal:

    python lfs_tool/main.py lfs.img --dump-raw --dump-mode terminal

---

## Test Cases

This tool was used to evaluate different filesystem states to assess data recoverability:
| Case | File Present | `secret` Found by Tool | Explanation |
|-------------------------------------|--------------|------------------------|---------------------------------------------------|
| File written and not deleted | ✅ | ✅ | File is active, content accessible |
| File never written | ❌ | ❌ | No data exists in the image |
| File written and then deleted | ❌ | ✅ | File not visible, but raw content still present |
| File written, deleted, overwritten | ❌ | ❌ | Flash block reused, deleted content is erased |

---

## Creating the LittleFS Image

I built the image by writing a C program using the official [LittleFS library](https://github.com/littlefs-project/littlefs). This file was used in the official tool repo:

```c
#include "lfs.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define BLOCK_SIZE 512
#define BLOCK_COUNT 128
#define IMAGE_FILE "lfs.img"

static uint8_t storage[BLOCK_SIZE * BLOCK_COUNT];

// Block device functions
int user_read(const struct lfs_config *c, lfs_block_t block,
              lfs_off_t off, void *buffer, lfs_size_t size) {
    memcpy(buffer, &storage[BLOCK_SIZE * block + off], size);
    return 0;
}

int user_prog(const struct lfs_config *c, lfs_block_t block,
              lfs_off_t off, const void *buffer, lfs_size_t size) {
    memcpy(&storage[BLOCK_SIZE * block + off], buffer, size);
    return 0;
}

int user_erase(const struct lfs_config *c, lfs_block_t block) {
    memset(&storage[BLOCK_SIZE * block], 0xFF, BLOCK_SIZE);
    return 0;
}

int user_sync(const struct lfs_config *c) {
    return 0;
}

// Dummy CRC function (required by LittleFS)
uint32_t lfs_crc(uint32_t crc, const void *buffer, size_t size) {
    return 0;
}

int main() {
    // Set up configuration
    struct lfs_config cfg = {
        .context = NULL,
        .read = user_read,
        .prog = user_prog,
        .erase = user_erase,
        .sync = user_sync,
        .block_size = BLOCK_SIZE,
        .block_count = BLOCK_COUNT,
        .read_size = 16,
        .prog_size = 16,
        .cache_size = 16,
        .lookahead_size = 16,
        .block_cycles = 500
    };

    lfs_t lfs;
    lfs_format(&lfs, &cfg);
    lfs_mount(&lfs, &cfg);

    // File 1: hello.txt
    lfs_file_t file;
    lfs_file_open(&lfs, &file, "hello.txt", LFS_O_WRONLY | LFS_O_CREAT);
    lfs_file_write(&lfs, &file, "Hello from LittleFS!\n", 23);
    lfs_file_close(&lfs, &file);

    // File 2: secret.txt
    lfs_file_open(&lfs, &file, "secret.txt", LFS_O_WRONLY | LFS_O_CREAT);
    lfs_file_write(&lfs, &file, "This is a secret string.", 26);
    lfs_file_close(&lfs, &file);

    // Delete secret.txt (to simulate deletion)
    lfs_remove(&lfs, "secret.txt");

    lfs_unmount(&lfs);

    // Save raw image to disk
    FILE *img = fopen(IMAGE_FILE, "wb");
    fwrite(storage, 1, sizeof(storage), img);
    fclose(img);

    printf("Created '%s' with hello.txt and deleted secret.txt\n", IMAGE_FILE);
    return 0;
}


```

### Step 1: Write files

    lfs_file_open(&lfs, &file, "secret.txt", LFS_O_WRONLY | LFS_O_CREAT);
    lfs_file_write(&lfs, &file, "This is a secret string.", 26);
    lfs_file_close(&lfs, &file);

### Step 2: Delete the file

    lfs_remove(&lfs, "secret.txt");

### Step 3: Save image

    FILE *img = fopen("lfs.img", "wb");
    fwrite(storage, 1, sizeof(storage), img);
    fclose(img);

This simulates a **real-world delete**, where the file is removed from the directory but its data still resides in unallocated flash.

---

## Forensic Result

Running the tool on this image:

    python lfs_tool/main.py lfs.img --search "secret"

Output:

    Found keyword 'secret' in raw image data!

This confirms that LittleFS **does not securely wipe data on deletion**, making it possible to recover deleted content using forensic techniques.

---

## References

- [LittleFS GitHub](https://github.com/littlefs-project/littlefs)
- [littlefs-python](https://github.com/littlefs-project/littlefs-python)
- [Eurecom Forensics Project Guidelines]
