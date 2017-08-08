#include <Arduino.h>
#include "mbed.h"
#include "FATFileSystem.h"
#include "SFlashBlockDevice.h"
#include "HeapBlockDevice.h"
#include "fatfs_exfuns.h"
#include <stdio.h>
#include <errno.h>

SFlashBlockDevice bd;
FATFileSystem fs("fs");

void processError(int ret_val) {
  if (ret_val) {
    Serial.print("Failure.");
    Serial.println(ret_val);
  } else {
    Serial.println("done.");
  }
}

void processError(void* ret_val) {
  if (ret_val == NULL) {
    Serial.println(" Failure.");
  } else {
    Serial.println(" done.");
  }
}


void setup() {
  int error = 0;
  Serial.println("Welcome to the filesystem example.");

  // Format file system
  Serial.print("Formatting a FAT, RAM-backed filesystem.");
  error = FATFileSystem::format(&bd);
  processError(error);

  // Mount the file system
  Serial.print("Mounting the filesystem on \"/fs\".");
  error = fs.mount(&bd);
  processError(error);

  // Open file to write
  Serial.print("Opening a new file, numbers.txt.");
  FILE* fd = fopen("/fs/numbers.txt", "w");
  processError(fd);

  Serial.print("Writing decimal numbers 1~20 to a file.");
  for (int i = 0; i < 20; i++){
    fprintf(fd, "%d\r\n", i + 1);
  }
  Serial.print("done.\r\n");

  // Close file
  Serial.print("Closing file.");
  fclose(fd);
  Serial.print(" done.\r\n");

  // Re-open file to read
  Serial.print("Re-opening file read-only.");
  fd = fopen("/fs/numbers.txt", "r");
  processError(fd);

  Serial.print("Dumping file to screen.\r\n");
  delay(100);
  char buff[16] = {0};
  while (!feof(fd)){
    int size = fread(&buff[0], 1, 15, fd);
    fwrite(&buff[0], 1, size, stdout);
  }
  Serial.println("EOF.");

  Serial.print("Closing file.");
  fclose(fd);
  Serial.println(" done.");

  Serial.print("Opening root directory.");
  DIR* dir = opendir("/fs/");
  processError(fd);

  struct dirent* de;
  Serial.print("Printing all filenames:\r\n");
  while((de = readdir(dir)) != NULL){
    Serial.println(&(de->d_name)[0]);
  }

  Serial.print("Closeing root directory. ");
  error = closedir(dir);
  processError(error);

  Serial.println("FileSystem Demo complete.");
  filesystem_info info = fatfs_get_info();
  char buf[128];
  sprintf(buf, "Total drive space: %d %cB; free space :%d %cB\r\n", info.total_space, info.unit, info.free_space, info.unit);
  Serial.println(buf);
}

void loop() {
  // put your main code here, to run repeatedly:

}