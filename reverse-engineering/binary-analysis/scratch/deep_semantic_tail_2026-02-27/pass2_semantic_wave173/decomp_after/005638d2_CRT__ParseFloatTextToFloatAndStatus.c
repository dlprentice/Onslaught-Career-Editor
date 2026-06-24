/* address: 0x005638d2 */
/* name: CRT__ParseFloatTextToFloatAndStatus */
/* signature: void __cdecl CRT__ParseFloatTextToFloatAndStatus(void * param_1, int param_2) */


void __cdecl CRT__ParseFloatTextToFloatAndStatus(void *param_1,int param_2)

{
  uint uVar1;
  int extraout_EAX;
  uint uVar2;
  undefined1 local_1c [12];
  undefined4 local_10;
  undefined4 uStack_c;
  int local_8;

  uVar2 = 0;
  uVar1 = CRT__ParseFloatTextToLongDouble();
  if ((uVar1 & 4) == 0) {
    CRT__ConvertLongDoubleToFloat32(local_1c,&local_10);
    if (((uVar1 & 2) != 0) || (extraout_EAX == 1)) {
      uVar2 = 0x80;
    }
    if (((uVar1 & 1) != 0) || (extraout_EAX == 2)) {
      uVar2 = uVar2 | 0x100;
    }
  }
  else {
    uVar2 = 0x200;
    local_10 = 0;
    uStack_c = 0;
  }
  *(uint *)param_1 = uVar2;
  *(ulonglong *)((int)param_1 + 0x10) = CONCAT44(uStack_c,local_10);
  *(int *)((int)param_1 + 4) = local_8 - param_2;
  return;
}
