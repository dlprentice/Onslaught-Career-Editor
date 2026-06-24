/* address: 0x005b4080 */
/* name: CDXTexture__Unk_005b4080 */
/* signature: void __stdcall CDXTexture__Unk_005b4080(int param_1) */


void CDXTexture__Unk_005b4080(int param_1)

{
  undefined1 *puVar1;
  int *piVar2;
  undefined4 *puVar3;
  undefined4 uVar4;
  char *pcVar5;
  int in_EAX;
  int iVar6;
  undefined4 *puVar7;

  CDXTexture__Unk_005b3fd0();
  if (*(int *)(in_EAX + 0xc) == 0) {
    CDXTexture__Helper_005b3ec0(0x7f);
    puVar1 = *(undefined1 **)(in_EAX + 0x10);
    *puVar1 = 0xff;
    *(undefined1 **)(in_EAX + 0x10) = puVar1 + 1;
    iVar6 = *(int *)(in_EAX + 0x14) + -1;
    *(undefined4 *)(in_EAX + 0x18) = 0;
    *(undefined4 *)(in_EAX + 0x1c) = 0;
    *(int *)(in_EAX + 0x14) = iVar6;
    if (iVar6 == 0) {
      puVar7 = *(undefined4 **)(*(int *)(in_EAX + 0x20) + 0x18);
      iVar6 = (*(code *)puVar7[3])(*(int *)(in_EAX + 0x20));
      if (iVar6 == 0) {
        piVar2 = *(int **)(in_EAX + 0x20);
        puVar3 = (undefined4 *)*piVar2;
        puVar3[5] = 0x18;
        (*(code *)*puVar3)(piVar2);
      }
      uVar4 = puVar7[1];
      *(undefined4 *)(in_EAX + 0x10) = *puVar7;
      *(undefined4 *)(in_EAX + 0x14) = uVar4;
    }
    pcVar5 = *(char **)(in_EAX + 0x10);
    *pcVar5 = (char)param_1 + -0x30;
    *(char **)(in_EAX + 0x10) = pcVar5 + 1;
    piVar2 = (int *)(in_EAX + 0x14);
    *piVar2 = *piVar2 + -1;
    if (*piVar2 == 0) {
      puVar7 = *(undefined4 **)(*(int *)(in_EAX + 0x20) + 0x18);
      iVar6 = (*(code *)puVar7[3])(*(int *)(in_EAX + 0x20));
      if (iVar6 == 0) {
        piVar2 = *(int **)(in_EAX + 0x20);
        puVar3 = (undefined4 *)*piVar2;
        puVar3[5] = 0x18;
        (*(code *)*puVar3)(piVar2);
      }
      uVar4 = puVar7[1];
      *(undefined4 *)(in_EAX + 0x10) = *puVar7;
      *(undefined4 *)(in_EAX + 0x14) = uVar4;
    }
  }
  if (*(int *)(*(int *)(in_EAX + 0x20) + 0x144) == 0) {
    iVar6 = 0;
    if (0 < *(int *)(*(int *)(in_EAX + 0x20) + 0xfc)) {
      puVar7 = (undefined4 *)(in_EAX + 0x24);
      do {
        *puVar7 = 0;
        iVar6 = iVar6 + 1;
        puVar7 = puVar7 + 1;
      } while (iVar6 < *(int *)(*(int *)(in_EAX + 0x20) + 0xfc));
      return;
    }
  }
  else {
    *(undefined4 *)(in_EAX + 0x38) = 0;
    *(undefined4 *)(in_EAX + 0x3c) = 0;
  }
  return;
}
