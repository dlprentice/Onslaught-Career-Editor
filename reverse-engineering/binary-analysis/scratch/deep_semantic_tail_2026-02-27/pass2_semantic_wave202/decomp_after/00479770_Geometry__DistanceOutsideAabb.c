/* address: 0x00479770 */
/* name: Geometry__DistanceOutsideAabb */
/* signature: double __cdecl Geometry__DistanceOutsideAabb(void * param_1, void * param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __cdecl Geometry__DistanceOutsideAabb(void *param_1,void *param_2)

{
  float fVar1;
  float fVar2;
  float fVar3;
  uint uVar4;

  fVar1 = ABS(*(float *)param_1) - ABS(*(float *)param_2);
  uVar4 = 0;
  if (_DAT_005d856c < fVar1) {
    uVar4 = DAT_0062c98c;
  }
  fVar2 = ABS(*(float *)((int)param_1 + 4)) - ABS(*(float *)((int)param_2 + 4));
  if (_DAT_005d856c < fVar2) {
    uVar4 = uVar4 | DAT_0062c990;
  }
  fVar3 = ABS(*(float *)((int)param_1 + 8)) - ABS(*(float *)((int)param_2 + 8));
  if (_DAT_005d856c < fVar3) {
    uVar4 = uVar4 | DAT_0062c994;
  }
  if (uVar4 != 0) {
    if (uVar4 == DAT_0062c98c) {
      return (double)fVar1;
    }
    if (uVar4 == DAT_0062c990) {
      return (double)fVar2;
    }
    if (uVar4 == DAT_0062c994) {
      return (double)fVar3;
    }
    if (uVar4 == (DAT_0062c990 | DAT_0062c98c)) {
      return (double)SQRT(fVar1 * fVar1 + fVar2 * fVar2);
    }
    if (uVar4 == (DAT_0062c994 | DAT_0062c98c)) {
      return (double)SQRT(fVar1 * fVar1 + fVar3 * fVar3);
    }
    if (uVar4 == (DAT_0062c994 | DAT_0062c990)) {
      return (double)SQRT(fVar2 * fVar2 + fVar3 * fVar3);
    }
    if (uVar4 == (DAT_0062c994 | DAT_0062c990 | DAT_0062c98c)) {
      return (double)SQRT(fVar3 + fVar3 + fVar1 * fVar1 + fVar2 * fVar2);
    }
    CConsole__Printf(&DAT_0066f580,s_Error__Should_not_be_here_in__Di_0062c998);
  }
  return (double)_DAT_005d856c;
}
