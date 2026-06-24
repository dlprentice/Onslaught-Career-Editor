/* address: 0x00454e00 */
/* name: Controls__GetDeviceCategory */
/* signature: int __cdecl Controls__GetDeviceCategory(int device_code) */


/* Maps a raw device_code (keyboard/mouse/joy identifiers) into a smaller set of device categories
   (1..7). Used by Controls__ClearDuplicateBinding to treat related devices as equivalent when
   clearing conflicts. */

int __cdecl Controls__GetDeviceCategory(int device_code)

{
  switch(device_code) {
  default:
    return 1;
  case 4:
  case 6:
    return 3;
  case 5:
  case 7:
    return 2;
  case 8:
  case 9:
  case 10:
    return 4;
  case 0xb:
  case 0xd:
    return 5;
  case 0xc:
  case 0xe:
    return 6;
  case 0xf:
  case 0x10:
  case 0x11:
    return 7;
  }
}
