/* address: 0x00581a08 */
/* name: CFastVB__Helper_00581a08 */
/* signature: double __stdcall CFastVB__Helper_00581a08(float param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double CFastVB__Helper_00581a08(float param_1)

{
  int iVar1;
  float fVar2;
  float fVar3;

  fVar2 = param_1 * param_1 * _DAT_005e9f0c;
  iVar1 = (int)ROUND(fVar2);
  fVar3 = (float)iVar1;
  if (iVar1 < 0) {
    fVar3 = fVar3 + _DAT_005e72d8;
  }
  return (double)((fVar2 - fVar3) *
                  (*(float *)(&DAT_005e9ad4 + iVar1 * 4) - *(float *)(&DAT_005e9ad0 + iVar1 * 4)) +
                 *(float *)(&DAT_005e9ad0 + iVar1 * 4));
}
