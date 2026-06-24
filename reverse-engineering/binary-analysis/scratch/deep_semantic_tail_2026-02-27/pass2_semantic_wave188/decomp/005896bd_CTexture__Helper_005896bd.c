/* address: 0x005896bd */
/* name: CTexture__Helper_005896bd */
/* signature: int __fastcall CTexture__Helper_005896bd(int param_1) */


int __fastcall CTexture__Helper_005896bd(int param_1)

{
  void *pvVar1;
  uint *puVar2;
  undefined4 extraout_EAX;
  int iVar3;
  char *pcVar4;
  bool bVar5;

  CFastVB__ResetConversionStatus((void *)param_1);
  CTexture__TokenList_InitState_0058c129((void *)(param_1 + 4));
  *(undefined4 *)(param_1 + 0x24) = 0;
  *(undefined4 *)(param_1 + 0x28) = 1;
  *(undefined4 *)(param_1 + 0x2c) = 0;
  *(undefined4 *)(param_1 + 0x30) = 0;
  *(undefined4 *)(param_1 + 0x34) = 1;
  *(undefined4 *)(param_1 + 0x38) = 1;
  *(undefined4 *)(param_1 + 0x3c) = 1;
  *(undefined4 *)(param_1 + 0x40) = 0;
  *(undefined4 *)(param_1 + 0x44) = 0;
  *(undefined4 *)(param_1 + 0x48) = 0;
  *(undefined4 *)(param_1 + 0x50) = 0;
  *(undefined4 *)(param_1 + 0x54) = 0;
  *(undefined4 *)(param_1 + 0x4c) = 0;
  *(undefined4 *)(param_1 + 0x80) = 1;
  pvVar1 = (void *)CRT__SetLocale(4,(void *)0x0);
  puVar2 = CRT__StrDup(pvVar1);
  *(uint **)(param_1 + 0x84) = puVar2;
  if (puVar2 != (uint *)0x0) {
    iVar3 = 2;
    bVar5 = true;
    pcVar4 = "C";
    do {
      if (iVar3 == 0) break;
      iVar3 = iVar3 + -1;
      bVar5 = (char)*puVar2 == *pcVar4;
      puVar2 = (uint *)((int)puVar2 + 1);
      pcVar4 = pcVar4 + 1;
    } while (bVar5);
    if (bVar5) goto LAB_0058973d;
  }
  CRT__SetLocale(4,&DAT_005ea324);
LAB_0058973d:
  CRT__ControlFpMasked_0056947e(0,0);
  *(undefined4 *)(param_1 + 0x88) = extraout_EAX;
  CRT__ControlFpMasked_0056947e(0x10000,0x30000);
  return param_1;
}
