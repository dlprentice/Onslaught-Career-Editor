/* address: 0x004b52a0 */
/* name: Math__AbsDoubleFromSignedFloat */
/* signature: double __cdecl Math__AbsDoubleFromSignedFloat(float param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __cdecl Math__AbsDoubleFromSignedFloat(float param_1)

{
  if (param_1 < _DAT_005d856c) {
    return (double)-param_1;
  }
  return (double)param_1;
}
