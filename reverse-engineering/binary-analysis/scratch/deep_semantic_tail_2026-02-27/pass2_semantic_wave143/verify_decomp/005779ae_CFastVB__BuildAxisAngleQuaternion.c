/* address: 0x005779ae */
/* name: CFastVB__BuildAxisAngleQuaternion */
/* signature: float * __stdcall CFastVB__BuildAxisAngleQuaternion(void * param_1, int param_2, float param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

float * CFastVB__BuildAxisAngleQuaternion(void *param_1,int param_2,float param_3)

{
  float fVar1;
  float10 fVar2;
  float10 fVar3;
  undefined4 local_18;
  undefined4 local_14;
  undefined4 local_10;

  CTexture__Helper_00575d99();
  fVar2 = (float10)fcos((float10)(param_3 * _DAT_005e72d4));
  fVar3 = (float10)fsin((float10)(param_3 * _DAT_005e72d4));
  *(float *)((int)param_1 + 0xc) = (float)fVar2;
  fVar1 = (float)fVar3;
  *(float *)param_1 = local_18 * fVar1;
  *(float *)((int)param_1 + 4) = local_14 * fVar1;
  *(float *)((int)param_1 + 8) = local_10 * fVar1;
  return param_1;
}
