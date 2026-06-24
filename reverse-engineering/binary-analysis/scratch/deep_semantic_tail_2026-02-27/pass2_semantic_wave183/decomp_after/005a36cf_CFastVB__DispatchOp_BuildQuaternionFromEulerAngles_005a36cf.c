/* address: 0x005a36cf */
/* name: CFastVB__DispatchOp_BuildQuaternionFromEulerAngles_005a36cf */
/* signature: void __stdcall CFastVB__DispatchOp_BuildQuaternionFromEulerAngles_005a36cf(void * param_1, float param_2, float param_3, float param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void CFastVB__DispatchOp_BuildQuaternionFromEulerAngles_005a36cf
               (void *param_1,float param_2,float param_3,float param_4)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float local_30;
  float fStack_2c;
  float fStack_28;
  float fStack_24;
  float local_20;
  float fStack_1c;
  float fStack_18;

  local_30 = param_4 * _DAT_005f4330;
  fStack_2c = param_3 * _UNK_005f4334;
  fStack_28 = param_2 * _UNK_005f4338;
  fStack_24 = DAT_005e6a3c * _UNK_005f433c;
  CFastVB__SinCosVec4Approx(&local_30,&local_30,&local_20);
  fVar1 = (float)((uint)(local_30 * fStack_18 * fStack_2c) ^ _UNK_005f4324);
  fVar2 = (float)((uint)(local_20 * fStack_28 * fStack_2c) ^ _UNK_005f4328);
  fVar3 = (float)((uint)(local_30 * fStack_28 * fStack_2c) ^ _UNK_005f432c);
  *(float *)param_1 =
       local_20 * fStack_18 * fStack_2c +
       (float)((uint)(local_30 * fStack_28 * fStack_1c) ^ _DAT_005f4320);
  *(float *)((int)param_1 + 4) = local_20 * fStack_28 * fStack_1c + fVar1;
  *(float *)((int)param_1 + 8) = local_30 * fStack_18 * fStack_1c + fVar2;
  *(float *)((int)param_1 + 0xc) = local_20 * fStack_18 * fStack_1c + fVar3;
  return;
}
