/* address: 0x0040b660 */
/* name: CGeneralVolume__Unk_0040b660 */
/* signature: double __cdecl CGeneralVolume__Unk_0040b660(float param_1, float param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __cdecl CGeneralVolume__Unk_0040b660(float param_1,float param_2)

{
  if ((param_1 < _DAT_005d85c8) && (_DAT_005d85e4 < param_2)) {
    return (double)(param_1 - (param_2 - _DAT_005d85e0));
  }
  if ((_DAT_005d85e4 < param_1) && (param_2 < _DAT_005d85c8)) {
    return (double)(param_1 - (param_2 + _DAT_005d85e0));
  }
  return (double)(param_1 - param_2);
}
