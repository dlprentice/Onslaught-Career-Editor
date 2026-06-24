/* address: 0x0057437a */
/* name: CFastVB__SelectBestFormatHandler */
/* signature: int __stdcall CFastVB__SelectBestFormatHandler(void * param_1, uint param_2, int param_3, void * param_4) */


int CFastVB__SelectBestFormatHandler(void *param_1,uint param_2,int param_3,void *param_4)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  int *piVar4;
  int *piVar5;
  int *piVar6;
  undefined4 local_158;
  undefined4 local_154;
  undefined1 local_28 [12];
  undefined4 local_1c;
  undefined1 local_18 [12];
  byte local_c;
  int *local_8;

  local_8 = (int *)0x0;
  CFastVB__Helper_00579bd5(1);
  if (param_1 != (void *)0x0) {
    (**(code **)(*(int *)param_1 + 0x18))(param_1,&local_8);
    (**(code **)(*(int *)param_1 + 0x1c))(param_1,&local_158);
    (**(code **)(*(int *)param_1 + 0x20))(param_1,0,local_28);
    if (((param_2 & 0x100000) != 0) &&
       ((**(code **)(*(int *)param_1 + 0x24))(param_1,local_18), (local_c & 0x20) != 0)) {
      param_2 = param_2 | 0x10;
    }
  }
  uVar3 = 0xffffffff;
  piVar4 = &DAT_005e6a68;
  piVar6 = &DAT_005e6a40;
  piVar5 = &DAT_005e6a40;
  if (&DAT_005e6a68 < PTR_DAT_00656f28) {
    do {
      piVar6 = piVar5;
      if ((*piVar4 != 0) &&
         ((local_8 == (int *)0x0 ||
          (iVar1 = (**(code **)(*local_8 + 0x28))
                             (local_8,local_154,local_158,local_1c,param_2,param_3,*piVar4),
          -1 < iVar1)))) {
        piVar6 = piVar4;
        if (*(int *)param_4 == *piVar4) break;
        piVar6 = piVar5;
        if ((((piVar4[8] != 0) &&
             (uVar2 = CFastVB__ComputeFormatMatchPenalty((int)param_4,(int)piVar4),
             uVar2 != 0xffffffff)) && (uVar2 <= uVar3)) &&
           ((uVar2 != uVar3 || ((uint)piVar4[2] < (uint)piVar5[2])))) {
          uVar3 = uVar2;
          piVar6 = piVar4;
        }
      }
      piVar4 = piVar4 + 9;
      piVar5 = piVar6;
    } while (piVar4 < PTR_DAT_00656f28);
  }
  if (local_8 != (int *)0x0) {
    (**(code **)(*local_8 + 8))(local_8);
    local_8 = (int *)0x0;
  }
  CFastVB__Helper_00579bd5(0);
  return *piVar6;
}
