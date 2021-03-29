/*  Arduino wrapper for DoomGeneric
 *  Mouse and keyboard controls are not implemented at the moment; 
 *  to use the internal QSPI flash as storage, force the board in bootloader mode 
 *  by double clicking the reset button and upload doom.fat.dump (from doom/utils folder)
 *  with this command
 *  
 *  dfu-util -a1 --device 0x2341:0x035b -D doom.fat.dump --dfuse-address=0x90000000
 */

#include <Arduino.h>

#include "QSPIFBlockDevice.h"
#include "FATFileSystem.h"
#include "doomgeneric.h"

QSPIFBlockDevice block_device(PD_11, PD_12, PF_7, PD_13,  PF_10, PG_6, QSPIF_POLARITY_MODE_1, 40000000);
// Comment previous line and uncomment these two if you want to store DOOM.WAD in an external SD card (FAT32 formatted)
// #include "SDMMCBlockDevice.h"
// SDMMCBlockDevice block_device;

mbed::FATFileSystem fs("fs");

extern "C" int main_wrapper(int argc, char **argv);
char*argv[] = {"/fs/doom", "-iwad", "/fs/DOOM1.WAD"};

void setup() {
  // put your setup code here, to run once:
  delay(2000);
  int err =  fs.mount(&block_device);

  if (err) {
    // Reformat if we can't mount the filesystem
    // this should only happen on the first boot
    printf("No filesystem found, formatting... ");
    fflush(stdout);
    err = fs.reformat(&block_device);
  }
  DIR *dir;
  struct dirent *ent;
  printf("try to open dir\n");
  if ((dir = opendir("/fs")) != NULL) {
    /* print all the files and directories within directory */
    while ((ent = readdir (dir)) != NULL) {
      printf ("%s\n", ent->d_name);
    }
    closedir (dir);
  } else {
    /* could not open directory */
    printf ("error\n");
  }
  main_wrapper(3, argv);
}

void loop() {
  // put your main code here, to run repeatedly:

}