#include "FATFileSystem.h"
#include "SFlashBlockDevice.h"
#include "fatfs_exfuns.h"
#include <stdio.h>
#include <errno.h>

SFlashBlockDevice bd;
FATFileSystem fs("fs");

static int initFS()
{
  // Mount the file system
  int error = fs.mount(&bd);
  if (error != 0)
  {
    Serial.printf("Mount failed %d.\r\n", error);
    return -1;
  }
  filesystem_info info = fatfs_get_info();
  if (info.total_space == 0)
  {
    fs.unmount();
    // Format the disk
    Serial.print("Formatting the file system...");
    error = FATFileSystem::format(&bd);
    if (error != 0)
    {
      Serial.printf("failed (%d).\r\n", error);
      return -2;
    }
    Serial.println("done.");

    // Mount again
    int error = fs.mount(&bd);
    if (error != 0)
    {
      Serial.printf("Mount failed %d.\r\n", error);
      return -1;
    }
    filesystem_info info = fatfs_get_info();
    if (info.total_space == 0)
    {
      Serial.println("Internal error, load filesystem fault.");
      return -2;
    }
  }

  Serial.println("Mount the filesystem on \"/fs\".");
  Serial.printf("Total drive space: %d %cB; free space :%d %cB\r\n", info.total_space, info.unit, info.free_space, info.unit);
  return 0;
}

static int listFiles()
{
  DIR* dir = opendir("/fs/");
  if (dir == NULL)
  {
    Serial.println("Open root directory failed.");
    return -1;
  }

  struct dirent* de;
  Serial.println("ls /fs:");
  while((de = readdir(dir)) != NULL){
    Serial.print("  ");
    Serial.println(&(de->d_name)[0]);
  }

  int error = closedir(dir);
  if (error != 0)
  {
    Serial.printf("Close directory failed %d.\r\n", error);
    return - 1;
  }
  return 0;
}

static int writeFile()
{
  // Open file to write
  FILE* fd = fopen("/fs/numbers.txt", "w");
  if (fd == NULL)
  {
    Serial.printf("Open /fs/numbers.txt failed %d.\r\n", error);
    return -1;
  }
  
  Serial.print("Writing decimal numbers 1~20 to the file...");
  for (int i = 0; i < 20; i++){
    fprintf(fd, "%d\r\n", i + 1);
  }
  Serial.println("done.");

  fclose(fd);
  return 0;
}

static int readFile()
{
  // Open file to read
  Serial.print("Re-opening file with read-only mode,");
  FILE* fd = fopen("/fs/numbers.txt", "r");
  if (fd == NULL)
  {
    Serial.println("failed.");
    return -1;
  }
  Serial.println("done.");

  Serial.println("Dumping file:");
  delay(100);
  char buff[16] = {0};
  while (!feof(fd)){
    int size = fread(buff, 1, 15, fd);
    if (size > 0)
    {
      buff[size] = 0;
      Serial.print(buff);
    }
  }
  Serial.println("EOF.");

  fclose(fd);
  return 0;
}

void setup() {
  Serial.println("Welcome to the FileSystem example.");

  if (initFS() != 0)
  {
    return;
  }

  if (listFiles() != 0)
  {
    return;
  }

  if (writeFile() != 0)
  {
    return;
  }

  if (readFile() != 0)
  {
    return;
  }
  
  Serial.println("All done.");
}

void loop() {
  // put your main code here, to run repeatedly:
  delay(1000);
}