/* address: 0x00574270 */
/* name: CMeshCollisionVolume__Helper_00574270 */
/* signature: int * __stdcall CMeshCollisionVolume__Helper_00574270(int param_1) */


int * CMeshCollisionVolume__Helper_00574270(int param_1)

{
  int *piVar1;

  piVar1 = &DAT_005e6a68;
  while( true ) {
    if (PTR_DAT_00656f28 <= piVar1) {
      return &DAT_005e6a40;
    }
    if (param_1 == *piVar1) break;
    piVar1 = piVar1 + 9;
  }
  return piVar1;
}
