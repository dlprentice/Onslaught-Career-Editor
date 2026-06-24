/* address: 0x005aa73b */
/* name: CFastVB__Helper_005aa73b */
/* signature: int __stdcall CFastVB__Helper_005aa73b(void * param_1, void * param_2, void * param_3) */


int CFastVB__Helper_005aa73b(void *param_1,void *param_2,void *param_3)

{
  undefined4 uVar1;
  undefined8 uVar2;
  undefined8 uVar3;
  undefined8 uVar4;
  undefined8 uVar5;
  undefined8 uVar6;

  FastExitMediaState();
  uVar1 = (undefined4)*(undefined8 *)param_2;
  uVar3 = CONCAT44(uVar1,uVar1);
  uVar1 = (undefined4)((ulonglong)*(undefined8 *)param_2 >> 0x20);
  uVar6 = CONCAT44(uVar1,uVar1);
  uVar2 = PackedFloatingMUL(uVar3,*(undefined8 *)param_3);
  uVar4 = PackedFloatingMUL(uVar6,*(undefined8 *)((int)param_3 + 0x10));
  uVar2 = PackedFloatingADD(uVar2,*(undefined8 *)((int)param_3 + 0x30));
  uVar5 = PackedFloatingMUL(uVar3,*(undefined8 *)((int)param_3 + 8));
  uVar6 = PackedFloatingMUL(uVar6,*(undefined8 *)((int)param_3 + 0x18));
  uVar3 = PackedFloatingADD(uVar2,uVar4);
  uVar2 = PackedFloatingADD(uVar5,*(undefined8 *)((int)param_3 + 0x38));
  uVar2 = PackedFloatingADD(uVar2,uVar6);
  *(undefined8 *)param_1 = uVar3;
  *(undefined8 *)((int)param_1 + 8) = uVar2;
  FastExitMediaState();
  return (int)param_1;
}
