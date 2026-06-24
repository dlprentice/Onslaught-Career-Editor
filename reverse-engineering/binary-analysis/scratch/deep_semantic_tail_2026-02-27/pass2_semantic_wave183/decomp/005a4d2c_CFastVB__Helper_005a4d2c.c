/* address: 0x005a4d2c */
/* name: CFastVB__Helper_005a4d2c */
/* signature: void __stdcall CFastVB__Helper_005a4d2c(void * param_1, int param_2, uint param_3) */


void CFastVB__Helper_005a4d2c(void *param_1,int param_2,uint param_3)

{
  undefined8 extraout_MM0;
  undefined8 uVar1;
  undefined8 uVar2;
  undefined4 uVar3;
  undefined8 local_18;
  uint local_10;

  FastExitMediaState();
  CFastVB__Helper_005a9a5f(&local_18,(void *)param_2);
  PackedFloatingMUL((ulonglong)param_3,DAT_005ef190);
  CFastVB__FastTrigPairApprox_Scalar();
  uVar3 = (undefined4)((ulonglong)extraout_MM0 >> 0x20);
  uVar2 = CONCAT44(uVar3,uVar3);
  uVar1 = PackedFloatingMUL(local_18,uVar2);
  uVar2 = PackedFloatingMUL((ulonglong)local_10,uVar2);
  *(undefined8 *)param_1 = uVar1;
  *(ulonglong *)((int)param_1 + 8) = CONCAT44((int)extraout_MM0,(int)uVar2);
  FastExitMediaState();
  return;
}
