/* Audio Library for Teensy 3.X
 * Copyright (c) 2014, Pete (El Supremo), el_supremo@shaw.ca
 *
 * Development of this audio library was funded by PJRC.COM, LLC by sales of
 * Teensy and Audio Adaptor boards.  Please support PJRC's efforts to develop
 * open source software by purchasing Teensy or other PJRC products.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice, development funding notice, and this permission
 * notice shall be included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

// Read/Write W25Q128FV SPI flash (128Mbit = 16MBytes)
// 
// Pete (El Supremo)

/*
NOTES
  - this assumes that the page number referenced in page_number
    has been erased. If it hasn't, the read_back will be incorrect.
  - do not panic when the serial monitor outputs a whole series
of 255 at the end. This correct! scroll back to the beginning of the
output. It shoud like this:

Status = 0
EF, 40, 18, 0, 

Write Page 0xFFFF
time (us) = 814

Read Page 0xFFFF
time (us) = 429
0
1
2
3
4
5
6
.
.
.
etc.

It reads and prints the chip's status and then its ID.
Then it writes 0,1,2,3,...,254,255 into a 256 bytes buffer and writes
that into page_number on the chip. It then reads that back, so that
the output should be 0,1,2,3,...,254,255 (one per line). It then
erases the sector containing that page and times the operation.
You should see something like this:

Erase sector
time (us) = 90315

Read Page 0xFFFF
time (us) = 424
255
255
255
.
.
.

It should report that everything is 255 because the sector
(and the page) have been erased.


140426
  c
  - Change name to flash_test for release
  
  b
  - fix references to flash_read_page to flash_read_pages
    and flash_read_fast_page to flash_read_pages (the library
    now uses the fast method all the time).
  - remove last segment which does another read fast - obsolete.
  
140402
  a
  - read the ID
  - write 256 bytes to a page and then read them back.
  - erase the sector and read the page again - works
  
  On Teensy 3 there is/was a problem with SPI
  See: http://forum.pjrc.com/threads/7353-Bug-with-SPI
*/

#include <Audio.h>
#include <SPI.h>
#include <Wire.h>
#include <SD.h>
#include <flash_spi.h>

// Highest page number is 0xffff=65535
int page_number = 0xffff;
unsigned char w_page[256];
unsigned char r_page[256];

void setup() {
  unsigned char id_tab[32];
  unsigned long t_start;
  
  Serial.begin(9600);
  while(!Serial);
  delay(2000);

  // Assign MOSI and SCK for the audio board
  SPI.setMOSI(7);
  SPI.setSCK(14);

  flash_init();

//>>> Read Status Register 1 and the chip ID
  Serial.print("Status = ");
  Serial.println(flash_read_status(),HEX);
  // flash read doesn't work unless preceded by flash_read_status ??
  // Page 24 - a W25Q128FV should return EF, 40, 18, 0,
  flash_read_id(id_tab);
  // Just print the first four bytes
  // For now ignore the 16 remaining bytes
  for(int i = 0;i < 4;i++) {
    Serial.print(id_tab[i],HEX);
    Serial.print(", ");
  }
  Serial.println("");
  Serial.println("");

//>>> Initialize the array to 0,1,2,3 etc.
  for(int i = 0;i < 256;i++) {
    w_page[i] = i;
  }
  
//>>> Write the page to page_number - this page MUST be in the
// erased state
  Serial.print("Write Page 0x");
  Serial.println(page_number,HEX);
t_start = micros();
  flash_page_program(w_page,page_number);
t_start = micros() - t_start;
Serial.print("time (us) = ");
Serial.println(t_start);
  Serial.println("");

//>>> Read back page_number and print its contents which
// should be 0,1,2,3...
  Serial.print("Read Page 0x");
  Serial.println(page_number,HEX);
t_start = micros();
  flash_read_pages(r_page,page_number,1);
t_start = micros() - t_start;
Serial.print("time (us) = ");
Serial.println(t_start);
  for(int i = 0;i < 256;i++) {
    Serial.println(r_page[i]);
  }
  Serial.println("");
  
//>>> Erase the sector which includes page_number
  Serial.println("Erase sector");
t_start = micros();
  flash_erase_pages_sector(page_number);
t_start = micros() - t_start;
Serial.print("time (us) = ");
Serial.println(t_start);
Serial.println("");

//>>> Now read back the page. It should now be all 255.
  Serial.print("Read Page 0x");
  Serial.println(page_number,HEX);
t_start = micros();
  flash_read_pages(r_page,page_number,1);
t_start = micros() - t_start;
Serial.print("time (us) = ");
Serial.println(t_start);
  for(int i = 0;i < 256;i++) {
    Serial.println(r_page[i]);
  }
  Serial.println(""); 

}

void loop() {
}



