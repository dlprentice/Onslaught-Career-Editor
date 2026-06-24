/* address: 0x005819b8 */
/* name: CFastVB__Helper_005819b8 */
/* signature: double __stdcall CFastVB__Helper_005819b8(float param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double CFastVB__Helper_005819b8(float param_1)

{
  int iVar1;
  float fVar2;
  float fVar3;
  double dVar4;

  dVar4 = CDXTexture__FastReciprocalSqrtScalar((uint)param_1);
  fVar2 = (float)dVar4 * param_1 * _DAT_005e9f0c;
  iVar1 = (int)ROUND(fVar2);
  fVar3 = (float)iVar1;
  if (iVar1 < 0) {
    fVar3 = fVar3 + _DAT_005e72d8;
  }
  return (double)((fVar2 - fVar3) *
                  (*(float *)(&DAT_005e96d4 + iVar1 * 4) - *(float *)(&DAT_005e96d0 + iVar1 * 4)) +
                 *(float *)(&DAT_005e96d0 + iVar1 * 4));
}
