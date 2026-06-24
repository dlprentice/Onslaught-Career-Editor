/* address: 0x004114d0 */
/* name: CGeneralVolume__GetFlagFCScalar */
/* signature: double __fastcall CGeneralVolume__GetFlagFCScalar(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __fastcall CGeneralVolume__GetFlagFCScalar(int param_1)

{
  if (*(float *)(*(int *)(param_1 + 0x18) + 0xfc) == _DAT_005d856c) {
    return (double)_DAT_005d8cb0;
  }
  return (double)_DAT_005d856c;
}
